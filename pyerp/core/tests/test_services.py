"""
Tests for core services.

This module tests the functionality of the service classes defined in pyerp/core/services.py,
ensuring that service methods work correctly.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from pyerp.core.services import AuditService
from pyerp.core.models import AuditLog, UserPreference

User = get_user_model()


class AuditServiceTests(TestCase):
    """Tests for the AuditService class."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.factory = RequestFactory()
        
    def test_log_event_basic(self):
        """Test the basic event logging functionality."""
        event_type = AuditLog.EventType.LOGIN
        message = "User logged in"
        
        log = AuditService.log_event(event_type, message, self.user)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, event_type)
        self.assertEqual(log.message, message)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, self.user.username)
        self.assertIsNone(log.ip_address)
        self.assertEqual(log.user_agent, "")
        self.assertIsNone(log.content_type)
        self.assertEqual(log.object_id, "")
        
    def test_log_event_with_request(self):
        """Test logging an event with request data."""
        request = self.factory.get('/test/')
        request.user = self.user
        request.META['HTTP_USER_AGENT'] = 'Test Browser'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        log = AuditService.log_event(
            AuditLog.EventType.DATA_ACCESS,
            "Accessed sensitive data",
            request=request
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, self.user.username)
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_agent, 'Test Browser')
        
    def test_log_event_with_related_object(self):
        """Test logging an event with a related object."""
        preference = UserPreference.objects.create(user=self.user)
        
        log = AuditService.log_event(
            AuditLog.EventType.DATA_CHANGE,
            "User preference updated",
            self.user,
            obj=preference,
            additional_data={"changed_fields": ["dashboard_config"]}
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.content_type, ContentType.objects.get_for_model(preference))
        self.assertEqual(log.object_id, str(preference.pk))
        self.assertEqual(log.additional_data, {"changed_fields": ["dashboard_config"]})
        
    @patch('pyerp.core.services.AuditLog.objects.create')
    @patch('pyerp.core.services.logger')
    def test_log_event_exception_handling(self, mock_logger, mock_create):
        """Test that exceptions during log creation are handled gracefully."""
        # Make the create method raise an exception
        mock_create.side_effect = Exception("Test exception")
        
        log = AuditService.log_event(
            AuditLog.EventType.SYSTEM_ERROR,
            "Test error",
            self.user
        )
        
        # Verify that None is returned and the error is logged
        self.assertIsNone(log)
        mock_logger.error.assert_called_once()
        
    def test_log_login_success(self):
        """Test logging a successful login."""
        request = self.factory.get('/login/')
        
        log = AuditService.log_login(self.user, request, success=True)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.LOGIN)
        self.assertIn("successful", log.message)
        
    def test_log_login_failure(self):
        """Test logging a failed login."""
        request = self.factory.get('/login/')
        
        log = AuditService.log_login(self.user, request, success=False)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.LOGIN_FAILED)
        self.assertIn("failed", log.message)
        
    def test_log_logout(self):
        """Test logging a logout."""
        request = self.factory.get('/logout/')
        
        log = AuditService.log_logout(self.user, request)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.LOGOUT)
        self.assertIn("logged out", log.message.lower())
        
    def test_log_password_change(self):
        """Test logging a password change."""
        request = self.factory.post('/password/change/')
        
        log = AuditService.log_password_change(self.user, request)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.PASSWORD_CHANGE)
        self.assertIn("changed password", log.message.lower())
        
    def test_log_password_reset(self):
        """Test logging a password reset."""
        request = self.factory.post('/password/reset/')
        
        log = AuditService.log_password_reset(self.user, request)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.PASSWORD_RESET)
        self.assertIn("reset password", log.message.lower())
        
    def test_log_user_created(self):
        """Test logging user creation."""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        
        log = AuditService.log_user_created(new_user, self.user)
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.USER_CREATED)
        self.assertIn(new_user.username, log.message)
        self.assertEqual(log.user, self.user)  # Creator
        self.assertEqual(log.content_object, new_user)  # Created user
        
    def test_log_user_updated(self):
        """Test logging user updates."""
        changed_fields = ["email", "first_name"]
        
        log = AuditService.log_user_updated(
            self.user,
            self.user,  # Self-update
            changed_fields=changed_fields
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.USER_UPDATED)
        self.assertIn(self.user.username, log.message)
        self.assertEqual(log.additional_data, {"changed_fields": changed_fields})
        
    def test_log_permission_change(self):
        """Test logging permission changes."""
        target_user = User.objects.create_user(
            username='targetuser',
            email='target@example.com',
            password='password123'
        )
        permissions = {
            "added": ["can_view_reports", "can_edit_products"],
            "removed": ["can_delete_users"]
        }
        
        log = AuditService.log_permission_change(
            self.user,
            target_user,
            permissions=permissions["added"] + permissions["removed"],
            added=permissions["added"],
            removed=permissions["removed"]
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.PERMISSION_CHANGE)
        self.assertIn(target_user.username, log.message)
        self.assertEqual(log.additional_data["added"], permissions["added"])
        self.assertEqual(log.additional_data["removed"], permissions["removed"])
        
    def test_log_data_access(self):
        """Test logging data access."""
        preference = UserPreference.objects.create(user=self.user)
        
        log = AuditService.log_data_access(
            self.user,
            preference,
            action="viewed"
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.event_type, AuditLog.EventType.DATA_ACCESS)
        model_name = preference._meta.model_name.capitalize()
        self.assertIn(model_name, log.message)
        self.assertIn("viewed", log.message)
        
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test extracting client IP with X-Forwarded-For header."""
        request = self.factory.get('/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = AuditService._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
    def test_get_client_ip_without_x_forwarded_for(self):
        """Test extracting client IP without X-Forwarded-For header."""
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '10.0.0.1'
        
        ip = AuditService._get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1') 