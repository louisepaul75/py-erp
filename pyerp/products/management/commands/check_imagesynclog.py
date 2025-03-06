from django.core.management.base import BaseCommand
from django.db import connection
from pyerp.products.models import ImageSyncLog


class Command(BaseCommand):
    help = 'Checks the structure of the ImageSyncLog model and table'  # noqa: F841
  # noqa: F841

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking ImageSyncLog model structure...'))  # noqa: E501

        # Check model fields
        self.stdout.write('\nModel Fields:')
        self.stdout.write('=' * 80)

        for field in ImageSyncLog._meta.fields:
            field_type = field.get_internal_type()

            # Get default value
            if hasattr(field, 'default'):
                default = field.default
                if callable(default):
                    default_str = "callable"
                else:
                    default_str = str(default)
            else:
                default_str = "None"

            # Get auto_now and auto_now_add for DateTimeField
            auto_now = getattr(field, 'auto_now', False)
            auto_now_add = getattr(field, 'auto_now_add', False)

            # Get choices
            choices = getattr(field, 'choices', None)
            choices_str = str(choices) if choices else "None"

            # Get max_length for CharField
            max_length = getattr(field, 'max_length', None)
            max_length_str = str(max_length) if max_length else "N/A"

            self.stdout.write(f"{field.name:<20} {field_type:<20} Default: {default_str:<20}")  # noqa: E501

            if field_type == 'DateTimeField':
                self.stdout.write(f"{'  auto_now:':<20} {str(auto_now):<20}")
                self.stdout.write(f"{'  auto_now_add:':<20} {str(auto_now_add):<20}")  # noqa: E501

            if field_type == 'CharField':
  # noqa: F841
                self.stdout.write(f"{'  max_length:':<20} {max_length_str:<20}")  # noqa: E501
                self.stdout.write(f"{'  choices:':<20} {choices_str:<60}")

        # Check database structure
        with connection.cursor() as cursor:
            # Get column information
            cursor.execute("""
                SELECT
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM
                    information_schema.columns
                WHERE
                    table_name = 'products_imagesynclog'  # noqa: F841
                ORDER BY
                    ordinal_position
            """)

            columns = cursor.fetchall()

            self.stdout.write('\nDatabase Columns:')
            self.stdout.write('=' * 100)
            self.stdout.write(f"{'Column Name':<20} {'Data Type':<20} {'Max Length':<15} {'Nullable':<10} {'Default':<30}")  # noqa: E501
            self.stdout.write('-' * 100)

            for col in columns:
                col_name, data_type, max_length, nullable, default = col
                max_length_str = str(max_length) if max_length is not None else ""  # noqa: E501
                self.stdout.write(f"{col_name:<20} {data_type:<20} {max_length_str:<15} {nullable:<10} {str(default or ''):<30}")  # noqa: E501

            # Get constraints
            cursor.execute("""
                SELECT
                    tc.constraint_name,
                    tc.constraint_type,
                    kcu.column_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                WHERE
                    tc.table_name = 'products_imagesynclog'
  # noqa: F841
                ORDER BY
                    tc.constraint_type,
                    tc.constraint_name
            """)

            constraints = cursor.fetchall()

            if constraints:
                self.stdout.write('\nTable Constraints:')
                self.stdout.write('=' * 80)
                self.stdout.write(f"{'Constraint Name':<40} {'Type':<20} {'Column':<20}")  # noqa: E501
                self.stdout.write('-' * 80)

                for constraint in constraints:
                    name, type_, column = constraint
                    self.stdout.write(f"{name:<40} {type_:<20} {column:<20}")

            # Get sequence information
            cursor.execute("SELECT pg_get_serial_sequence('products_imagesynclog', 'id')")  # noqa: E501
            sequence = cursor.fetchone()

            if sequence and sequence[0]:
                self.stdout.write(f'\nID Sequence: {sequence[0]}')
                cursor.execute(f"SELECT last_value, is_called FROM {sequence[0]}")  # noqa: E501
                seq_info = cursor.fetchone()
                self.stdout.write(f'Last Value: {seq_info[0]}')
                self.stdout.write(f'Is Called: {seq_info[1]}')

        # Check for mismatches
        model_fields = {field.name for field in ImageSyncLog._meta.fields}
        db_columns = {col[0] for col in columns}

        missing_in_db = model_fields - db_columns
        missing_in_model = db_columns - model_fields

        if missing_in_db:
            self.stdout.write(self.style.ERROR(f'\nFields in model but missing in database: {missing_in_db}'))  # noqa: E501

        if missing_in_model:
            self.stdout.write(self.style.ERROR(f'\nColumns in database but missing in model: {missing_in_model}'))  # noqa: E501

        if not missing_in_db and not missing_in_model:
            self.stdout.write(self.style.SUCCESS('\nAll fields match between model and database!'))  # noqa: E501

        # Validate status field
        status_field = next((f for f in ImageSyncLog._meta.fields if f.name == 'status'), None)  # noqa: E501
        status_column = next((c for c in columns if c[0] == 'status'), None)

        if status_field and status_column:
            model_max_length = getattr(status_field, 'max_length', None)
            db_max_length = status_column[2]

            if model_max_length != db_max_length and db_max_length is not None:
                self.stdout.write(self.style.WARNING(
                    f'\nStatus field max_length mismatch: Model={model_max_length}, DB={db_max_length}'  # noqa: E501
  # noqa: E501, F841
                ))
            else:
                self.stdout.write(self.style.SUCCESS('\nStatus field max_length is consistent.'))  # noqa: E501

        self.stdout.write(self.style.SUCCESS('\nImageSyncLog structure check completed.'))  # noqa: E501
