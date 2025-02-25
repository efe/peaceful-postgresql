# peaceful-postgresql
A tool for detecting potential downtime during PostgreSQL schema modifications.

## How It Works

1)Parses an SQL query to identify `AccessExclusiveLock` and `ShareLock` locks, which block concurrent queries on the affected table.

2) Retrieves the size of the locked tables.

3) If a table exceeds a certain size threshold, downtime is likely.

## Roadmap

- Add native support for Django and Alembic.
- Enhance the query parser with improved accuracy and comprehensive test coverage.
- Expand downtime estimation by considering cache, dead tuples, and other factors beyond table size.
