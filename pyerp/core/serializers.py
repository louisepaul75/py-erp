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
    
    username = serializers.CharField(source='user.username', read_only=True)
    # Add fields for sender info, including last_seen
    sender_username = serializers.CharField(source='sender.username', read_only=True, allow_null=True)
    sender_last_seen = serializers.DateTimeField(source='sender.profile.last_seen', read_only=True, allow_null=True)
    
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "username",
            "sender", # Keep sender FK if needed
            "sender_username",
            "sender_last_seen",
            "title",
            "content",
            "type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "username", "sender", "sender_username", "sender_last_seen", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context['request']
        # Ensure the user is set from the request context
        # Ensure the sender is set from the request context
        validated_data['sender'] = request.user
        # If the notification is being created for a specific user (e.g., direct message)
        # the 'user' (recipient) should likely be passed in the data or determined elsewhere.
        # If the intention is for the recipient to always be the request user, adjust logic:
        # validated_data['user'] = request.user
        return super().create(validated_data)
