#!/usr/bin/env python
"""
Script to fix variant table migration issues and apply all pending migrations.
"""
import os
import sys
import django
from django.db import connection
from django.core.management import call_command

def setup_django():
    """Set up Django environment if not already set up."""
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
        django.setup()

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names()
        return table_name in tables

def fix_variant_table():
    """Fix the variant table migration issues."""
    setup_django()
    print("Starting variant table fix process...")
    
    # Check if the variant table exists
    if check_table_exists('products_variantproduct'):
        print("Variant table already exists in the database.")
    else:
        print("Variant table does not exist. Will be created during migration.")
    
    # Apply all pending migrations
    print("Applying all pending migrations...")
    call_command('migrate', 'products')
    
    # Verify the table exists after migrations
    if check_table_exists('products_variantproduct'):
        print("Variant table successfully created/updated.")
    else:
        print("ERROR: Variant table still does not exist after migrations!")
        return False
    
    # Check the structure of the variant table
    with connection.cursor() as cursor:
        try:
            cursor.execute("DESCRIBE products_variantproduct")
        except Exception:
            # PostgreSQL uses different syntax
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'products_variantproduct'
            """)
            
        columns = cursor.fetchall()
        print(f"Variant table has {len(columns)} columns.")
        
        # Check for key fields
        required_fields = ['id', 'sku', 'name', 'parent_id', 'variant_code', 'base_sku']
        found_fields = [col[0] for col in columns]
        
        missing_fields = [field for field in required_fields if field not in found_fields]
        if missing_fields:
            print(f"WARNING: Missing required fields: {', '.join(missing_fields)}")
            return False
        else:
            print("All required fields are present in the variant table.")
    
    print("Variant table fix completed successfully.")
    return True

def main():
    """Main entry point for the script."""
    success = fix_variant_table()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 