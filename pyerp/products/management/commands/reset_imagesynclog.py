from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Wipes the ImageSyncLog table and resets its ID sequence'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
  # noqa: F841
            help='Show SQL that would be executed without actually executing it',  # noqa: E501
  # noqa: E501, F841
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)

        # SQL to truncate the table and reset the sequence
        sql = """
        -- Truncate the table (remove all rows)
        TRUNCATE TABLE products_imagesynclog;

        -- Reset the ID sequence to start from 1
        ALTER SEQUENCE products_imagesynclog_id_seq RESTART WITH 1;
        """

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - SQL that would be executed:'))  # noqa: E501
            self.stdout.write(sql)
            return

        # Execute the SQL
        with connection.cursor() as cursor:
            self.stdout.write(self.style.WARNING('Wiping ImageSyncLog table...'))  # noqa: E501
            cursor.execute("TRUNCATE TABLE products_imagesynclog;")
            self.stdout.write(self.style.SUCCESS('Table truncated successfully.'))  # noqa: E501

            self.stdout.write(self.style.WARNING('Resetting ID sequence...'))
            cursor.execute("ALTER SEQUENCE products_imagesynclog_id_seq RESTART WITH 1;")  # noqa: E501
            self.stdout.write(self.style.SUCCESS('ID sequence reset successfully.'))  # noqa: E501

        self.stdout.write(self.style.SUCCESS('ImageSyncLog table has been reset.'))  # noqa: E501
