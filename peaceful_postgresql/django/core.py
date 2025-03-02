from django.db.migrations.recorder import MigrationRecorder
from django.apps import apps

# Get all applied migrations
applied_migrations = set(migration.name for migration in MigrationRecorder.objects.all())

# Get all existing migrations
all_migrations = set(
    migration for app in apps.get_app_configs() for migration in app.migrations
)

# Find unapplied migrations
unapplied_migrations = all_migrations - applied_migrations
print(unapplied_migrations)

sql_statements = sqlmigrate(app_label, migration_name)
