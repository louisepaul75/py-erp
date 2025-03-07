"""
Unit tests for core views.

This file demonstrates how to test views in the core module.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase

User = get_user_model()

class TestHealthCheckView(TestCase):
    """Tests for the health_check view."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_health_check_healthy(self):
        """Test the health check view when everything is healthy."""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("database", data)
        self.assertEqual(data["database"]["status"], "connected")
        self.assertEqual(data["database"]["message"], "Database is connected")
        self.assertIn("environment", data)
        self.assertIn("version", data)


class TestUserProfileView(TestCase):
    """Tests for the UserProfileView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test getting a user profile."""
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["first_name"], "Test")
        self.assertEqual(data["last_name"], "User")
        self.assertFalse(data["is_staff"])
        self.assertFalse(data["is_superuser"])

    def test_update_profile_valid(self):
        """Test updating a user profile with valid data."""
        data = {
            "email": "new@example.com",
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = self.client.patch("/api/profile/", data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Profile updated successfully")
        self.assertEqual(response.json()["updated_fields"]["email"], "new@example.com")
        self.assertEqual(response.json()["updated_fields"]["first_name"], "Updated")
        self.assertEqual(response.json()["updated_fields"]["last_name"], "Name")

        # Verify the changes were saved
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@example.com")
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_update_profile_invalid(self):
        """Test updating a user profile with invalid data."""
        data = {
            "email": "invalid-email",
            "profile": {
                "website": "invalid-url",
            },
        }
        response = self.client.patch("/api/profile/", data, format="json")
        self.assertEqual(response.status_code, 400)
        # Add more assertions based on expected response

    def test_update_profile_no_changes(self):
        """Test updating a user profile with no valid fields."""
        data = {
            "invalid_field": "value"
        }
        response = self.client.patch("/api/profile/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "No valid fields to update")

    def test_update_profile_unauthenticated(self):
        """Test updating a user profile when not authenticated."""
        self.client.force_authenticate(user=None)
        data = {
            "email": "new@example.com"
        }
        response = self.client.patch("/api/profile/", data, format="json")
        self.assertEqual(response.status_code, 401)
