"""
Custom storage backends for AWS S3 integration.
"""

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage backend for static files on S3.
    """
    location = settings.STATIC_LOCATION  # noqa: F841
    default_acl = 'public-read'  # noqa: F841
    file_overwrite = True  # noqa: F841


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for media files on S3.
    """
    location = settings.MEDIA_LOCATION  # noqa: F841
    default_acl = 'public-read'  # noqa: F841
    file_overwrite = False  # noqa: F841
