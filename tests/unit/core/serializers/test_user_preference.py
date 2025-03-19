import pytest
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from pyerp.core.models import UserPreference
from pyerp.core.serializers import UserPreferenceSerializer

User = get_user_model()


@pytest.mark.django_db
class TestUserPreferenceSerializer(TestCase):
    """Test the UserPreferenceSerializer."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword"
        )
        
        self.user_preference_data = {
            "user": self.user,
            "dashboard_config": json.dumps({"layout": "grid", "widgets": ["sales", "inventory"]}),
        }
        self.user_preference = UserPreference.objects.create(**self.user_preference_data)

    def test_serializer_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        serializer = UserPreferenceSerializer(instance=self.user_preference)
        data = serializer.data
        assert set(data.keys()) == {"id", "dashboard_config", "updated_at"}

    def test_serializer_read_only_fields(self):
        """Test that the read-only fields are actually read-only."""
        # Create a new user for this test
        new_user = User.objects.create_user(
            username="newuser",
            email="new@example.com",
            password="newpassword"
        )
        
        # Create serializer with data but without id and updated_at
        serializer = UserPreferenceSerializer(data={
            "dashboard_config": json.dumps({"layout": "list", "widgets": ["products"]}),
            "id": 999,  # This should be ignored as it's read-only
            "updated_at": "2023-01-01T00:00:00Z",  # This should be ignored as it's read-only
        }, context={"user": new_user})
        
        assert serializer.is_valid()
        
        # Save the serializer to create a new instance
        instance = serializer.save(user=new_user)
        
        # Verify that the id and updated_at were not set from the input data
        assert instance.id != 999
        
        # Verify that the dashboard_config was correctly set
        assert json.loads(instance.dashboard_config) == {"layout": "list", "widgets": ["products"]}

    def test_serializer_update(self):
        """Test updating an existing UserPreference with the serializer."""
        new_config = json.dumps({"layout": "compact", "widgets": ["orders", "customers"]})
        
        # Create serializer with an existing instance and new data
        serializer = UserPreferenceSerializer(
            instance=self.user_preference,
            data={"dashboard_config": new_config}
        )
        
        assert serializer.is_valid()
        updated_instance = serializer.save()
        
        # Verify that the instance was updated correctly
        assert updated_instance.dashboard_config == new_config
        
        # Reload from database to confirm persistence
        reloaded = UserPreference.objects.get(id=self.user_preference.id)
        assert reloaded.dashboard_config == new_config 