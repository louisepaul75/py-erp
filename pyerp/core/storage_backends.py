"""
Custom storage backends for AWS S3 integration.
"""

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """
    Storage backend for static files on S3.
    """

    # location = settings.STATIC_LOCATION  # Removed class attribute
    default_acl = "public-read"
    file_overwrite = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", settings.STATIC_LOCATION)
        super().__init__(*args, **kwargs)


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for media files on S3.
    """

    # location = settings.MEDIA_LOCATION  # Removed class attribute
    default_acl = "public-read"
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("location", settings.MEDIA_LOCATION)
        super().__init__(*args, **kwargs)
