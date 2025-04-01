"""
Tests for API serializers.

This module tests the functionality of API serializers in the core app,
ensuring that they correctly serialize and deserialize data.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APIRequestFactory

from pyerp.core.models import AuditLog, UserPreference, Tag, TaggedItem
from users.serializers import UserSerializer
from pyerp.core.serializers import (
    AuditLogSerializer,
    UserPreferenceSerializer,
    TagSerializer,
    TaggedItemSerializer
)

User = get_user_model()


class UserSerializerTests(TestCase):
    """Tests for UserSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        self.serializer = UserSerializer(instance=self.user)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertIn('email', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertNotIn('password', data)  # Password should not be included
        
    def test_username_field_content(self):
        """Test that the username field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['username'], 'testuser')
        
    def test_email_field_content(self):
        """Test that the email field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['email'], 'test@example.com')
        
    def test_user_deserialization(self):
        """Test deserializing user data."""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('newpassword123'))
        
    def test_user_update(self):
        """Test updating user data."""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        serializer = UserSerializer(instance=self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.username, 'testuser')  # Unchanged
        self.assertEqual(updated_user.email, 'test@example.com')  # Unchanged
        
    def test_username_uniqueness(self):
        """Test that usernames must be unique."""
        data = {
            'username': 'testuser',  # Already exists
            'email': 'another@example.com',
            'password': 'password123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)
        
    def test_email_validation(self):
        """Test email validation."""
        data = {
            'username': 'emailuser',
            'email': 'invalid-email',  # Invalid email
            'password': 'password123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class AuditLogSerializerTests(TestCase):
    """Tests for AuditLogSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.audit_log = AuditLog.objects.create(
            event_type=AuditLog.EventType.LOGIN,
            message="User logged in",
            user=self.user,
            ip_address="127.0.0.1",
            user_agent="Test Browser",
            additional_data={"browser": "Chrome", "os": "Windows"}
        )
        self.serializer = AuditLogSerializer(instance=self.audit_log)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('timestamp', data)
        self.assertIn('event_type', data)
        self.assertIn('message', data)
        self.assertIn('username', data)
        self.assertIn('ip_address', data)
        self.assertIn('user_agent', data)
        self.assertIn('additional_data', data)
        self.assertIn('uuid', data)
        
    def test_event_type_field_content(self):
        """Test that the event_type field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['event_type'], AuditLog.EventType.LOGIN)
        
    def test_username_field_content(self):
        """Test that the username field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['username'], 'testuser')
        
    def test_additional_data_field_content(self):
        """Test that the additional_data field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['additional_data'], {"browser": "Chrome", "os": "Windows"})
        
    def test_ip_address_field_content(self):
        """Test that the ip_address field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['ip_address'], '127.0.0.1')
        
    def test_audit_log_deserialization(self):
        """Test deserializing audit log data."""
        data = {
            'event_type': AuditLog.EventType.DATA_ACCESS,
            'message': 'User accessed sensitive data',
            'username': 'testuser',
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'additional_data': {'resource': 'customer_data', 'action': 'view'}
        }
        serializer = AuditLogSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        audit_log = serializer.save()
        self.assertEqual(audit_log.event_type, AuditLog.EventType.DATA_ACCESS)
        self.assertEqual(audit_log.message, 'User accessed sensitive data')
        self.assertEqual(audit_log.username, 'testuser')
        self.assertEqual(audit_log.ip_address, '192.168.1.1')
        self.assertEqual(audit_log.user_agent, 'Mozilla/5.0')
        self.assertEqual(
            audit_log.additional_data, 
            {'resource': 'customer_data', 'action': 'view'}
        )


class UserPreferenceSerializerTests(TestCase):
    """Tests for UserPreferenceSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.preference = UserPreference.objects.create(
            user=self.user,
            dashboard_config={
                'modules': [
                    {'id': 'test-module', 'title': 'Test Module'}
                ],
                'grid_layout': {
                    'lg': [{'i': 'test-module', 'x': 0, 'y': 0, 'w': 12, 'h': 12}]
                }
            }
        )
        self.serializer = UserPreferenceSerializer(instance=self.preference)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('dashboard_config', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        
    def test_user_field_content(self):
        """Test that the user field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['user'], self.user.id)
        
    def test_dashboard_config_field_content(self):
        """Test that the dashboard_config field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['dashboard_config']['modules'][0]['id'], 'test-module')
        self.assertEqual(data['dashboard_config']['modules'][0]['title'], 'Test Module')
        self.assertEqual(
            data['dashboard_config']['grid_layout']['lg'][0],
            {'i': 'test-module', 'x': 0, 'y': 0, 'w': 12, 'h': 12}
        )
        
    def test_preference_deserialization(self):
        """Test deserializing preference data."""
        data = {
            'user': self.user.id,
            'dashboard_config': {
                'modules': [
                    {'id': 'new-module', 'title': 'New Module'}
                ],
                'grid_layout': {
                    'lg': [{'i': 'new-module', 'x': 0, 'y': 0, 'w': 6, 'h': 6}]
                }
            }
        }
        serializer = UserPreferenceSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        preference = serializer.save()
        self.assertEqual(preference.user, self.user)
        self.assertEqual(preference.dashboard_config['modules'][0]['id'], 'new-module')
        self.assertEqual(
            preference.dashboard_config['grid_layout']['lg'][0],
            {'i': 'new-module', 'x': 0, 'y': 0, 'w': 6, 'h': 6}
        )
        
    def test_preference_update(self):
        """Test updating preference data."""
        data = {
            'dashboard_config': {
                'modules': [
                    {'id': 'updated-module', 'title': 'Updated Module'}
                ]
            }
        }
        serializer = UserPreferenceSerializer(
            instance=self.preference, 
            data=data, 
            partial=True
        )
        self.assertTrue(serializer.is_valid())
        
        updated_preference = serializer.save()
        self.assertEqual(
            updated_preference.dashboard_config['modules'][0]['id'], 
            'updated-module'
        )
        self.assertEqual(
            updated_preference.dashboard_config['modules'][0]['title'], 
            'Updated Module'
        )
        # Grid layout should remain unchanged
        self.assertEqual(
            updated_preference.dashboard_config['grid_layout']['lg'][0],
            {'i': 'test-module', 'x': 0, 'y': 0, 'w': 12, 'h': 12}
        )


