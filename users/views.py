"""
API views for user, role, and permission management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import UserProfile, Role, PermissionCategory
from .serializers import (
    UserSerializer, UserDetailSerializer, GroupSerializer, 
    PermissionSerializer, RoleSerializer, UserProfileSerializer
)
from .services import UserService, RoleService, PermissionService

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'profile__department']
    ordering_fields = ['username', 'email', 'date_joined', 'profile__department']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return UserDetailSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=True, methods=['post'])
    def assign_groups(self, request, pk=None):
        """
        Assign user to groups.
        """
        user = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        if not group_ids:
            return Response(
                {"detail": "No group IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            groups = UserService.assign_user_to_groups(user, group_ids)
            return Response({
                "detail": f"User assigned to {len(groups)} groups",
                "groups": GroupSerializer(groups, many=True).data
            })
        except Group.DoesNotExist:
            return Response(
                {"detail": "One or more groups not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_groups(self, request, pk=None):
        """
        Remove user from groups.
        """
        user = self.get_object()
        group_ids = request.data.get('group_ids', [])
        
        if not group_ids:
            return Response(
                {"detail": "No group IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            groups = UserService.remove_user_from_groups(user, group_ids)
            return Response({
                "detail": f"User removed from {len(groups)} groups",
                "groups": GroupSerializer(groups, many=True).data
            })
        except Group.DoesNotExist:
            return Response(
                {"detail": "One or more groups not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update user status.
        """
        user = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status or new_status not in ['active', 'inactive', 'pending', 'locked']:
            return Response(
                {"detail": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_user = UserService.update_user_status(user, new_status)
        return Response(UserDetailSerializer(updated_user).data)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """
        Get users filtered by department.
        """
        department = request.query_params.get('department')
        if not department:
            return Response(
                {"detail": "Department parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = UserService.get_users_by_department(department)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get users filtered by status.
        """
        status_param = request.query_params.get('status')
        if not status_param or status_param not in ['active', 'inactive', 'pending', 'locked']:
            return Response(
                {"detail": "Valid status parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = UserService.get_users_by_status(status_param)
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """Filter profiles by department if specified"""
        queryset = UserProfile.objects.all()
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department=department)
        return queryset


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for groups.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get users in this group.
        """
        group = self.get_object()
        users = User.objects.filter(groups=group)
        
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """
        Get permissions for this group.
        """
        group = self.get_object()
        permissions = group.permissions.all()
        
        page = self.paginate_queryset(permissions)
        if page is not None:
            serializer = PermissionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_permissions(self, request, pk=None):
        """
        Add permissions to this group.
        """
        group = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        if not permission_ids:
            return Response(
                {"detail": "No permission IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
            if len(permissions) != len(permission_ids):
                return Response(
                    {"detail": "One or more permissions not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            group.permissions.add(*permissions)
            return Response({
                "detail": f"Added {len(permissions)} permissions to group",
                "permissions": PermissionSerializer(permissions, many=True).data
            })
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def remove_permissions(self, request, pk=None):
        """
        Remove permissions from this group.
        """
        group = self.get_object()
        permission_ids = request.data.get('permission_ids', [])
        
        if not permission_ids:
            return Response(
                {"detail": "No permission IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            permissions = Permission.objects.filter(id__in=permission_ids)
            group.permissions.remove(*permissions)
            return Response({
                "detail": f"Removed {len(permissions)} permissions from group",
                "permissions": PermissionSerializer(permissions, many=True).data
            })
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for permissions (read-only).
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'codename']
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get permissions organized by category.
        """
        categorized_perms = PermissionService.organize_permissions_by_category()
        return Response(categorized_perms)


class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['group__name', 'description']
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """
        Get users in this role.
        """
        role = self.get_object()
        users = RoleService.get_users_in_role(role)
        
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def child_roles(self, request, pk=None):
        """
        Get all child roles (including descendants).
        """
        role = self.get_object()
        child_roles = RoleService.get_all_child_roles(role)
        
        serializer = RoleSerializer(child_roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_child_role(self, request, pk=None):
        """
        Add a child role.
        """
        parent_role = self.get_object()
        
        # Check if the request is to link an existing role
        child_role_id = request.data.get('child_role_id')
        
        if child_role_id:
            try:
                child_role = get_object_or_404(Role, id=child_role_id)
                # Prevent circular references
                if parent_role.id == child_role.id:
                    return Response(
                        {"detail": "Cannot add role as child of itself"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                # Check if this would create a cycle
                if parent_role in RoleService.get_all_child_roles(child_role):
                    return Response(
                        {"detail": "Cannot add role as child because it would create a cycle"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                    
                child_role.parent_role = parent_role
                child_role.save()
                
                return Response(RoleSerializer(child_role).data)
            except Role.DoesNotExist:
                return Response(
                    {"detail": "Child role not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Create a new role as a child
            # Copy relevant data from request
            role_data = request.data.copy()
            
            # Set the parent role
            role_data['parent_role'] = parent_role.id
            
            serializer = self.get_serializer(data=role_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
