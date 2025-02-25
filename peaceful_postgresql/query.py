import sqlparse
import re
from typing import Dict, List

from peaceful_postgresql.constants import StatementType, LockType, LockModeKeyword


def detect_locks(sql_query: str) -> Dict[str, str]:
    """
    Analyze SQL queries to detect PostgreSQL locks that would be acquired.

    Args:
        sql_query: String containing one or more SQL statements

    Returns:
        Dictionary mapping table names to PostgreSQL lock types
    """
    locks = {}
    statements = sqlparse.split(sql_query)

    for stmt in statements:
        parsed = sqlparse.parse(stmt)[0]

        # Skip empty statements
        if not parsed.tokens:
            continue

        # Extract the first meaningful token to determine statement type
        statement_type = None
        for token in parsed.tokens:
            if token.ttype is not None and token.ttype in sqlparse.tokens.Keyword:
                try:
                    statement_type = StatementType(token.value.upper())
                except ValueError:
                    # Not a statement type we're tracking
                    pass
                break

        if not statement_type:
            continue

        # Handle different statement types
        if statement_type == StatementType.SELECT:
            # SELECT generally acquires RowShareLock (unless FOR UPDATE/SHARE is specified)
            table_names = extract_table_names(parsed)
            for table in table_names:
                # Check for FOR UPDATE/SHARE clause
                if re.search(r'(?i)FOR\s+(UPDATE|SHARE)', stmt):
                    locks[table] = LockType.ROW_EXCLUSIVE.value
                else:
                    locks[table] = LockType.ROW_SHARE.value

        elif statement_type in {StatementType.INSERT, StatementType.UPDATE, StatementType.DELETE}:
            # These statements typically acquire RowExclusiveLock
            table_names = extract_table_names(parsed)
            for table in table_names:
                locks[table] = LockType.ROW_EXCLUSIVE.value

        elif statement_type in {StatementType.CREATE, StatementType.ALTER,
                                StatementType.DROP, StatementType.TRUNCATE}:
            # These statements typically acquire AccessExclusiveLock
            table_match = re.search(
                r'(?i)(TABLE|INDEX|SEQUENCE|VIEW)\s+(IF EXISTS\s+)?("?[a-zA-Z_0-9]+"?)',
                stmt
            )
            if table_match:
                table_name = table_match.group(3).strip('"')
                locks[table_name] = LockType.ACCESS_EXCLUSIVE.value

        elif statement_type == StatementType.LOCK:
            # Explicit LOCK statement
            table_match = re.search(
                r'(?i)LOCK\s+TABLE\s+("?[a-zA-Z_0-9]+"?)(?:\s+IN\s+(.+)\s+MODE)?',
                stmt
            )
            if table_match:
                table_name = table_match.group(1).strip('"')
                lock_mode = table_match.group(2).upper() if table_match.group(2) else "ACCESS EXCLUSIVE"

                # Map lock mode to PostgreSQL lock type
                if LockModeKeyword.SHARE.value in lock_mode and LockModeKeyword.UPDATE.value in lock_mode:
                    locks[table_name] = LockType.SHARE_UPDATE_EXCLUSIVE.value
                elif LockModeKeyword.SHARE.value in lock_mode and LockModeKeyword.ROW.value in lock_mode:
                    locks[table_name] = LockType.ROW_SHARE.value
                elif LockModeKeyword.SHARE.value in lock_mode:
                    locks[table_name] = LockType.SHARE.value
                elif f"{LockModeKeyword.ROW.value} {LockModeKeyword.EXCLUSIVE.value}" in lock_mode:
                    locks[table_name] = LockType.ROW_EXCLUSIVE.value
                elif LockModeKeyword.EXCLUSIVE.value in lock_mode:
                    locks[table_name] = LockType.ACCESS_EXCLUSIVE.value

    return locks


def extract_table_names(parsed_stmt) -> List[str]:
    """Extract table names from a parsed SQL statement."""
    tables = []

    # Find all table references
    for token in parsed_stmt.flatten():
        if isinstance(token, sqlparse.sql.Identifier):
            # Simple identifier
            tables.append(token.get_real_name())
        elif isinstance(token, sqlparse.sql.IdentifierList):
            # List of identifiers (like in FROM clause with multiple tables)
            for identifier in token.get_identifiers():
                tables.append(identifier.get_real_name())

    # Remove empty entries
    return [table for table in tables if table]
