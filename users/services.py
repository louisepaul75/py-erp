"""
Service layer for user, role, and permission management.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from .models import (
    UserProfile,
    Role,
    PermissionCategory,
    PermissionCategoryItem,
    DataPermission,
)

User = get_user_model()


class UserService:
    """
    Service for user-related operations beyond basic CRUD.
    """

    @staticmethod
    def assign_user_to_groups(user, group_ids):
        """
        Assign a user to multiple groups.

        Args:
            user: User instance
            group_ids: List of group IDs

        Returns:
            List of groups the user was assigned to
        """
        groups = Group.objects.filter(id__in=group_ids)
        user.groups.add(*groups)
        return groups

    @staticmethod
    def remove_user_from_groups(user, group_ids):
        """
        Remove a user from multiple groups.

        Args:
            user: User instance
            group_ids: List of group IDs

        Returns:
            List of groups the user was removed from
        """
        groups = Group.objects.filter(id__in=group_ids)
        user.groups.remove(*groups)
        return groups

    @staticmethod
    def get_users_by_permission(permission_codename):
        """
        Get all users who have a specific permission.

        Args:
            permission_codename: The codename of the permission

        Returns:
            QuerySet of User objects
        """
        try:
            # Users can have permissions directly or through groups
            perm = Permission.objects.get(codename=permission_codename)

            # Users with direct permission
            users_with_direct_perm = User.objects.filter(user_permissions=perm)

            # Users with permission through a group
            users_with_group_perm = User.objects.filter(groups__permissions=perm)

            # Combine the two querysets without duplicates
            return (users_with_direct_perm | users_with_group_perm).distinct()
        except Permission.DoesNotExist:
            # Return empty queryset if permission doesn't exist
            return User.objects.none()

    @staticmethod
    def update_user_status(user, new_status):
        """
        Update a user's status and handle related changes.

        Args:
            user: User instance
            new_status: New status string ('active', 'inactive', 'pending', 'locked')

        Returns:
            Updated user instance
        """
        # Ensure user has a profile
        if not hasattr(user, "profile"):
            UserProfile.objects.create(user=user)

        profile = user.profile
        profile.status = new_status

        # Handle related changes based on status
        if new_status == "active":
            user.is_active = True
        elif new_status in ("inactive", "locked"):
            user.is_active = False

        user.save()
        profile.save()
        return user

    @staticmethod
    def get_users_by_department(department):
        """
        Get all users in a specific department.

        Args:
            department: Department name

        Returns:
            QuerySet of User objects
        """
        return User.objects.filter(profile__department=department)

    @staticmethod
    def get_users_by_status(status):
        """
        Get all users with a specific status.

        Args:
            status: Status value ('active', 'inactive', 'pending', 'locked')

        Returns:
            QuerySet of User objects
        """
        return User.objects.filter(profile__status=status)

    @staticmethod
    def create_user_with_profile(username, email, password=None, **profile_data):
        """
        Create a new user with associated profile data.

        Args:
            username: Username for the new user
            email: Email for the new user
            password: Optional password (if not provided, user will need to reset)
            **profile_data: Additional profile fields like department, position, etc.

        Returns:
            Newly created User instance
        """
        # Create the base user
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        # User profile will be created automatically via signal
        # Just update with provided data
        if profile_data and hasattr(user, "profile"):
            profile = user.profile
            for key, value in profile_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            profile.save()

        return user


class RoleService:
    """
    Service for role and group management.
    """

    @staticmethod
    def create_role(
        group=None,
        name=None,
        description="",
        permissions=None,
        is_system_role=False,
        priority=0,
        parent_role=None,
    ):
        """
        Create a new role with associated group.

        Args:
            group: Existing Group object (takes precedence if provided)
            name: Name for the role/group (used to create a group if group not provided)
            description: Optional description
            permissions: List of Permission objects or IDs
            is_system_role: Whether this is a system-defined role
            priority: Priority level (higher numbers = higher priority)
            parent_role: Optional parent Role object

        Returns:
            Newly created Role instance
        """
        # Create the group if not provided
        if not group:
            if not name:
                raise ValueError("Either group or name must be provided")
            group = Group.objects.create(name=name)

        # Add permissions if provided
        if permissions:
            if isinstance(permissions[0], int):  # If IDs are provided
                permissions = Permission.objects.filter(id__in=permissions)
            group.permissions.add(*permissions)

        # Create the role
        role = Role.objects.create(
            group=group,
            description=description,
            is_system_role=is_system_role,
            priority=priority,
            parent_role=parent_role,
        )

        return role

    @staticmethod
    def get_users_in_role(role):
        """
        Get all users assigned to a role.

        Args:
            role: Role instance

        Returns:
            QuerySet of User objects
        """
        return User.objects.filter(groups=role.group)

    @staticmethod
    def get_all_child_roles(role):
        """
        Get all child roles (recursive) for a given role.

        Args:
            role: Role instance

        Returns:
            List of Role objects
        """
        children = list(role.child_roles.all())
        for child in list(
            children
        ):  # Create a copy to avoid modifying during iteration
            children.extend(RoleService.get_all_child_roles(child))
        return children


class PermissionService:
    """
    Service for permission management.
    """

    @staticmethod
    def get_user_permissions(user):
        """
        Get all permissions for a user, including group permissions.

        Args:
            user: User instance

        Returns:
            QuerySet of Permission objects
        """
        if user.is_superuser:
            return Permission.objects.all()

        # Get permissions from user and groups
        return Permission.objects.filter(Q(user=user) | Q(group__user=user)).distinct()

    @staticmethod
    def check_object_permission(user, obj, permission_type):
        """
        Check if user has permission for a specific object.

        Args:
            user: User instance
            obj: Model instance
            permission_type: Type of permission ('view', 'edit', 'delete', 'full')

        Returns:
            Boolean indicating if user has permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True

        # Get content type for the object
        content_type = ContentType.objects.get_for_model(obj)

        # Check for direct user permission
        user_has_perm = DataPermission.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.pk,
            permission_type__in=[permission_type, "full"],
        ).exists()

        if user_has_perm:
            return True

        # Check for group permission
        group_has_perm = DataPermission.objects.filter(
            group__in=user.groups.all(),
            content_type=content_type,
            object_id=obj.pk,
            permission_type__in=[permission_type, "full"],
        ).exists()

        return group_has_perm

    @staticmethod
    def get_objects_with_permission(user, model_class, permission_type):
        """
        Get all objects of a given model that user has permission for.

        Args:
            user: User instance
            model_class: Model class
            permission_type: Type of permission ('view', 'edit', 'delete', 'full')

        Returns:
            QuerySet of model instances
        """
        # Superusers can access all objects
        if user.is_superuser:
            return model_class.objects.all()

        content_type = ContentType.objects.get_for_model(model_class)

        # Get object IDs from user permissions
        user_object_ids = DataPermission.objects.filter(
            user=user,
            content_type=content_type,
            permission_type__in=[permission_type, "full"],
        ).values_list("object_id", flat=True)

        # Get object IDs from group permissions
        group_object_ids = DataPermission.objects.filter(
            group__in=user.groups.all(),
            content_type=content_type,
            permission_type__in=[permission_type, "full"],
        ).values_list("object_id", flat=True)

        # Combine object IDs
        object_ids = list(user_object_ids) + list(group_object_ids)

        # Return objects with those IDs
        return model_class.objects.filter(pk__in=object_ids)

    @staticmethod
    def organize_permissions_by_category():
        """
        Organize all permissions by category for UI display.

        Returns:
            List of category dictionaries with their permissions
        """
        categories = []

        for category in PermissionCategory.objects.all():
            perms = Permission.objects.filter(
                permissioncategoryitem__category=category
            ).values("id", "name", "codename")

            categories.append(
                {
                    "name": category.name,
                    "description": category.description,
                    "icon": category.icon,
                    "permissions": list(perms),
                }
            )

        # Add uncategorized permissions
        categorized_perm_ids = PermissionCategoryItem.objects.values_list(
            "permission_id", flat=True
        )

        uncategorized = Permission.objects.exclude(id__in=categorized_perm_ids).values(
            "id", "name", "codename"
        )

        if uncategorized.exists():
            categories.append(
                {
                    "name": "Uncategorized",
                    "description": "Permissions not assigned to any category",
                    "icon": "question-mark",
                    "permissions": list(uncategorized),
                }
            )

        return categories
