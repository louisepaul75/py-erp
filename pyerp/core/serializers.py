from rest_framework import serializers

from pyerp.core.models import UserPreference, AuditLog, Tag, TaggedItem


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model."""

    class Meta:
        model = UserPreference
        fields = ['id', 'user', 'dashboard_config', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    # Attempt to get username from related user if available, otherwise use stored username
    username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'timestamp',
            'event_type',
            'message',
            'username', # Use the method field
            'ip_address',
            'user_agent',
            'additional_data',
            'uuid',
            'user', # Include user FK for reference
            'content_type',
            'object_id',
        ]
        read_only_fields = [
            'id',
            'timestamp',
            'uuid',
            'content_type',
            'object_id',
            'username',
         ]
        extra_kwargs = {
             # Allow creating logs without associating a user/object initially via serializer
             'username': {'required': False, 'allow_null': True, 'read_only': True}, # Readonly as it's derived or backup
             'ip_address': {'required': False, 'allow_null': True},
             'user_agent': {'required': False, 'allow_blank': True},
             'additional_data': {'required': False, 'allow_null': True},
             'content_type': {'required': False, 'allow_null': True},
             'object_id': {'required': False, 'allow_blank': True},
             'user': {'required': False, 'allow_null': True},
        }

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return obj.username # Return backup username if user is deleted/null


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at'] # Slug is auto-generated on save


class TaggedItemSerializer(serializers.ModelSerializer):
    """Serializer for TaggedItem model."""
    class Meta:
        model = TaggedItem
        fields = ['id', 'tag', 'content_type', 'object_id', 'created_at']
        read_only_fields = ['id', 'created_at']
