from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

User = get_user_model()

class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for the Group model.
    """
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'description']
        extra_kwargs = {
            'description': {'required': False}
        }

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']

class PermissionCategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    permissions = PermissionSerializer(many=True)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model (list/basic details)."""
    name = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True, read_only=True) # Use existing GroupSerializer
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'name',  # Combined name
            'role',  # Derived role based on permissions
            'is_active', 
            'is_staff', 
            'is_superuser', 
            'groups',
            'date_joined',
            'last_login',
            'status',  # This appears to be a custom field in the response
            'department'  # This appears to be a custom field in the response
        ]
        read_only_fields = [
            'id', 
            'username', 
            'is_staff', 
            'is_superuser', 
            'groups', 
            'date_joined', 
            'last_login'
        ]

    def get_name(self, obj):
        """Combine first and last name."""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.username
        
    def get_role(self, obj):
        """Determine role based on permissions."""
        if obj.is_superuser:
            return "Admin"
        elif obj.is_staff:
            return "Editor"
        else:
            return "Viewer" 