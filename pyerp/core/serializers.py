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
    # Attempt to get username from related user if available, 
    # otherwise use stored username
    username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'timestamp',
            'event_type',
            'message',
            'username',  # Use the method field
            'ip_address',
            'user_agent',
            'additional_data',
            'uuid',
            'user',  # Include user FK for reference
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
             # Allow creating logs without associating a user/object 
             # initially via serializer
             'username': {
                 'required': False, 'allow_null': True, 'read_only': True
             },  # Readonly as it's derived or backup
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
        return obj.username  # Return backup username if user is deleted/null


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'slug', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'created_at', 'updated_at'
        ]  # Slug is auto-generated on save


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
    sender_username = serializers.CharField(
        source='sender.username', read_only=True, allow_null=True
    )
    sender_last_seen = serializers.DateTimeField(
        source='sender.profile.last_seen', read_only=True, allow_null=True
    )
    
    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "username",
            "sender",
            "sender_username",
            "sender_last_seen",
            "title",
            "content",
            "type",
            "is_read",
            "is_completed",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "username",
            "sender_username",
            "sender_last_seen",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            'user': {'required': False, 'allow_null': True},
            'sender': {'required': False, 'allow_null': True},
            'is_completed': {'required': False, 'allow_null': True},
            'priority': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def validate(self, data):
        """Ensure is_completed and priority are only set for TODO type."""
        notification_type = data.get(
            'type', getattr(self.instance, 'type', None)
        )
        is_completed = data.get('is_completed', None)
        priority = data.get('priority', None)

        if notification_type != Notification.NotificationType.TODO:
            # Allow setting to False for existing non-todos if needed?
            if is_completed is not None and is_completed is not False: 
                raise serializers.ValidationError({
                    'is_completed': _(
                        "Completion status can only be set for "
                        "To-Do notifications."
                    )
                })
            if priority is not None:
                raise serializers.ValidationError({
                    'priority': _(
                        "Priority can only be set for To-Do notifications."
                    )
                })
        elif notification_type == Notification.NotificationType.TODO:
            # Optionally enforce priority for ToDos if desired
            # if priority is None:
            #     raise serializers.ValidationError({
            #         'priority': _(
            #             "Priority must be set for To-Do notifications."
            #         )
            #     })
            # Ensure is_completed is treated as boolean, 
            # defaulting to False if None/null is passed
            if is_completed is None:
                data['is_completed'] = False  # Default if not provided for TODO

        return data

    def create(self, validated_data):
        # Ensure sender is set, typically the authenticated user
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data['sender'] = request.user

            # If recipient ('user') is not provided, default to the sender (authenticated user)
            if 'user' not in validated_data:
                validated_data['user'] = request.user

        # Recipient ('user') MUST be provided if the request is unauthenticated
        # or if we explicitly want to allow creating notifications without a logged-in user
        # (e.g., system processes). Add specific checks if needed.
        elif 'user' not in validated_data:
            # This case should ideally not happen for authenticated requests due to the block above.
            # If it can happen (e.g., anonymous user API access allowed for specific types),
            # raise an error or handle appropriately.
            raise serializers.ValidationError({
                'user': _("Recipient user must be specified.")
            })

        # Handle default values specifically for TODO type if not provided
        if validated_data.get('type') == Notification.NotificationType.TODO:
            validated_data.setdefault('is_completed', False)
            # validated_data.setdefault(
            #     'priority', Notification.PriorityLevel.MEDIUM
            # )  # Example default priority

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing the type of an existing notification?
        validated_data.pop('type', None) 
        
        # Handle setting completion/priority specifically for TODOs during update
        if instance.type == Notification.NotificationType.TODO:
            instance.is_completed = validated_data.get(
                'is_completed', instance.is_completed
            )
            instance.priority = validated_data.get(
                'priority', instance.priority
            )
        else:
            # Ensure these fields aren't updated for non-TODOs
            validated_data.pop('is_completed', None)
            validated_data.pop('priority', None)
        
        # Apply other updates
        instance.is_read = validated_data.get('is_read', instance.is_read)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        # Add other updatable fields as needed
        
        instance.save()
        return instance
