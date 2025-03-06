"""
Script to fix migration issues in the pyERP system.
"""

import os
import sys

import django
from django.db import connection


def setup_django():
    """Set up Django environment if not already set up."""
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
        django.setup()


def fix_migrations():
    """Fix migration issues in the pyERP system."""
    setup_django()
    print("Starting migration fix process...")

    # Execute SQL to fix the django_migrations table
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'monitoring_healthcheckresult')",
        )
        table_exists = cursor.fetchone()[0]

        print(f"Table monitoring_healthcheckresult exists: {table_exists}")

        # Check migration record
        cursor.execute("SELECT * FROM django_migrations WHERE app = 'monitoring'")
        migrations = cursor.fetchall()
        print(f"Existing migrations for monitoring app: {migrations}")

        if table_exists and not migrations:
            print(
                "Table exists but migration record is missing. Adding the migration record...",
            )
            cursor.execute("SELECT pg_get_serial_sequence('django_migrations', 'id')")
            sequence_name = cursor.fetchone()[0]

            if sequence_name:
                print(f"Sequence name: {sequence_name}")
                cursor.execute(f"SELECT nextval('{sequence_name}')")
                next_id = cursor.fetchone()[0]
                print(f"Next ID: {next_id}")

                # Insert the migration record
                cursor.execute(
                    "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, NOW())",  # noqa: E501
                    [next_id, "monitoring", "0001_initial"],
                )
                print("Migration record added successfully!")
            else:
                print("Sequence not found. Trying a different approach...")
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM django_migrations")
                next_id = cursor.fetchone()[0]
                print(f"Next ID based on MAX: {next_id}")

                # Insert the migration record
                cursor.execute(
                    "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, NOW())",  # noqa: E501
                    [next_id, "monitoring", "0001_initial"],
                )
                print("Migration record added successfully using MAX(id) approach!")

    print("Migration fix completed successfully.")
    return True


def main():
    """Main entry point for the script."""
    success = fix_migrations()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
