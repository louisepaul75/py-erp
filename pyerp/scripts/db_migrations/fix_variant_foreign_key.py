#!/usr/bin/env python
"""
Script to add the missing foreign key constraint to the variant table.
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


def fix_variant_foreign_key():
    """Add the missing foreign key constraint to the variant table."""
    setup_django()
    print("Adding missing foreign key constraint to variant table...")

    with connection.cursor() as cursor:
        # Check if the constraint already exists using a different query
        cursor.execute(
            """  # noqa: E128
            SELECT COUNT(*) FROM pg_constraint
            WHERE conrelid = 'products_variantproduct'::regclass
            AND contype = 'f'
            AND conkey @> ARRAY[
                (SELECT attnum FROM pg_attribute  # noqa: E128
                 WHERE attrelid = 'products_variantproduct'::regclass
                 AND attname = 'parent_id')
            ]::smallint[];
            """
        )
        constraint_count = cursor.fetchone()[0]

        if constraint_count > 0:
            print(f"Found {constraint_count} foreign key constraint(s) for parent_id.")  # noqa: E501
            return True

        # Add the foreign key constraint
        try:
            # First, check if there are any orphaned records
            cursor.execute(
                """  # noqa: E128
                SELECT COUNT(*) FROM products_variantproduct v
                LEFT JOIN products_parentproduct p ON v.parent_id = p.id
                WHERE v.parent_id IS NOT NULL AND p.id IS NULL;
                """
            )
            orphaned_count = cursor.fetchone()[0]

            if orphaned_count > 0:
                print(f"WARNING: Found {orphaned_count} orphaned records. Setting parent_id to NULL for these records.")  # noqa: E501
                cursor.execute(
                    """  # noqa: E128
                    UPDATE products_variantproduct v
                    SET parent_id = NULL
                    WHERE parent_id IS NOT NULL AND NOT EXISTS (
                        SELECT 1 FROM products_parentproduct p WHERE v.parent_id = p.id  # noqa: E501
                    );
                    """
                )

            # Now add the constraint
            cursor.execute(
                """  # noqa: E128
                ALTER TABLE products_variantproduct
                ADD CONSTRAINT products_variantproduct_parent_id_fk
                FOREIGN KEY (parent_id) REFERENCES products_parentproduct(id)
                ON DELETE CASCADE;
                """
            )
            print("Foreign key constraint added successfully.")

            # Verify using the same query as above
            cursor.execute(
                """  # noqa: E128
                SELECT COUNT(*) FROM pg_constraint
                WHERE conrelid = 'products_variantproduct'::regclass
  # noqa: F841
                AND contype = 'f'
  # noqa: F841
                AND conkey @> ARRAY[
                    (SELECT attnum FROM pg_attribute  # noqa: E128
                     WHERE attrelid = 'products_variantproduct'::regclass
  # noqa: F841
                     AND attname = 'parent_id')
  # noqa: F841
                ]::smallint[];
                """
            )
            constraint_count = cursor.fetchone()[0]

            if constraint_count > 0:
                print(f"Verification successful: Found {constraint_count} foreign key constraint(s) for parent_id.")  # noqa: E501
                return True
            else:
                print("ERROR: Foreign key constraint still not found after adding!")  # noqa: E501
                return False

        except Exception as e:
            print(f"ERROR: Failed to add foreign key constraint: {e}")
            return False


def main():

    """Main entry point for the script."""
    success = fix_variant_foreign_key()
    return 0 if success else 1

if __name__ == "__main__":
  # noqa: F841
    sys.exit(main())
