"""
Serializers for the users app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from .models import (
    UserProfile,
    Role,
    PermissionCategory,
    PermissionCategoryItem,
    DataPermission,
)

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model.
    """

    class Meta:
        model = UserProfile
        fields = [
            "department",
            "position",
            "phone",
            "language_preference",
            "profile_picture",
            "status",
            "two_factor_enabled",
            "last_password_change",
        ]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model with basic fields and profile information.
    """

    department = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
            "department",
            "status",
        ]
        read_only_fields = ["is_active", "is_staff", "date_joined"]

    def get_department(self, obj):
        """Get department from profile."""
        if hasattr(obj, "profile"):
            return obj.profile.department
        return ""

    def get_status(self, obj):
        """Get status from profile."""
        if hasattr(obj, "profile"):
            return obj.profile.status
        return "active"  # Default value


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the User model with all fields including profile.
    """

    groups = serializers.SerializerMethodField()
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "profile",
            "groups",
        ]
        read_only_fields = [
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
        ]

    def get_groups(self, obj):
        """Return the user's groups with minimal information."""
        return [{"id": group.id, "name": group.name} for group in obj.groups.all()]

    def create(self, validated_data):
        """Create a User with associated UserProfile."""
        profile_data = validated_data.pop("profile", {})
        user = User.objects.create_user(**validated_data)

        # Check if profile already exists (created by signal) and update it
        # instead of creating a new one
        if hasattr(user, "profile"):
            profile = user.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        else:
            # Create profile if it doesn't exist
            UserProfile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        """Update the User and UserProfile together."""
        profile_data = validated_data.pop("profile", None)

        # Update User instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update UserProfile instance if data provided
        if profile_data and hasattr(instance, "profile"):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model.
    """

    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "permissions_count", "users_count", "role"]

    def get_permissions_count(self, obj):
        """Return the number of permissions in the group."""
        return obj.permissions.count()

    def get_users_count(self, obj):
        """Return the number of users in the group."""
        return obj.user_set.count()

    def get_role(self, obj):
        """Return associated role information if it exists."""
        try:
            role = obj.role
            return {
                "id": role.id,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "priority": role.priority,
                "parent_role_id": role.parent_role_id,
            }
        except Role.DoesNotExist:
            return None


class GroupDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Group model including permissions.
    """

    permissions = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["id", "name", "permissions", "users_count", "role"]

    def get_permissions(self, obj):
        """Return all permissions in the group."""
        return [
            {
                "id": perm.id,
                "name": perm.name,
                "codename": perm.codename,
                "content_type": perm.content_type.app_label
                + "."
                + perm.content_type.model,
            }
            for perm in obj.permissions.all()
        ]

    def get_users_count(self, obj):
        """Return the number of users in the group."""
        return obj.user_set.count()

    def get_role(self, obj):
        """Return associated role information if it exists."""
        try:
            role = obj.role
            return {
                "id": role.id,
                "description": role.description,
                "is_system_role": role.is_system_role,
                "priority": role.priority,
                "parent_role_id": role.parent_role_id,
            }
        except Role.DoesNotExist:
            return None


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """

    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "group",
            "group_name",
            "description",
            "is_system_role",
            "priority",
            "parent_role",
        ]
        read_only_fields = ["group_name"]

    def create(self, validated_data):
        """Create a new role using the RoleService."""
        from .services import RoleService

        group = validated_data.get("group")
        description = validated_data.get("description", "")
        is_system_role = validated_data.get("is_system_role", False)
        priority = validated_data.get("priority", 0)
        parent_role = validated_data.get("parent_role", None)

        return RoleService.create_role(
            group=group,
            description=description,
            is_system_role=is_system_role,
            priority=priority,
            parent_role=parent_role,
        )

    def update(self, instance, validated_data):
        """Update an existing role."""
        instance.description = validated_data.get("description", instance.description)
        instance.is_system_role = validated_data.get(
            "is_system_role", instance.is_system_role
        )
        instance.priority = validated_data.get("priority", instance.priority)
        instance.parent_role = validated_data.get("parent_role", instance.parent_role)
        instance.save()
        return instance


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Permission model.
    """

    content_type_name = serializers.CharField(
        source="content_type.model_class.__name__", read_only=True
    )
    app_label = serializers.CharField(source="content_type.app_label", read_only=True)

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "codename",
            "content_type",
            "content_type_name",
            "app_label",
        ]


class PermissionCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the PermissionCategory model with nested permissions.
    """
    permissions = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = PermissionCategory
        fields = ['id', 'name', 'description', 'icon', 'permissions', 'subcategories']

    def get_permissions(self, obj):
        permissions = Permission.objects.filter(permissioncategoryitem__category=obj)
        return PermissionSerializer(permissions, many=True).data

    def get_subcategories(self, obj):
        return PermissionCategorySerializer(obj.subcategories.all(), many=True).data


class PermissionCategoryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the PermissionCategoryItem model.
    """

    class Meta:
        model = PermissionCategoryItem
        fields = ["id", "category", "permission"]


class DataPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for the DataPermission model.
    """

    content_type_name = serializers.CharField(
        source="content_type.model_class.__name__", read_only=True
    )

    class Meta:
        model = DataPermission
        fields = [
            "id",
            "user",
            "group",
            "content_type",
            "content_type_name",
            "object_id",
            "permission_type",
            "created_at",
            "created_by",
            "expires_at",
        ]
        read_only_fields = ["created_at", "content_type_name"]
