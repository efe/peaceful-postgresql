from django.db.migrations.recorder import MigrationRecorder
from django.apps import apps

def get_unapplied_migrations():
    # Get all applied migrations
    applied_migrations = set(migration.name for migration in MigrationRecorder.objects.all())

    # Get all existing migrations
    all_migrations = set(
        migration for app in apps.get_app_configs() for migration in app.migrations
    )

    # Find unapplied migrations
    unapplied_migrations = all_migrations - applied_migrations
    return unapplied_migrations


def get_sql_statements_of_migration(app_label, migration_name):
    sql_statements = sqlmigrate(app_label, migration_name)
    return sql_statements
