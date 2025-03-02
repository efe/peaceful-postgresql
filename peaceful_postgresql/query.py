import sqlparse
import re
from typing import Dict, List

from peaceful_postgresql.constants import StatementType, LockType, LockModeKeyword


def detect_locks(sql_query: str) -> Dict[str, str]:
    """
    Analyze SQL queries to detect PostgreSQL locks that would be acquired.
    Only detects ACCESS EXCLUSIVE and SHARE locks.

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
            # Check for additional statement types that acquire ACCESS EXCLUSIVE locks
            for exclusive_stmt in ['VACUUM FULL', 'CLUSTER', 'REINDEX']:
                if stmt.strip().upper().startswith(exclusive_stmt):
                    table_match = re.search(
                        r'(?i)' + exclusive_stmt + r'\s+("?[a-zA-Z_0-9]+"?)',
                        stmt
                    )
                    if table_match:
                        table_name = table_match.group(1).strip('"')
                        locks[table_name] = LockType.ACCESS_EXCLUSIVE.value
                    break
            continue

        # Handle different statement types
        if statement_type == StatementType.SELECT:
            # Only track SHARE locks for SELECT
            table_names = extract_table_names(parsed)
            for table in table_names:
                locks[table] = LockType.SHARE.value

        elif statement_type in {StatementType.INSERT, StatementType.UPDATE, StatementType.DELETE}:
            # These statements typically acquire RowExclusiveLock
            table_names = extract_table_names(parsed)
            for table in table_names:
                locks[table] = LockType.ROW_EXCLUSIVE.value

        elif statement_type in {StatementType.CREATE, StatementType.ALTER,
                                StatementType.DROP, StatementType.TRUNCATE}:
            # These statements acquire AccessExclusiveLock
            # Enhanced regex to catch more object types and their names
            table_match = re.search(
                r'(?i)(TABLE|INDEX|SEQUENCE|VIEW|MATERIALIZED\s+VIEW)\s+'
                r'(IF EXISTS\s+)?(["\w\s.]+?)(?:\s|$)',
                stmt
            )
            
            # Special handling for ALTER statements
            if statement_type == StatementType.ALTER:
                # Handle all ALTER TABLE/INDEX operations that require ACCESS EXCLUSIVE lock
                alter_match = re.search(
                    r'(?i)ALTER\s+(TABLE|INDEX)\s+(["\w\s.]+?)\s+'
                    r'(SET|DROP|RENAME|ADD|ALTER|ATTACH|DETACH|INHERIT|ENABLE|DISABLE)',
                    stmt
                )
                if alter_match:
                    table_name = alter_match.group(2).strip('"')
                    locks[table_name] = LockType.ACCESS_EXCLUSIVE.value
            
            elif table_match:
                table_name = table_match.group(3).strip('"')
                locks[table_name] = LockType.ACCESS_EXCLUSIVE.value

        elif statement_type == StatementType.LOCK:
            # Only handle explicit SHARE or ACCESS EXCLUSIVE locks
            table_match = re.search(
                r'(?i)LOCK\s+TABLE\s+("?[a-zA-Z_0-9]+"?)(?:\s+IN\s+(.+)\s+MODE)?',
                stmt
            )
            if table_match:
                table_name = table_match.group(1).strip('"')
                lock_mode = table_match.group(2).upper() if table_match.group(2) else "ACCESS EXCLUSIVE"

                if LockModeKeyword.SHARE.value in lock_mode and LockModeKeyword.UPDATE.value not in lock_mode:
                    locks[table_name] = LockType.SHARE.value
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
