from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

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