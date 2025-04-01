"""
Tests for core models.

This module tests the functionality of the models defined in pyerp/core/models.py,
ensuring that model validation, methods, and relationships work correctly.
"""

import uuid
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

from pyerp.core.models import AuditLog, UserPreference, Tag, TaggedItem

User = get_user_model()


class AuditLogTests(TestCase):
    """Tests for the AuditLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
    def test_create_audit_log(self):
        """Test creating an audit log entry."""
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user,
            ip_address="127.0.0.1",
            user_agent="Test Browser"
        )
        
        self.assertEqual(log.event_type, AuditLog.EventType.LOGIN)
        self.assertEqual(log.message, "User logged in")
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.username, self.user.username)
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.user_agent, "Test Browser")
        self.assertIsNone(log.content_type)
        self.assertEqual(log.object_id, "")
        self.assertIsNone(log.additional_data)
        self.assertIsNotNone(log.timestamp)
        self.assertIsNotNone(log.uuid)
        
    def test_create_audit_log_with_related_object(self):
        """Test creating an audit log with a related object."""
        # Use UserPreference as the related object for this test
        preference = UserPreference.objects.create(user=self.user)
        
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.DATA_CHANGE,
            message="User preference updated",
            user=self.user,
            content_type=ContentType.objects.get_for_model(preference),
            object_id=str(preference.pk),
            additional_data={"changed_fields": ["dashboard_config"]}
        )
        
        self.assertEqual(log.event_type, AuditLog.EventType.DATA_CHANGE)
        self.assertEqual(log.content_type, ContentType.objects.get_for_model(preference))
        self.assertEqual(log.object_id, str(preference.pk))
        self.assertEqual(log.additional_data, {"changed_fields": ["dashboard_config"]})
        self.assertEqual(log.content_object, preference)
        
    def test_audit_log_str_method(self):
        """Test the string representation of an audit log."""
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user
        )
        
        # Get the event type display value directly to avoid translation discrepancies
        expected_event = log.get_event_type_display()
        expected_str = f"{expected_event} - {self.user.username} - {log.timestamp}"
        self.assertEqual(str(log), expected_str)
        
        # Test without a username
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.SYSTEM_ERROR,
            message="System error occurred",
            username=""
        )
        
        # Get the event type display value directly
        expected_event = log.get_event_type_display()
        expected_str = f"{expected_event} - {log.timestamp}"
        self.assertEqual(str(log), expected_str)
        
    def test_auto_set_username(self):
        """Test that username is automatically set from user."""
        log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user,
            username=""  # Explicitly set empty to test auto-population
        )
        
        self.assertEqual(log.username, self.user.username)


class UserPreferenceTests(TestCase):
    """Tests for the UserPreference model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.preference = UserPreference.objects.create(user=self.user)
        
    def test_create_user_preference(self):
        """Test creating a user preference."""
        self.assertEqual(self.preference.user, self.user)
        self.assertEqual(self.preference.dashboard_config, {})
        self.assertIsNotNone(self.preference.created_at)
        self.assertIsNotNone(self.preference.updated_at)
        
    def test_user_preference_str_method(self):
        """Test the string representation of a user preference."""
        expected_str = f"Preferences for {self.user.username}"
        self.assertEqual(str(self.preference), expected_str)
        
    def test_get_default_dashboard_modules(self):
        """Test getting default dashboard modules."""
        modules = self.preference.get_dashboard_modules()
        self.assertIsInstance(modules, list)
        self.assertTrue(len(modules) > 0)
        self.assertIn('id', modules[0])
        self.assertIn('title', modules[0])
        self.assertIn('type', modules[0])
        
    def test_get_default_dashboard_grid_layout(self):
        """Test getting default dashboard grid layout."""
        layout = self.preference.get_dashboard_grid_layout()
        self.assertIsInstance(layout, dict)
        self.assertIn('lg', layout)
        self.assertIn('md', layout)
        self.assertIn('sm', layout)
        
    def test_save_dashboard_config(self):
        """Test saving dashboard configuration."""
        new_modules = [{"id": "test-module", "title": "Test Module"}]
        new_layout = {"lg": [{"i": "test-module", "x": 0, "y": 0, "w": 12, "h": 12}]}
        
        # Save modules only
        self.preference.save_dashboard_config(modules=new_modules)
        self.assertEqual(self.preference.dashboard_config['modules'], new_modules)
        self.assertNotIn('grid_layout', self.preference.dashboard_config)
        
        # Save layout only
        self.preference.save_dashboard_config(grid_layout=new_layout)
        self.assertEqual(self.preference.dashboard_config['modules'], new_modules)
        self.assertEqual(self.preference.dashboard_config['grid_layout'], new_layout)
        
        # Save both
        updated_modules = [{"id": "updated-module", "title": "Updated Module"}]
        self.preference.save_dashboard_config(
            modules=updated_modules,
            grid_layout=new_layout
        )
        self.assertEqual(self.preference.dashboard_config['modules'], updated_modules)
        self.assertEqual(self.preference.dashboard_config['grid_layout'], new_layout)


