from rest_framework import serializers
from .models import AuditLog, UserPreference, Tag, TaggedItem, Notification
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


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


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for the Notification model."""
    
    # Optionally make user read-only if it's always set based on the request user
    # user = serializers.PrimaryKeyRelatedField(read_only=True)
    # Or include the username for easier frontend display
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            "id",
            "user", # Keep if needed, otherwise rely on username
            "username",
            "title",
            "content",
            "type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "username", "created_at", "updated_at"]

    def create(self, validated_data):
        # Ensure the user is set from the request context, not payload
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
