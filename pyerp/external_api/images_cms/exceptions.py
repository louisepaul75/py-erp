"""
Exceptions for the Images CMS API.
"""


class ImageAPIError(Exception):
    """Base exception for all image API errors."""


class NoResponseError(ImageAPIError):
    """Raised when no response is received from the API."""

    def __str__(self):
        return "No response received from the image API."


class InvalidResponseFormatError(ImageAPIError):
    """Raised when the API response is not in the expected format."""

    def __str__(self):
        return "The image API response is not in the expected format."


class MissingFieldsError(ImageAPIError):
    """Raised when required fields are missing from the API response."""

    def __str__(self):
        return "The image API response is missing required fields."
