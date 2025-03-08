from typing import Any

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Field


class Command(BaseCommand):
    """Command to check the structure of the ImageSyncLog model and table."""

    help = "Check ImageSyncLog table structure and data"

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle command execution."""
        self.stdout.write("=" * 79)

        # Get model fields using model's _meta API
        model = apps.get_model("products", "ImageSyncLog")
        fields = model._meta.get_fields()

        for field in fields:
            if isinstance(field, Field):
                field_type = field.get_internal_type()
                field_info = (
                    f"{field.name} ({field_type})"
                    f"{' (Primary Key)' if field.primary_key else ''}"
                    f"{' (Null)' if field.null else ''}"
                )
                self.stdout.write(field_info)

        self.stdout.write("\nChecking database table structure...")

        with connection.cursor() as cursor:
            # Get table name from model
            table_name = model._meta.db_table
            self.stdout.write(f"Table name: {table_name}")

            # Get table info
            cursor.execute(
                """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
                """,
                [table_name],
            )
            columns = cursor.fetchall()

            self.stdout.write("\nDatabase columns:")
            for column in columns:
                self.stdout.write(
                    f"  {column[0]} ({column[1]}) "
                    f"{'NULL' if column[2] == 'YES' else 'NOT NULL'}"
                )

            # Get sequence info
            cursor.execute(
                """
                SELECT pg_get_serial_sequence(%s, 'id')
                """,
                [table_name],
            )
            sequence = cursor.fetchone()

            if sequence and sequence[0]:
                self.stdout.write(f"\nID Sequence: {sequence[0]}")
                cursor.execute("SELECT last_value, is_called FROM %s", [sequence[0]])
                seq_info = cursor.fetchone()
                self.stdout.write(f"Last Value: {seq_info[0]}")
                self.stdout.write(f"Is Called: {seq_info[1]}")

        # Check for mismatches
        model_fields = {field.name for field in fields if isinstance(field, Field)}
        db_columns = {col[0] for col in columns}

        missing_in_db = model_fields - db_columns
        missing_in_model = db_columns - model_fields

        if missing_in_db:
            self.stdout.write(
                self.style.ERROR(
                    f"\nFields in model but missing in database: {missing_in_db}"
                )
            )

        if missing_in_model:
            self.stdout.write(
                self.style.ERROR(
                    f"\nColumns in database but missing in model: {missing_in_model}"
                )
            )

        # Validate status field
        status_field = next(
            (f for f in fields if isinstance(f, Field) and f.name == "status"),
            None,
        )

        if status_field:
            self.stdout.write("\nStatus field found in model")
            # Additional status field validation could go here
        else:
            self.stdout.write(self.style.WARNING("\nStatus field not found in model"))

        self.stdout.write(self.style.SUCCESS("\nCheck complete"))
