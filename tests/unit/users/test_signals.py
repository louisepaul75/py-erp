"""
Unit tests for the users app signals.

Test cases for signal handlers that respond to user events.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from unittest.mock import patch

from users.signals import (
    handle_user_logged_in,
    handle_user_logged_out,
    handle_user_login_failed,
    handle_password_change,
    handle_user_save,
)

User = get_user_model()


class UserSignalsTest(TestCase):
    """Test cases for user-related signal handlers."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpassword"
        )
        self.request = self.factory.get("/fake-url")
        self.request.user = self.user

    @patch("users.signals.logger")
    def test_handle_user_logged_in(self, mock_logger):
        """Test the user_logged_in signal handler."""
        # Trigger the signal handler
        handle_user_logged_in(sender=User, request=self.request, user=self.user)

        # Check that logger.info was called with the right message
        mock_logger.info.assert_called_with(
            f"User {self.user.username} logged in successfully"
        )

    @patch("users.signals.logger")
    def test_handle_user_logged_out(self, mock_logger):
        """Test the user_logged_out signal handler."""
        # Trigger the signal handler
        handle_user_logged_out(sender=User, request=self.request, user=self.user)

        # Check that logger.info was called with the right message
        mock_logger.info.assert_called_with(f"User {self.user.username} logged out")

        # Test with no user (should not log anything)
        mock_logger.reset_mock()
        handle_user_logged_out(sender=User, request=self.request, user=None)
        mock_logger.info.assert_not_called()

    @patch("users.signals.logger")
    def test_handle_user_login_failed(self, mock_logger):
        """Test the user_login_failed signal handler."""
        # Trigger the signal handler
        credentials = {"username": "baduser"}
        handle_user_login_failed(
            sender=User, credentials=credentials, request=self.request
        )

        # Check that logger.warning was called with the right message
        mock_logger.warning.assert_called_with("Failed login attempt for user baduser")

        # Test with missing username
        mock_logger.reset_mock()
        handle_user_login_failed(sender=User, credentials={}, request=self.request)
        mock_logger.warning.assert_called_with("Failed login attempt for user unknown")

    @patch("users.signals.logger")
    def test_handle_password_change(self, mock_logger):
        """Test the password change handler."""
        # Save the original password
        original_password = self.user.password

        # Change the password
        self.user.set_password("newpassword")

        # Manually trigger the pre_save signal handler
        handle_password_change(sender=User, instance=self.user)

        # Check that the last_password_change was updated
        self.assertIsNotNone(self.user.last_password_change)

        # Check that the logger was called
        mock_logger.info.assert_called_with(
            f"Password changed for user {self.user.username}"
        )

        # Test with a new user (no existing record)
        mock_logger.reset_mock()
        new_user = User(username="newuser", email="new@example.com")
        handle_password_change(sender=User, instance=new_user)

        # Should not log anything for new users
        mock_logger.info.assert_not_called()

    @patch("users.signals.logger")
    def test_handle_user_save(self, mock_logger):
        """Test the post-save handler for user."""
        # Test user creation
        new_user = User(username="brandnew", email="brandnew@example.com")
        handle_user_save(sender=User, instance=new_user, created=True)
        mock_logger.info.assert_called_with(f"New user created: {new_user.username}")

        # Test user update
        mock_logger.reset_mock()
        handle_user_save(sender=User, instance=self.user, created=False)
        mock_logger.info.assert_called_with(f"User updated: {self.user.username}")
