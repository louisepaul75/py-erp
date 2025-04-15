from rest_framework import viewsets, mixins
from rest_framework.response import Response
from .models import SalesRecordRelationship
from .serializers import SalesRecordRelationshipSerializer


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
        return {
            "id": pk,
            "name": "Example Sale",
            "description": "This is a placeholder",
        }


# This helps other modules check if this module is available
API_VERSION = "0.1.0"


# Change to use GenericAPIView and ListModelMixin for more explicit control
class SalesRecordRelationshipViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   mixins.CreateModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.DestroyModelMixin,
                                   viewsets.GenericViewSet):
    """
    API endpoint that allows Sales Record Relationships to be viewed or edited.
    (Using GenericViewSet for more explicit control)
    """
    # Keep for router introspection
    queryset = SalesRecordRelationship.objects.all()
    serializer_class = SalesRecordRelationshipSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Ensure queryset is evaluated per request, respecting transactions."""
        # This overrides the class attribute for actual data fetching
        qs = SalesRecordRelationship.objects.all()
        return qs

    # Explicitly define list to bypass mixin behavior
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
