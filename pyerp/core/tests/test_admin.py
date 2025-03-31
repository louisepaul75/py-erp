"""
Tests for admin configurations.

This module tests the admin configurations for the core app,
ensuring that all admin classes and functionality work correctly.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from pyerp.core.models import AuditLog, UserPreference, Tag, TaggedItem
from pyerp.core.admin import (
    AuditLogAdmin,
    UserPreferenceAdmin,
    TagAdmin,
    TaggedItemAdmin
)

User = get_user_model()


class MockRequest:
    """Mock request for admin testing."""
    
    def __init__(self, user=None):
        self.user = user


class AdminConfigTests(TestCase):
    """Tests for admin configurations."""
    
    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.audit_log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user
        )
        self.preference = UserPreference.objects.create(
            user=self.user
        )
        self.tag = Tag.objects.create(
            name="Test Tag",
            description="Test tag description"
        )
        self.content_type = ContentType.objects.get_for_model(User)
        self.tagged_item = TaggedItem.objects.create(
            tag=self.tag,
            content_type=self.content_type,
            object_id=self.user.pk
        )
        
        # Create admin instances
        self.audit_log_admin = AuditLogAdmin(AuditLog, self.site)
        self.user_preference_admin = UserPreferenceAdmin(UserPreference, self.site)
        self.tag_admin = TagAdmin(Tag, self.site)
        self.tagged_item_admin = TaggedItemAdmin(TaggedItem, self.site)
        
    def test_audit_log_admin_list_display(self):
        """Test AuditLogAdmin list_display."""
        self.assertIn('event_type', self.audit_log_admin.list_display)
        self.assertIn('timestamp', self.audit_log_admin.list_display)
        self.assertIn('username', self.audit_log_admin.list_display)
        self.assertIn('ip_address', self.audit_log_admin.list_display)
        
    def test_audit_log_admin_search_fields(self):
        """Test AuditLogAdmin search_fields."""
        self.assertIn('username', self.audit_log_admin.search_fields)
        self.assertIn('message', self.audit_log_admin.search_fields)
        self.assertIn('ip_address', self.audit_log_admin.search_fields)
        
    def test_audit_log_admin_list_filter(self):
        """Test AuditLogAdmin list_filter."""
        self.assertIn('event_type', self.audit_log_admin.list_filter)
        self.assertIn('timestamp', self.audit_log_admin.list_filter)
        
    def test_audit_log_admin_readonly_fields(self):
        """Test AuditLogAdmin readonly_fields."""
        self.assertTrue(len(self.audit_log_admin.readonly_fields) > 0)
        self.assertIn('uuid', self.audit_log_admin.readonly_fields)
        self.assertIn('timestamp', self.audit_log_admin.readonly_fields)
        
    def test_user_preference_admin_list_display(self):
        """Test UserPreferenceAdmin list_display."""
        self.assertIn('user', self.user_preference_admin.list_display)
        self.assertIn('created_at', self.user_preference_admin.list_display)
        self.assertIn('updated_at', self.user_preference_admin.list_display)
        
    def test_tag_admin_list_display(self):
        """Test TagAdmin list_display."""
        self.assertIn('name', self.tag_admin.list_display)
        self.assertIn('slug', self.tag_admin.list_display)
        
    def test_tag_admin_prepopulated_fields(self):
        """Test TagAdmin prepopulated_fields."""
        self.assertEqual(self.tag_admin.prepopulated_fields, {'slug': ('name',)})
        
    def test_tag_admin_search_fields(self):
        """Test TagAdmin search_fields."""
        self.assertIn('name', self.tag_admin.search_fields)
        self.assertIn('slug', self.tag_admin.search_fields)
        
    def test_tagged_item_admin_list_display(self):
        """Test TaggedItemAdmin list_display."""
        self.assertIn('tag', self.tagged_item_admin.list_display)
        self.assertIn('content_type', self.tagged_item_admin.list_display)
        self.assertIn('object_id', self.tagged_item_admin.list_display)
        
    def test_tagged_item_admin_list_filter(self):
        """Test TaggedItemAdmin list_filter."""
        self.assertIn('tag', self.tagged_item_admin.list_filter)
        self.assertIn('content_type', self.tagged_item_admin.list_filter)
        
    def test_admin_changelist_view(self):
        """Test admin changelist views."""
        response = self.client.get(reverse('admin:core_auditlog_changelist'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:core_userpreference_changelist'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:core_tag_changelist'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:core_taggeditem_changelist'))
        self.assertEqual(response.status_code, 200)
        
    def test_admin_change_view(self):
        """Test admin change views."""
        response = self.client.get(
            reverse('admin:core_auditlog_change', args=[self.audit_log.pk])
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            reverse('admin:core_userpreference_change', args=[self.preference.pk])
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            reverse('admin:core_tag_change', args=[self.tag.pk])
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            reverse('admin:core_taggeditem_change', args=[self.tagged_item.pk])
        )
        self.assertEqual(response.status_code, 200)
        
    def test_admin_add_view(self):
        """Test admin add views."""
        response = self.client.get(reverse('admin:core_tag_add'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('admin:core_taggeditem_add'))
        self.assertEqual(response.status_code, 200)
        
    def test_audit_log_admin_has_delete_permission(self):
        """Test AuditLogAdmin delete permission."""
        # AuditLog should not be deletable
        mock_request = MockRequest(user=self.superuser)
        
        # Even superusers shouldn't be able to delete audit logs
        self.assertFalse(
            self.audit_log_admin.has_delete_permission(mock_request, self.audit_log)
        )
        
    def test_audit_log_admin_has_change_permission(self):
        """Test AuditLogAdmin change permission."""
        # AuditLog should not be changeable
        mock_request = MockRequest(user=self.superuser)
        
        # Even superusers shouldn't be able to change audit logs
        self.assertFalse(
            self.audit_log_admin.has_change_permission(mock_request, self.audit_log)
        )
        
    def test_tag_admin_save_model(self):
        """Test TagAdmin save_model method."""
        # Create a new tag via admin
        response = self.client.post(
            reverse('admin:core_tag_add'),
            {
                'name': 'Admin Created Tag',
                'description': 'Created via admin'
            }
        )
        
        # Check tag was created
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Tag.objects.filter(name='Admin Created Tag').exists())
        
        # Verify slug was auto-generated
        tag = Tag.objects.get(name='Admin Created Tag')
        self.assertEqual(tag.slug, 'admin-created-tag')
        
    def test_admin_filters(self):
        """Test admin filters."""
        # Test AuditLog event_type filter
        response = self.client.get(
            reverse('admin:core_auditlog_changelist') + 
            f'?event_type={AuditLog.EventType.LOGIN}'
        )
        self.assertEqual(response.status_code, 200)
        
        # Test Tag created_at filter
        response = self.client.get(
            reverse('admin:core_tag_changelist') + 
            '?created_at__gte=2023-01-01'
        )
        self.assertEqual(response.status_code, 200)
        
    def test_admin_actions(self):
        """Test admin actions."""
        # Test Tag bulk delete
        tag2 = Tag.objects.create(name='Another Tag')
        
        response = self.client.post(
            reverse('admin:core_tag_changelist'),
            {
                'action': 'delete_selected',
                '_selected_action': [self.tag.pk, tag2.pk]
            }
        )
        self.assertEqual(response.status_code, 200)  # Should show confirmation page 