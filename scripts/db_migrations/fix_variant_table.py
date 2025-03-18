"""
Script to fix the variant product table issues.
"""

from django.db import connection


def check_table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as _:
        tables = connection.introspection.table_names()
        return table_name in tables
