import psycopg2
from peaceful_postgresql.settings import DATABASE_CONFIG, TABLE_SIZE_THRESHOLD


def get_connection():
    return psycopg2.connect(
        dbname=DATABASE_CONFIG["dbname"],
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"]
    )


def get_table_sizes(table_names):
    sizes = {}
    with get_connection() as conn:
        with conn.cursor() as cursor:
            for table in table_names:
                cursor.execute(
                    """
                    SELECT pg_total_relation_size(%s);
                    """, (table,)
                )
                size = cursor.fetchone()[0]
                sizes[table] = size
    return sizes


def is_downtime_going_to_happen(table_names):
    sizes = get_table_sizes(table_names)
    for table, size in sizes.items():
        if size > TABLE_SIZE_THRESHOLD:
            return True
    return False
