"""
Tests for storage backends.

This module tests the functionality of the storage backends defined in
pyerp/core/storage_backends.py, ensuring that they are configured correctly.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.conf import settings

from pyerp.core.storage_backends import StaticStorage, MediaStorage


class StorageBackendsTests(TestCase):
    """Tests for the storage backends."""
    
    @patch('pyerp.core.storage_backends.S3Boto3Storage')
    def test_static_storage_configuration(self, mock_s3_storage):
        """Test StaticStorage is configured correctly."""
        # Create an instance of StaticStorage
        static_storage = StaticStorage()
        
        # Verify the configuration
        self.assertEqual(static_storage.location, settings.STATIC_LOCATION)
        self.assertEqual(static_storage.default_acl, "public-read")
        self.assertTrue(static_storage.file_overwrite)
        
    @patch('pyerp.core.storage_backends.S3Boto3Storage')
    def test_media_storage_configuration(self, mock_s3_storage):
        """Test MediaStorage is configured correctly."""
        # Create an instance of MediaStorage
        media_storage = MediaStorage()
        
        # Verify the configuration
        self.assertEqual(media_storage.location, settings.MEDIA_LOCATION)
        self.assertEqual(media_storage.default_acl, "public-read")
        self.assertFalse(media_storage.file_overwrite)
        
    @override_settings(
        STATIC_LOCATION="static-test",
        MEDIA_LOCATION="media-test"
    )
    @patch('pyerp.core.storage_backends.S3Boto3Storage')
    def test_storage_with_custom_settings(self, mock_s3_storage):
        """Test storage backends with custom settings."""
        # Create instances with custom settings
        static_storage = StaticStorage()
        media_storage = MediaStorage()
        
        # Verify the configuration reflects the custom settings
        self.assertEqual(static_storage.location, "static-test")
        self.assertEqual(media_storage.location, "media-test")
        self.assertEqual(static_storage.default_acl, "public-read")
        self.assertFalse(media_storage.file_overwrite)

    @override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
                       MEDIA_LOCATION='media-test',
                       STATIC_LOCATION='static/')
    def test_storage_with_custom_settings(self):
        """Test storage backend configuration with overridden settings."""
        static_storage = StaticStorage()
        media_storage = MediaStorage()

        # Static location should use the default from testing.py settings
        self.assertEqual(static_storage.location, "static/")
        # Media location should use the overridden value
        self.assertEqual(media_storage.location, "media-test")
        # Check other default properties remain
        self.assertEqual(static_storage.default_acl, "public-read")
        self.assertFalse(media_storage.file_overwrite) 