class TagTests(TestCase):
    """Tests for the Tag model."""
    
    def test_create_tag(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            name="Test Tag",
            description="Test tag description"
        )
        
        self.assertEqual(tag.name, "Test Tag")
        self.assertEqual(tag.slug, "test-tag")
        self.assertEqual(tag.description, "Test tag description")
        self.assertIsNotNone(tag.created_at)
        self.assertIsNotNone(tag.updated_at)
        
    def test_tag_str_method(self):
        """Test the string representation of a tag."""
        tag = Tag.objects.create(name="Test Tag")
        self.assertEqual(str(tag), "Test Tag")
        
    def test_auto_slug_generation(self):
        """Test automatic slug generation."""
        tag = Tag.objects.create(name="Special Characters & Test!")
        self.assertEqual(tag.slug, "special-characters-test")
        
    def test_custom_slug(self):
        """Test using a custom slug."""
        tag = Tag.objects.create(
            name="Test Tag",
            slug="custom-slug"
        )
        self.assertEqual(tag.slug, "custom-slug")
        
    def test_slug_uniqueness(self):
        """Test that slugs are unique."""
        Tag.objects.create(name="Test Tag")
        
        # Creating a tag with the same name should generate a different slug
        # or fail with an IntegrityError. Django's behavior depends on the DB.
        # For this test, we'll assume it fails with an IntegrityError
        with self.assertRaises(Exception):
            Tag.objects.create(name="Test Tag")


class TaggedItemTests(TestCase):
    """Tests for the TaggedItem model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.tag = Tag.objects.create(name="Test Tag")
        
    def test_create_tagged_item(self):
        """Test creating a tagged item."""
        content_type = ContentType.objects.get_for_model(User)
        tagged_item = TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=self.user.pk
        )
        
        self.assertEqual(tagged_item.tag, self.tag)
        self.assertEqual(tagged_item.content_type, content_type)
        self.assertEqual(tagged_item.object_id, self.user.pk)
        self.assertEqual(tagged_item.content_object, self.user)
        self.assertIsNotNone(tagged_item.created_at)
        
    def test_tagged_item_str_method(self):
        """Test the string representation of a tagged item."""
        content_type = ContentType.objects.get_for_model(User)
        tagged_item = TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=self.user.pk
        )
        
        expected_str = f"'Test Tag' tag on {self.user}"
        self.assertEqual(str(tagged_item), expected_str)
        
    def test_unique_together_constraint(self):
        """Test the unique_together constraint."""
        content_type = ContentType.objects.get_for_model(User)
        TaggedItem.objects.create(
            tag=self.tag,
            content_type=content_type,
            object_id=self.user.pk
        )
        
        # Attempting to create the same tag for the same object should fail
        with self.assertRaises(Exception):
            TaggedItem.objects.create(
                tag=self.tag,
                content_type=content_type,
                object_id=self.user.pk
            ) 