class TagSerializerTests(TestCase):
    """Tests for TagSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.tag = Tag.objects.create(
            name="Test Tag",
            description="Test tag description"
        )
        self.serializer = TagSerializer(instance=self.tag)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('name', data)
        self.assertIn('slug', data)
        self.assertIn('description', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        
    def test_name_field_content(self):
        """Test that the name field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['name'], 'Test Tag')
        
    def test_slug_field_content(self):
        """Test that the slug field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['slug'], 'test-tag')
        
    def test_tag_deserialization(self):
        """Test deserializing tag data."""
        data = {
            'name': 'New Tag',
            'description': 'New tag description'
        }
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        tag = serializer.save()
        self.assertEqual(tag.name, 'New Tag')
        self.assertEqual(tag.slug, 'new-tag')
        self.assertEqual(tag.description, 'New tag description')
        
    def test_tag_update(self):
        """Test updating tag data."""
        data = {
            'description': 'Updated description'
        }
        serializer = TagSerializer(instance=self.tag, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_tag = serializer.save()
        self.assertEqual(updated_tag.name, 'Test Tag')  # Unchanged
        self.assertEqual(updated_tag.slug, 'test-tag')  # Unchanged
        self.assertEqual(updated_tag.description, 'Updated description')
        
    def test_name_uniqueness(self):
        """Test that tag names must be unique."""
        data = {
            'name': 'Test Tag',  # Already exists
            'description': 'Another description'
        }
        serializer = TagSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        

class TaggedItemSerializerTests(TestCase):
    """Tests for TaggedItemSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.tag = Tag.objects.create(name="Test Tag")
        self.content_type = ContentType.objects.get_for_model(User)
        
        self.tagged_item = TaggedItem.objects.create(
            tag=self.tag,
            content_type=self.content_type,
            object_id=self.user.pk
        )
        self.serializer = TaggedItemSerializer(instance=self.tagged_item)
        
    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        data = self.serializer.data
        self.assertIn('id', data)
        self.assertIn('tag', data)
        self.assertIn('content_type', data)
        self.assertIn('object_id', data)
        self.assertIn('created_at', data)
        
    def test_tag_field_content(self):
        """Test that the tag field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['tag'], self.tag.id)
        
    def test_content_type_field_content(self):
        """Test that the content_type field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['content_type'], self.content_type.id)
        
    def test_object_id_field_content(self):
        """Test that the object_id field contains the correct data."""
        data = self.serializer.data
        self.assertEqual(data['object_id'], self.user.pk)
        
    def test_tagged_item_deserialization(self):
        """Test deserializing tagged item data."""
        preference = UserPreference.objects.create(user=self.user)
        content_type = ContentType.objects.get_for_model(UserPreference)
        
        data = {
            'tag': self.tag.id,
            'content_type': content_type.id,
            'object_id': preference.pk
        }
        serializer = TaggedItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        tagged_item = serializer.save()
        self.assertEqual(tagged_item.tag, self.tag)
        self.assertEqual(tagged_item.content_type, content_type)
        self.assertEqual(tagged_item.object_id, preference.pk)
        
    def test_unique_together_constraint(self):
        """Test the unique_together constraint."""
        data = {
            'tag': self.tag.id,
            'content_type': self.content_type.id,
            'object_id': self.user.pk
        }
        serializer = TaggedItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors) 