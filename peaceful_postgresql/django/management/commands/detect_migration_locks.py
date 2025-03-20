from django.core.management.base import BaseCommand
from peaceful_postgresql.django.core import get_sql_statements_of_migration, get_unapplied_migrations
from peaceful_postgresql.query import detect_locks

class Command(BaseCommand):
    help = 'Detects potential locks that could occur during a migration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app_label', type=str, help='The app label of the migration', nargs='?', default=None
        )
        parser.add_argument(
            '--migration_name', type=str, help='The name of the migration', nargs='?', default=None
        )

    def handle(self, *args, **options):
        app_label = options.get('app_label')
        migration_name = options.get('migration_name')

        if app_label and migration_name:
            migrations = [(app_label, migration_name)]
        else:
            migrations = get_unapplied_migrations()

        for migration in migrations:
            # Get SQL statements for the migration
            sql_statements = get_sql_statements_of_migration(app_label, migration_name)

            # Detect locks for each SQL statement
            for sql in sql_statements.split(';'):
                sql = sql.strip()

                if not sql:
                    # Skip empty statements
                    continue

                locks = detect_locks(sql)
                if locks:
                    self.stdout.write(f"\nAnalyzing SQL: {sql}")
                    self.stdout.write(self.style.WARNING("Potential locks detected:"))
                    for lock in locks:
                        self.stdout.write(f"- {lock}")
                else:
                    self.stdout.write(self.style.SUCCESS(f"No locks detected for: {sql}"))
