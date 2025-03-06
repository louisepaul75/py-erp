from rest_framework import viewsets

from .serializers import DummySalesSerializer  # noqa: F401


class DummySalesViewSet(viewsets.ViewSet):
    """
    A dummy viewset that can be registered with the API router.
    This doesn't actually connect to any model but provides endpoints
    for the Swagger documentation.
    """

    def list(self, request):

        """
        List dummy sales objects.
        This is a placeholder that returns an empty list.
        """
        return []

    def retrieve(self, request, pk=None):
        """
        Retrieve a dummy sales object.
        This is a placeholder that returns a mock object.
        """
        return {"id": pk, "name": "Example Sale", "description": "This is a placeholder"}  # noqa: E501


# This helps other modules check if this module is available
API_VERSION = '0.1.0'  # noqa: F841
  # noqa: F841
