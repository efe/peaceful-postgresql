from enum import Enum


class LockType(Enum):
    """PostgreSQL lock types."""
    ACCESS_EXCLUSIVE = "AccessExclusiveLock"
    SHARE = "ShareLock"


class StatementType(Enum):
    """SQL statement types."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    ALTER = "ALTER"
    DROP = "DROP"
    TRUNCATE = "TRUNCATE"
    LOCK = "LOCK"
    VACUUM = "VACUUM"
    CLUSTER = "CLUSTER"
    REINDEX = "REINDEX"


class ObjectType(Enum):
    """SQL object types."""
    TABLE = "TABLE"
    INDEX = "INDEX"
    SEQUENCE = "SEQUENCE"
    VIEW = "VIEW"


class LockModeKeyword(Enum):
    """Keywords used in lock mode specifications."""
    SHARE = "SHARE"
    UPDATE = "UPDATE"
    ROW = "ROW"
    EXCLUSIVE = "EXCLUSIVE"