import sqlparse
import re

def detect_locks(sql_query: str):
    locks = {}
    statements = sqlparse.split(sql_query)
    for stmt in statements:
        parsed = sqlparse.parse(stmt)
        for token in parsed[0].tokens:
            if token.ttype is None and token.value.upper() in {"CREATE", "ALTER", "DROP"}:
                table_match = re.search(r'(?i)(TABLE|INDEX|SEQUENCE)\s+(IF EXISTS\s+)?("?[a-zA-Z_0-9]+"?)', stmt)
                if table_match:
                    table_name = table_match.group(3).strip('"')
                    if "DROP" in token.value.upper() or "ALTER" in token.value.upper():
                        locks[table_name] = "AccessExclusiveLock"
                    elif "CREATE" in token.value.upper():
                        locks[table_name] = "ShareLock"
    return locks
