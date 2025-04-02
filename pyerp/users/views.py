from rest_framework import viewsets, permissions
from django.contrib.auth.models import Group
from .serializers import GroupSerializer

class GroupViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing group instances.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin users can manage groups 