"""
Tests for the signal handlers in the core module.

This module tests the Django signals defined in pyerp/core/signals.py.
"""

import unittest
from unittest.mock import patch, MagicMock

from django.test import RequestFactory

from pyerp.core.signals import (
    log_user_login,
    log_user_login_failed,
    log_user_logout,
    log_user_changes,
)


class SignalHandlerTests(unittest.TestCase):
    """Tests for the signal handlers."""
    
    def setUp(self):
        """Set up test environment."""
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get('/')
        self.user = MagicMock()
        self.user.username = 'testuser'
    
    @patch('pyerp.core.signals.AuditService.log_login')
    def test_log_user_login(self, mock_log_login):
        """Test that user login is logged."""
        # Simulate signal being sent
        log_user_login(sender=None, request=self.request, user=self.user)
        
        # Verify AuditService was called correctly
        mock_log_login.assert_called_once_with(
            self.user, self.request, success=True
        )
    
    @patch('pyerp.core.signals.AuditService.log_event')
    def test_log_user_login_failed(self, mock_log_event):
        """Test that failed login attempts are logged."""
        credentials = {'username': 'nonexistent'}
        
        # Simulate signal being sent
        log_user_login_failed(
            sender=None, credentials=credentials, request=self.request
        )
        
        # Verify AuditService was called correctly
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args[1]
        self.assertEqual(call_args['event_type'], 'login_failed')
        self.assertIn('nonexistent', call_args['message'])
        self.assertEqual(call_args['request'], self.request)
        self.assertEqual(
            call_args['additional_data']['username_attempted'], 
            'nonexistent'
        )
    
    @patch('pyerp.core.signals.AuditService.log_logout')
    def test_log_user_logout(self, mock_log_logout):
        """Test that user logout is logged."""
        # Simulate signal being sent
        log_user_logout(sender=None, request=self.request, user=self.user)
        
        # Verify AuditService was called correctly
        mock_log_logout.assert_called_once_with(self.user, self.request)
    
    @patch('pyerp.core.signals.AuditService.log_logout')
    def test_log_user_logout_no_user(self, mock_log_logout):
        """Test that logout without a user doesn't cause an error."""
        # Simulate signal being sent with no user
        log_user_logout(sender=None, request=self.request, user=None)
        
        # Verify AuditService was not called
        mock_log_logout.assert_not_called()
    
    @patch('pyerp.core.signals.AuditService.log_event')
    def test_log_user_created(self, mock_log_event):
        """Test that user creation is logged."""
        # Simulate signal being sent for a new user
        log_user_changes(sender=None, instance=self.user, created=True)
        
        # Verify AuditService was called correctly
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args[1]
        self.assertEqual(call_args['event_type'], 'user_created')
        self.assertIn('testuser', call_args['message'])
        self.assertEqual(call_args['obj'], self.user)
    
    @patch('pyerp.core.signals.AuditService.log_event')
    def test_log_user_updated(self, mock_log_event):
        """Test that user updates are logged."""
        # Simulate signal being sent for an updated user
        log_user_changes(sender=None, instance=self.user, created=False)
        
        # Verify AuditService was called correctly
        mock_log_event.assert_called_once()
        call_args = mock_log_event.call_args[1]
        self.assertEqual(call_args['event_type'], 'user_updated')
        self.assertIn('testuser', call_args['message'])
        self.assertEqual(call_args['obj'], self.user) 