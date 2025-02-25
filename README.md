# peaceful-postgresql

A tool that prevents downtime during PostgreSQL schema modifications.

## How does it work?

1- Parses an SQL query and guesses `AccessExclusiveLock` and `ShareLock` locks. Then, returns the table names.
2- Then, checks the table size of these tables.
3- If the size of table above certain limit, it means that we'll have a downtime.