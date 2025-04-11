from rest_framework import viewsets, permissions
from django.contrib.auth.models import Group
from .serializers import GroupSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing group instances.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin users can manage groups 

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage users 