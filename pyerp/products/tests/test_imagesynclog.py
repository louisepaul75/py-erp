from django.test import TestCase
from pyerp.products.models import ImageSyncLog
from django.db import connections


class ImageSyncLogTest(TestCase):
    def test_create_log(self):
        """Test that we can create an ImageSyncLog instance with auto-incrementing ID."""  # noqa: E501
        # Print database connection information
        connection = connections['default']
        print(
            f"\nDATABASE INFO: {connection.vendor} - {connection.settings_dict['ENGINE']}")  # noqa: E501
        print(f"DATABASE NAME: {connection.settings_dict['NAME']}")
        if 'HOST' in connection.settings_dict:
            print(f"DATABASE HOST: {connection.settings_dict['HOST']}")

        log = ImageSyncLog()
        log.save()
        self.assertIsNotNone(log.id)
        self.assertTrue(log.id > 0)

        # Create another log to ensure IDs are incrementing
        log2 = ImageSyncLog()
        log2.save()
        self.assertIsNotNone(log2.id)
        self.assertTrue(log2.id > log.id)
