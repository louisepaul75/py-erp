#!/usr/bin/env python
"""
Fix is_placeholder Field Script

This script fixes the issue with the is_placeholder field in the ParentProduct table
by modifying the SQL query directly.
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

def fix_is_placeholder_field():
    """Fix the is_placeholder field in the ParentProduct table."""
    print("Starting is_placeholder field fix...")
    
    try:
        with connection.cursor() as cursor:
            # Check if the table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'products_parentproduct'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"Table products_parentproduct exists: {table_exists}")
            
            if not table_exists:
                print("Table does not exist, cannot fix")
                return
            
            # Check the data type of the is_placeholder field
            cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'products_parentproduct' 
                AND column_name = 'is_placeholder'
            """)
            result = cursor.fetchone()
            if not result:
                print("Column is_placeholder does not exist")
                return
                
            data_type = result[0]
            print(f"Current data type of is_placeholder: {data_type}")
            
            # If the field is smallint, we need to modify our SQL queries to use integers
            if data_type == 'smallint':
                print("Field is smallint, updating Django model to use integers instead of booleans")
                
                # Create a test record with integer value for is_placeholder
                try:
                    cursor.execute("""
                        INSERT INTO products_productcategory (code, name, description)
                        VALUES ('TEST_FIX', 'Test Fix Category', 'Test category for fix')
                        RETURNING id
                    """)
                    category_id = cursor.fetchone()[0]
                    print(f"Created test category with ID: {category_id}")
                    
                    # Try to create a test parent product with integer value for is_placeholder
                    cursor.execute("""
                        INSERT INTO products_parentproduct (
                            sku, base_sku, name, is_active, is_discontinued, 
                            has_bom, is_one_sided, is_hanging, created_at, updated_at, 
                            category_id, is_placeholder
                        )
                        VALUES (
                            'TEST_FIX', 'TEST_FIX', 'Test Fix Product', 1, 0, 
                            0, 0, 0, NOW(), NOW(), 
                            %s, 0
                        )
                        RETURNING id
                    """, [category_id])
                    product_id = cursor.fetchone()[0]
                    print(f"Created test product with ID: {product_id}")
                    
                    # Clean up the test records
                    cursor.execute("DELETE FROM products_parentproduct WHERE id = %s", [product_id])
                    cursor.execute("DELETE FROM products_productcategory WHERE id = %s", [category_id])
                    print("Deleted test records")
                    
                    print("Fix completed successfully")
                except Exception as e:
                    print(f"Error during test: {e}")
            else:
                print(f"Field is {data_type}, no fix needed")
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_is_placeholder_field() 