import logging
import subprocess

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import PermissionCategory
from users.serializers import PermissionCategorySerializer

logger = logging.getLogger(__name__)


class PermissionCategoriesView(APIView):
    """
    A view to list all permissions grouped by their categories from
    PermissionCategory model.
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
        permissions = Permission.objects.all().values(
            "id", "name", "codename", "content_type__app_label"
        )
        return Response(permissions)


class GroupPermissionsView(APIView):
    """
    API endpoint to manage permissions for a specific group.
    """

    permission_classes = [IsAdminUser]

    def get(self, request, group_id):
        """Get permissions for a specific group"""
        group = get_object_or_404(Group, id=group_id)
        permissions = group.permissions.all().values(
            "id", "name", "codename", "content_type__app_label"
        )
        return Response(permissions)

    def put(self, request, group_id):
        """Update permissions for a specific group"""
        group = get_object_or_404(Group, id=group_id)
        
        # Validate request data
        if not isinstance(request.data.get("permissions"), list):
            return Response(
                {
                    "error": "permissions field must be a list of permission IDs" # noqa E501
                },
                status=status.HTTP_400_BAD_REQUEST,
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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_git_branch(request):
    """
    API endpoint to retrieve the current git branch name.
    Returns 'unknown' if git command fails or is unavailable.
    """
    try:
        # Ensure we run the command from the project's root directory
        project_root = settings.BASE_DIR
        
        # Run the git command
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,  # Raises CalledProcessError if command fails
            cwd=project_root,  # Execute in the project root
        )
        
        branch_name = result.stdout.strip()
        return JsonResponse({'branch': branch_name})

    except (FileNotFoundError, subprocess.CalledProcessError):
        # Git command not found or failed (e.g., not a git repository,
        # git not installed)
        # Return a default value instead of 500 error in production
        return JsonResponse({"branch": "unknown"}, status=status.HTTP_200_OK)
    except Exception as e:
        # Catch any other unexpected errors, but still try to avoid 500
        logger.error(
            f"Unexpected error in get_git_branch: {str(e)}"  # Log the error
        )
        return JsonResponse({"branch": "error"}, status=status.HTTP_200_OK)