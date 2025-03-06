"""
Script to check the variant table structure.
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


def check_variant_table():
    """Check the variant table structure."""
    setup_django()
    print("Checking variant table structure...")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = %s)",  # noqa: E501
            ['products_variantproduct']
        )
        exists = cursor.fetchone()[0]

        if not exists:
            print("ERROR: Variant table does not exist!")
            return False

 # Get the table columns
        cursor.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position",  # noqa: E501
            ['products_variantproduct']
        )
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]

        print(f"Variant table has {len(column_names)} columns:")
        for col in column_names:
            print(f"  - {col}")

 # Check for required fields
        required_fields = ['id', 'sku', 'name', 'parent_id', 'variant_code', 'base_sku']  # noqa: E501
        missing_fields = [field for field in required_fields if field not in column_names]  # noqa: E501

        if missing_fields:
            print(f"WARNING: Missing required fields: {', '.join(missing_fields)}")  # noqa: E501
            return False
        else:
            print("All required fields are present in the variant table.")

 # Check for foreign key constraint
        cursor.execute(
            """  # noqa: E128
            SELECT EXISTS(
            SELECT 1 FROM information_schema.table_constraints tc  # noqa: E128
            JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name  # noqa: E501
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = 'products_variantproduct'
            AND ccu.column_name = 'parent_id'
        )
            """
        )
        has_fk = cursor.fetchone()[0]

        if has_fk:
            print("Foreign key constraint for parent_id is properly set up.")
        else:
            print("WARNING: Foreign key constraint for parent_id is missing!")

    print("Variant table check completed.")
    return True


def main():

    """Main entry point for the script."""
    success = check_variant_table()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
