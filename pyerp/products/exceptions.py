"""Custom exceptions for the products module."""


class ImageAPIError(Exception):
    """Base exception for image API related errors."""


class NoResponseError(ImageAPIError):
    """Raised when no response is received from the API."""

    def __init__(self):
        super().__init__("No response received from API")


class InvalidResponseFormatError(ImageAPIError):
    """Raised when the API response format is invalid."""

    def __init__(self):
        super().__init__("Invalid response format from API")


class MissingFieldsError(ImageAPIError):
    """Raised when required fields are missing in the API response."""

    def __init__(self):
        super().__init__("Missing required fields in API response") 