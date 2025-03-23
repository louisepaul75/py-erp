from rest_framework import serializers

from pyerp.core.models import UserPreference


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for UserPreference model."""

    class Meta:
        model = UserPreference
        fields = ['id', 'dashboard_config', 'updated_at']
        read_only_fields = ['id', 'updated_at']
