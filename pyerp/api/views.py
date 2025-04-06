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
import subprocess
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

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

@api_view(['GET'])
@permission_classes([AllowAny])
def get_git_branch(request):
    """
    API endpoint to retrieve the current git branch name.
    """
    try:
        # Ensure we run the command from the project's root directory
        project_root = settings.BASE_DIR
        
        # Run the git command
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True, # Raises CalledProcessError if command fails
            cwd=project_root  # Execute in the project root
        )
        
        branch_name = result.stdout.strip()
        return JsonResponse({'branch': branch_name})

    except FileNotFoundError:
        # Git command not found
        return JsonResponse({'error': 'Git command not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except subprocess.CalledProcessError as e:
        # Git command failed (e.g., not a git repository)
        error_message = f"Git command failed: {e.stderr.strip()}" if e.stderr else f"Git command failed with exit code {e.returncode}"
        return JsonResponse({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        # Catch any other unexpected errors
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 