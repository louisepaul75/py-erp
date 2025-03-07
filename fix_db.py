#!/usr/bin/env python
"""
Fix Database Script

This script fixes the issue with the ProductCategory table where the id column
has a null value, violating the not-null constraint.
"""

import os
import sys
import django
from pathlib import Path

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

from django.db import connection

# Print debug information
print("Script started")
print(f"Django version: {django.get_version()}")
print(f"Database engine: {connection.vendor}")

def fix_database():
    """Fix the database issue with ProductCategory."""
    print("Starting database fix...")
    
    try:
        with connection.cursor() as cursor:
            # Delete any records with null id
            cursor.execute("DELETE FROM products_productcategory WHERE id IS NULL")
            print("Deleted records with NULL id")
            
            # Reset the sequence
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('products_productcategory', 'id'),
                    COALESCE((SELECT MAX(id) FROM products_productcategory), 1),
                    true
                )
            """)
            print("Reset the sequence for products_productcategory")
            
            # Verify the fix
            cursor.execute("SELECT COUNT(*) FROM products_productcategory")
            count = cursor.fetchone()[0]
            print(f"Total ProductCategory records: {count}")
            
            # Get the next sequence value
            cursor.execute("SELECT nextval(pg_get_serial_sequence('products_productcategory', 'id'))")
            next_id = cursor.fetchone()[0]
            print(f"Next ID that will be used: {next_id}")
        
        print("Database fix completed successfully")
    except Exception as e:
        print(f"Error fixing database: {e}")

# Run the function immediately
fix_database() 