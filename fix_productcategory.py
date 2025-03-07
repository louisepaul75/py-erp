#!/usr/bin/env python
"""
Fix ProductCategory Database Script

This script fixes the issue with the ProductCategory table where the id column
has a null value, violating the not-null constraint.
"""

import os
import sys
import logging
from pathlib import Path

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")

# Initialize Django
import django
django.setup()

# Import Django models after setting up the environment
from django.db import connection
from pyerp.products.models import ProductCategory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

def fix_productcategory_table():
    """
    Fix the ProductCategory table by:
    1. Checking for any records with null id
    2. Resetting the auto-increment sequence if needed
    """
    logger.info("Starting ProductCategory table fix")
    
    # Check if there are any ProductCategory records
    count = ProductCategory.objects.count()
    logger.info(f"Found {count} ProductCategory records")
    
    # Get the database engine being used
    db_engine = connection.vendor
    logger.info(f"Database engine: {db_engine}")
    
    if db_engine == 'postgresql':
        # For PostgreSQL, reset the sequence
        with connection.cursor() as cursor:
            # Check if there are any records with null id
            cursor.execute("SELECT COUNT(*) FROM products_productcategory WHERE id IS NULL")
            null_count = cursor.fetchone()[0]
            logger.info(f"Found {null_count} records with NULL id")
            
            if null_count > 0:
                # Delete records with null id
                cursor.execute("DELETE FROM products_productcategory WHERE id IS NULL")
                logger.info(f"Deleted {null_count} records with NULL id")
            
            # Reset the sequence
            cursor.execute("""
                SELECT setval(
                    pg_get_serial_sequence('products_productcategory', 'id'),
                    COALESCE((SELECT MAX(id) FROM products_productcategory), 0) + 1,
                    false
                )
            """)
            logger.info("Reset the auto-increment sequence for products_productcategory")
    
    elif db_engine == 'sqlite3':
        # For SQLite, we need a different approach
        with connection.cursor() as cursor:
            # Check if there are any records with null id
            cursor.execute("SELECT COUNT(*) FROM products_productcategory WHERE id IS NULL")
            null_count = cursor.fetchone()[0]
            logger.info(f"Found {null_count} records with NULL id")
            
            if null_count > 0:
                # Delete records with null id
                cursor.execute("DELETE FROM products_productcategory WHERE id IS NULL")
                logger.info(f"Deleted {null_count} records with NULL id")
    
    else:
        logger.warning(f"Unsupported database engine: {db_engine}")
        logger.warning("Manual intervention may be required")
    
    # Try to create a test category to verify the fix
    try:
        test_category = ProductCategory.objects.create(
            code="TEST_FIX",
            name="Test Fix Category",
            description="Category created to test the database fix"
        )
        logger.info(f"Successfully created test category with id: {test_category.id}")
        
        # Clean up the test category
        test_category.delete()
        logger.info("Deleted test category")
        
        logger.info("ProductCategory table fix completed successfully")
    except Exception as e:
        logger.error(f"Failed to create test category: {e}")
        logger.error("Fix may not have been successful")

if __name__ == "__main__":
    fix_productcategory_table() 