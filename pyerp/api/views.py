import json
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from users.models import PermissionCategory
from users.serializers import PermissionCategorySerializer

class PermissionCategoriesView(APIView):
    """
    A view to list all permissions grouped by their categories from PermissionCategory model.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # Get all parent categories (those without a parent)
            categories = PermissionCategory.objects.filter(parent__isnull=True)
            
            # Serialize the categories with their permissions
            serializer = PermissionCategorySerializer(categories, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=500
            )

class PermissionListView(APIView):
    """
    API endpoint to list all available permissions.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        permissions = Permission.objects.all().values('id', 'name', 'codename', 'content_type__app_label')
        return Response(permissions)

class GroupPermissionsView(APIView):
    """
    API endpoint to manage permissions for a specific group.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, group_id):
        """Get permissions for a specific group"""
        group = get_object_or_404(Group, id=group_id)
        permissions = group.permissions.all().values('id', 'name', 'codename', 'content_type__app_label')
        return Response(permissions)

    def put(self, request, group_id):
        """Update permissions for a specific group"""
        group = get_object_or_404(Group, id=group_id)
        
        # Validate request data
        if not isinstance(request.data.get('permissions'), list):
            return Response(
                {"error": "permissions field must be a list of permission IDs"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get permissions from the provided IDs
            permission_ids = request.data['permissions']
            permissions = Permission.objects.filter(id__in=permission_ids)

            # Update group permissions
            group.permissions.set(permissions)

            # Return updated permissions
            updated_permissions = group.permissions.all().values(
                'id', 'name', 'codename', 'content_type__app_label'
            )
            return Response(updated_permissions)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 