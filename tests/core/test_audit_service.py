"""
Tests for the AuditService in core services.
"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory

from pyerp.core.models import AuditLog
from pyerp.core.services import AuditService


User = get_user_model()


class TestAuditService(TestCase):
    """
    Test suite for the AuditService which handles security audit logging.
    """

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a sample request
        self.sample_request = self.factory.get('/sample-path')
        self.sample_request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        self.sample_request.META['REMOTE_ADDR'] = '127.0.0.1'
        self.sample_request.user = self.user

    def test_log_event_basic(self):
        """Test basic event logging without additional context."""
        # Test creating a basic log entry
        event_type = AuditLog.EventType.SYSTEM_ERROR
        message = "Test system error"
        
        log_entry = AuditService.log_event(
            event_type=event_type,
            message=message,
            user=self.user
        )
        
        # Verify log was created
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.event_type, event_type)
        self.assertEqual(log_entry.message, message)
        self.assertEqual(log_entry.user, self.user)
        self.assertEqual(log_entry.username, self.user.username)
        
        # Verify retrieval from database
        db_log = AuditLog.objects.get(pk=log_entry.pk)
        self.assertEqual(db_log.event_type, event_type)
        self.assertEqual(db_log.user, self.user)

    def test_log_event_with_request(self):
        """Test event logging with HTTP request context."""
        # Test with request object to capture IP and user agent
        event_type = AuditLog.EventType.LOGIN
        message = "Test login event"
        
        log_entry = AuditService.log_event(
            event_type=event_type,
            message=message,
            request=self.sample_request
        )
        
        # Verify request info was captured
        self.assertEqual(log_entry.event_type, event_type)
        self.assertEqual(log_entry.user, self.user)  # Should get user from request
        self.assertEqual(log_entry.ip_address, '127.0.0.1')
        self.assertEqual(log_entry.user_agent, 'Test User Agent')

    @patch('pyerp.core.services.logger')
    def test_log_event_with_logger(self, mock_logger):
        """Test that events are also sent to the security logger."""
        event_type = AuditLog.EventType.DATA_ACCESS
        message = "Test data access log"
        
        AuditService.log_event(
            event_type=event_type,
            message=message,
            user=self.user,
            request=self.sample_request
        )
        
        # Verify logger was called with appropriate info
        mock_logger.info.assert_called_once()
        log_call_args = mock_logger.info.call_args[0]
        self.assertIn(event_type, log_call_args[0])
        self.assertIn(message, log_call_args[0])
        
        # Verify extra data was included
        log_extra = mock_logger.info.call_args[1]['extra']
        self.assertEqual(log_extra['event_type'], event_type)
        self.assertEqual(log_extra['username'], self.user.username)

    def test_log_event_with_related_object(self):
        """Test event logging with a related model object."""
        # Use User as a test related object
        related_user = User.objects.create_user(
            username='related_user',
            email='related@example.com',
            password='password123'
        )
        
        event_type = AuditLog.EventType.USER_CREATED
        message = "Test user created event"
        
        log_entry = AuditService.log_event(
            event_type=event_type,
            message=message,
            user=self.user,
            obj=related_user
        )
        
        # Verify related object was captured
        content_type = ContentType.objects.get_for_model(User)
        self.assertEqual(log_entry.content_type, content_type)
        self.assertEqual(log_entry.object_id, str(related_user.pk))

    def test_log_event_with_additional_data(self):
        """Test event logging with additional JSON data."""
        event_type = AuditLog.EventType.DATA_CHANGE
        message = "Test data change with extra info"
        additional_data = {
            'changed_fields': ['name', 'description'],
            'old_values': {'name': 'Old Name', 'description': 'Old description'},
            'new_values': {'name': 'New Name', 'description': 'New description'}
        }
        
        log_entry = AuditService.log_event(
            event_type=event_type,
            message=message,
            user=self.user,
            additional_data=additional_data
        )
        
        # Verify additional data was stored
        self.assertEqual(log_entry.additional_data, additional_data)
        
        # Verify data can be retrieved and used
        self.assertEqual(
            log_entry.additional_data['changed_fields'], 
            ['name', 'description']
        )
        self.assertEqual(
            log_entry.additional_data['old_values']['name'], 
            'Old Name'
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_login(self, mock_log_event):
        """Test login event logging."""
        # Test successful login
        AuditService.log_login(self.user, self.sample_request, success=True)
        mock_log_event.assert_called_with(
            AuditLog.EventType.LOGIN,
            "User login successful",
            self.user,
            self.sample_request
        )
        
        # Test failed login
        mock_log_event.reset_mock()
        AuditService.log_login(self.user, self.sample_request, success=False)
        mock_log_event.assert_called_with(
            AuditLog.EventType.LOGIN_FAILED,
            "User login failed",
            self.user,
            self.sample_request
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_logout(self, mock_log_event):
        """Test logout event logging."""
        AuditService.log_logout(self.user, self.sample_request)
        mock_log_event.assert_called_with(
            AuditLog.EventType.LOGOUT,
            "User logged out",
            self.user,
            self.sample_request
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_password_change(self, mock_log_event):
        """Test password change event logging."""
        AuditService.log_password_change(self.user, self.sample_request)
        mock_log_event.assert_called_with(
            AuditLog.EventType.PASSWORD_CHANGE,
            "User changed password",
            self.user,
            self.sample_request
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_password_reset(self, mock_log_event):
        """Test password reset event logging."""
        AuditService.log_password_reset(self.user, self.sample_request)
        mock_log_event.assert_called_with(
            AuditLog.EventType.PASSWORD_RESET,
            "User reset password",
            self.user,
            self.sample_request
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_user_created(self, mock_log_event):
        """Test user creation event logging."""
        created_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='password123'
        )
        
        AuditService.log_user_created(created_user, self.user, self.sample_request)
        mock_log_event.assert_called_with(
            AuditLog.EventType.USER_CREATED,
            f"User '{created_user.username}' created",
            self.user,
            self.sample_request,
            created_user
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_user_updated(self, mock_log_event):
        """Test user update event logging."""
        updated_user = User.objects.create_user(
            username='updateduser',
            email='updated@example.com',
            password='password123'
        )
        changed_fields = ['email', 'first_name']
        
        AuditService.log_user_updated(
            updated_user,
            self.user,
            self.sample_request,
            changed_fields
        )
        
        mock_log_event.assert_called_with(
            AuditLog.EventType.USER_UPDATED,
            f"User '{updated_user.username}' updated (email, first_name)",
            self.user,
            self.sample_request,
            updated_user,
            {"changed_fields": changed_fields}
        )
        
        # Test without specified fields
        mock_log_event.reset_mock()
        AuditService.log_user_updated(
            updated_user,
            self.user,
            self.sample_request
        )
        
        mock_log_event.assert_called_with(
            AuditLog.EventType.USER_UPDATED,
            f"User '{updated_user.username}' updated (fields)",
            self.user,
            self.sample_request,
            updated_user,
            {"changed_fields": None}
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_permission_change(self, mock_log_event):
        """Test permission change event logging."""
        target_user = User.objects.create_user(
            username='permissionuser',
            email='permission@example.com',
            password='password123'
        )
        
        added = ['add_product', 'change_product']
        removed = ['delete_product']
        
        AuditService.log_permission_change(
            self.user,
            target_user,
            self.sample_request,
            added=added,
            removed=removed
        )
        
        mock_log_event.assert_called_with(
            AuditLog.EventType.PERMISSION_CHANGE,
            f"Permissions changed for '{target_user.username}'",
            self.user,
            self.sample_request,
            target_user,
            {
                'permissions': None,
                'added': added,
                'removed': removed,
            }
        )

    @patch('pyerp.core.services.AuditService.log_event')
    def test_log_data_access(self, mock_log_event):
        """Test data access event logging."""
        # We'll use User as a sample model for data access
        accessed_user = User.objects.create_user(
            username='accesseduser',
            email='accessed@example.com',
            password='password123'
        )
        
        AuditService.log_data_access(
            self.user,
            accessed_user,
            self.sample_request,
            action="viewed"
        )
        
        mock_log_event.assert_called_with(
            AuditLog.EventType.DATA_ACCESS,
            f"User ({accessed_user.pk}) accessed viewed",
            self.user,
            self.sample_request,
            accessed_user
        )

    def test_get_client_ip_with_x_forwarded_for(self):
        """Test IP address extraction with X-Forwarded-For header."""
        request = self.factory.get('/sample-path')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = AuditService._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')

    def test_get_client_ip_with_remote_addr(self):
        """Test IP address extraction with REMOTE_ADDR."""
        request = self.factory.get('/sample-path')
        request.META['REMOTE_ADDR'] = '192.168.1.2'
        
        ip = AuditService._get_client_ip(request)
        self.assertEqual(ip, '192.168.1.2')

    @patch('pyerp.core.services.ContentType.objects.get_for_model')
    def test_log_event_handles_exception(self, mock_get_for_model):
        """Test that log_event gracefully handles exceptions."""
        # Simulate an exception in the logging process
        mock_get_for_model.side_effect = Exception("Simulated error")
        
        with patch('pyerp.core.services.logger') as mock_logger:
            result = AuditService.log_event(
                event_type=AuditLog.EventType.SYSTEM_ERROR,
                message="This will cause an error",
                user=self.user,
                obj=self.user  # This will trigger the ContentType lookup
            )
            
            # Verify method returns None on error
            self.assertIsNone(result)
            
            # Verify error was logged
            mock_logger.error.assert_called_once()
            error_msg = mock_logger.error.call_args[0][0]
            self.assertIn("Error creating audit log", error_msg) 