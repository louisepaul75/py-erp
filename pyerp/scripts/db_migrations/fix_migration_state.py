#!/usr/bin/env python
"""
Script to fix the migration state by marking pending migrations as applied.
"""
import os
import sys
import django
from django.db import connection

def setup_django():
    """Set up Django environment if not already set up."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
        django.setup()

def fix_migration_state():
    """Fix the migration state by marking pending migrations as applied."""
    setup_django()
    print("Starting migration state fix process...")
    
    # List of migrations to mark as applied
    migrations_to_apply = [
        ('products', '0013_create_variantproduct_table'),
        ('products', '0014_create_productimage_table'),
        ('products', '0015_merge_20250303_0050'),
        ('products', '0016_fix_variant_table'),
    ]
    
    # Mark migrations as applied
    with connection.cursor() as cursor:
        # Get the next ID value
        cursor.execute("SELECT MAX(id) FROM django_migrations")
        max_id = cursor.fetchone()[0] or 0
        next_id = max_id + 1
        
        for app, migration in migrations_to_apply:
            # Check if migration is already applied
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM django_migrations WHERE app = %s AND name = %s)",
                [app, migration]
            )
            exists = cursor.fetchone()[0]
            
            if exists:
                print(f"Migration {app}.{migration} is already applied.")
            else:
                # Insert the migration record with an ID
                cursor.execute(
                    "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, NOW())",
                    [next_id, app, migration]
                )
                print(f"Marked migration {app}.{migration} as applied with ID {next_id}.")
                next_id += 1
    
    print("Migration state fix completed successfully.")
    return True

def main():
    """Main entry point for the script."""
    success = fix_migration_state()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 