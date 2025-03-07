"""
Unit tests for core views.

This file demonstrates how to test views in the core module.
"""

from django.test import Client, TestCase

# Avoid importing from rest_framework.test which causes metaclass conflicts
# from rest_framework.test import APIClient, APITestCase


class TestHealthCheckView(TestCase):
    """Tests for the health_check view."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_health_check_healthy(self):
        """Test the health check view when everything is healthy."""
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")
        self.assertIn("database", response.json())
        self.assertEqual(response.json()["database"]["status"], "connected")


class TestUserProfileView(TestCase):
    """Tests for the UserProfileView."""

    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        # Add any necessary user setup here

    def test_get_profile(self):
        """Test getting a user profile."""
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on expected response

    def test_update_profile_valid(self):
        """Test updating a user profile with valid data."""
        data = {
            "email": "new@example.com",
            "profile": {
                "bio": "New bio",
                "location": "New location",
                "website": "https://new-example.com",
            },
        }
        response = self.client.put(
            "/api/profile/", 
            data=data, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on expected response

    def test_update_profile_invalid(self):
        """Test updating a user profile with invalid data."""
        data = {
            "email": "invalid-email",
            "profile": {
                "website": "invalid-url",
            },
        }
        response = self.client.put(
            "/api/profile/", 
            data=data, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        # Add more assertions based on expected response

    def test_update_profile_mixed(self):
        """Test updating a user profile with mixed valid and invalid data."""
        data = {
            "email": "new@example.com",  # Valid
            "profile": {
                "bio": "New bio",  # Valid
                "website": "invalid-url",  # Invalid
            },
        }
        response = self.client.put(
            "/api/profile/", 
            data=data, 
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        # Add more assertions based on expected response
