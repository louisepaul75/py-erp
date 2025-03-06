"""
Custom storage backends for AWS S3 integration.
"""

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage backend for static files on S3.
    """

    location = settings.STATIC_LOCATION
    default_acl = "public-read"
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for media files on S3.
    """

    location = settings.MEDIA_LOCATION
    default_acl = "public-read"
    file_overwrite = False
