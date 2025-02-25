from enum import Enum


class LockType(Enum):
    """PostgreSQL lock types."""
    ACCESS_EXCLUSIVE = "AccessExclusiveLock"
    ROW_EXCLUSIVE = "RowExclusiveLock"
    ROW_SHARE = "RowShareLock"
    SHARE = "ShareLock"
    SHARE_UPDATE_EXCLUSIVE = "ShareUpdateExclusiveLock"


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