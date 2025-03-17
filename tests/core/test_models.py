"""
Tests for core models in the pyERP system.
"""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django.utils import timezone

from pyerp.core.models import AuditLog


User = get_user_model()


class TestAuditLogModel(TransactionTestCase):
    """
    Tests for the AuditLog model which stores security and audit events.
    """

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # Create a basic audit log entry
        self.audit_log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Test User Agent'
        )

    def test_audit_log_creation(self):
        """Test basic audit log creation and retrieval."""
        # Verify the audit log was created
        self.assertEqual(AuditLog.objects.count(), 1)
        
        # Check that the record has the correct data
        log = AuditLog.objects.first()
        self.assertEqual(log.event_type, AuditLog.EventType.LOGIN)
        self.assertEqual(log.message, "User logged in")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, self.user.username)
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.user_agent, 'Test User Agent')
        
        # Check timestamp is recent
        now = timezone.now()
        time_diff = now - log.timestamp
        self.assertLess(time_diff.total_seconds(), 10)  # Within 10 seconds
        
        # Verify UUID was created
        self.assertIsNotNone(log.uuid)

    def test_audit_log_str_method(self):
        """Test the string representation of AuditLog objects."""
        # With username
        log_with_user = self.audit_log
        expected_str = (
            f"{log_with_user.get_event_type_display()} - "
            f"{log_with_user.username} - {log_with_user.timestamp}"
        )
        self.assertEqual(str(log_with_user), expected_str)
        
        # Without username
        log_no_user = AuditLog.objects.create(
            event_type=AuditLog.EventType.SYSTEM_ERROR,
            message="System error occurred"
        )
        expected_str = (
            f"{log_no_user.get_event_type_display()} - "
            f"{log_no_user.timestamp}"
        )
        self.assertEqual(str(log_no_user), expected_str)

    def test_username_auto_population(self):
        """Test that username is automatically populated from user."""
        # Create log with user but no username
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User login test",
            user=self.user
        )
        
        # Verify username was auto-populated
        self.assertEqual(log.username, self.user.username)
        
        # Manually specified username should be preserved
        log_with_manual_username = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User login test",
            user=self.user,
            username="specified_username"
        )
        self.assertEqual(
            log_with_manual_username.username,
            "specified_username"
        )

    def test_related_object_tracking(self):
        """Test that related objects are properly tracked."""
        # Create related object test
        related_user = User.objects.create_user(
            username='related_user',
            email='related@example.com',
            password='password123'
        )
        
        # Create log with related object
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.USER_CREATED,
            message=f"User {related_user.username} created",
            user=self.user,
            content_type=ContentType.objects.get_for_model(User),
            object_id=str(related_user.pk)
        )
        
        # Verify related object is correctly linked
        content_type = ContentType.objects.get_for_model(User)
        self.assertEqual(log.content_type, content_type)
        self.assertEqual(log.object_id, str(related_user.pk))
        self.assertEqual(log.content_object, related_user)

    def test_additional_data_storage(self):
        """Test storage and retrieval of additional JSON data."""
        # Create log with additional data
        test_data = {
            'action': 'update',
            'fields_changed': ['name', 'email'],
            'metadata': {
                'source': 'admin interface',
                'session_id': '12345'
            }
        }
        
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.DATA_CHANGE,
            message="Data was updated",
            user=self.user,
            additional_data=test_data
        )
        
        # Retrieve from DB to ensure it was stored
        retrieved_log = AuditLog.objects.get(pk=log.pk)
        
        # Verify data structure was preserved
        self.assertEqual(retrieved_log.additional_data, test_data)
        self.assertEqual(
            retrieved_log.additional_data['fields_changed'],
            ['name', 'email']
        )
        self.assertEqual(
            retrieved_log.additional_data['metadata']['source'],
            'admin interface'
        )

    def test_event_type_choices(self):
        """Test that all EventType choices are working properly."""
        # Test a selection of event types
        event_types = [
            AuditLog.EventType.LOGIN,
            AuditLog.EventType.LOGOUT,
            AuditLog.EventType.PASSWORD_CHANGE,
            AuditLog.EventType.USER_CREATED,
            AuditLog.EventType.DATA_ACCESS,
            AuditLog.EventType.SYSTEM_ERROR
        ]
        
        for event_type in event_types:
            # Delete any existing logs to ensure clean state
            AuditLog.objects.filter(event_type=event_type).delete()
            
            log = AuditLog.objects.create(
                event_type=event_type,
                message=f"Test for {event_type}"
            )
            self.assertEqual(log.event_type, event_type)
            
            # Verify the display value is non-empty
            self.assertTrue(log.get_event_type_display())
            
            # Verify retrieval works
            self.assertEqual(
                AuditLog.objects.filter(event_type=event_type).count(),
                1
            ) 