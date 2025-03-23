import pytest
from django.db import connections
from django.test import TestCase

from pyerp.business_modules.products.models import ImageSyncLog


@pytest.mark.backend
@pytest.mark.database
class ImageSyncLogTest(TestCase):




    def test_create_log(self):
        """Test that we can create an ImageSyncLog instance with auto-incrementing ID."""
        connection = connections["default"]
        print(
            f"\nDATABASE INFO: {connection.vendor} - {connection.settings_dict['ENGINE']}",
        )
        print(f"DATABASE NAME: {connection.settings_dict['NAME']}")
        if "HOST" in connection.settings_dict:
            print(f"DATABASE HOST: {connection.settings_dict['HOST']}")

        log = ImageSyncLog()
        log.save()
        assert log.id is not None
        assert log.id > 0

        # Create another log to ensure IDs are incrementing
        log2 = ImageSyncLog()
        log2.save()
        assert log2.id is not None
        assert log2.id > log.id
