"""
API tests for the users app views.

Test cases for the API endpoints in the users app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import uuid

from users.models import (
    UserProfile, Role, PermissionCategory, 
    PermissionCategoryItem, DataPermission
)

User = get_user_model()


class UserViewSetTest(TransactionTestCase):
    """Test cases for the UserViewSet API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create API client
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Update profiles
        self.admin_user.profile.department = 'IT'
        self.admin_user.profile.save()
        
        self.regular_user.profile.department = 'HR'
        self.regular_user.profile.save()
        
        # Create groups
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')
        
        # Authentication
        self.client.force_authenticate(user=self.admin_user)

    def test_list_users(self):
        """Test listing users."""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['username'], self.admin_user.username)
        self.assertEqual(response.data[1]['username'], self.regular_user.username)

    def test_retrieve_user(self):
        """Test retrieving a single user."""
        url = reverse('user-detail', args=[self.regular_user.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.regular_user.username)
        self.assertEqual(response.data['email'], self.regular_user.email)
        self.assertEqual(response.data['profile']['department'], 'HR')

    def test_create_user(self):
        """Test creating a new user."""
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        
        url = reverse('user-list')
        data = {
            'username': unique_username,
            'email': f'{unique_username}@example.com',
            'password': 'newpassword',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'department': 'Finance',
                'position': 'Analyst',
                'phone': '555-1234'
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username=unique_username).exists())
        
        # Check user was created with correct data
        created_user = User.objects.get(username=unique_username)
        self.assertEqual(created_user.email, f'{unique_username}@example.com')
        self.assertEqual(created_user.first_name, 'New')
        self.assertEqual(created_user.last_name, 'User')
        
        # Check profile was created with correct data
        self.assertEqual(created_user.profile.department, 'Finance')
        self.assertEqual(created_user.profile.position, 'Analyst')
        self.assertEqual(created_user.profile.phone, '555-1234')

    def test_update_user(self):
        """Test updating a user."""
        url = reverse('user-detail', args=[self.regular_user.id])
        data = {
            'username': self.regular_user.username,
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User',
            'profile': {
                'department': 'Marketing',
                'position': 'Manager',
                'phone': '555-5678'
            }
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.regular_user.refresh_from_db()
        self.regular_user.profile.refresh_from_db()
        
        # Check user was updated with correct data
        self.assertEqual(self.regular_user.email, 'updated@example.com')
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertEqual(self.regular_user.last_name, 'User')
        
        # Check profile was updated with correct data
        self.assertEqual(self.regular_user.profile.department, 'Marketing')
        self.assertEqual(self.regular_user.profile.position, 'Manager')
        self.assertEqual(self.regular_user.profile.phone, '555-5678')

    def test_delete_user(self):
        """Test deleting a user."""
        url = reverse('user-detail', args=[self.regular_user.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.regular_user.id)

    def test_assign_groups(self):
        """Test assigning groups to a user."""
        url = reverse('user-assign-groups', args=[self.regular_user.id])
        data = {
            'group_ids': [self.group1.id, self.group2.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check user was assigned to groups
        self.regular_user.refresh_from_db()
        self.assertIn(self.group1, self.regular_user.groups.all())
        self.assertIn(self.group2, self.regular_user.groups.all())

    def test_remove_groups(self):
        """Test removing groups from a user."""
        # First assign groups
        self.regular_user.groups.add(self.group1, self.group2)
        
        url = reverse('user-remove-groups', args=[self.regular_user.id])
        data = {
            'group_ids': [self.group1.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check group was removed
        self.regular_user.refresh_from_db()
        self.assertNotIn(self.group1, self.regular_user.groups.all())
        self.assertIn(self.group2, self.regular_user.groups.all())

    def test_update_status(self):
        """Test updating a user's status."""
        url = reverse('user-update-status', args=[self.regular_user.id])
        data = {
            'status': 'inactive'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check status was updated
        self.regular_user.refresh_from_db()
        self.regular_user.profile.refresh_from_db()
        self.assertEqual(self.regular_user.profile.status, 'inactive')

    def test_filter_by_department(self):
        """Test filtering users by department."""
        url = reverse('user-by-department')
        response = self.client.get(url, {'department': 'HR'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], self.regular_user.username)

    def test_permission_denied_for_regular_user(self):
        """Test that regular users cannot access admin endpoints."""
        # Switch to regular user
        self.client.force_authenticate(user=self.regular_user)
        
        # Try to create a user
        url = reverse('user-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(url, data, format='json')
        
        # Should be denied
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GroupViewSetTest(TransactionTestCase):
    """Test cases for the GroupViewSet API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create API client
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password2'
        )
        
        # Create groups
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')
        
        # Add users to groups
        self.user1.groups.add(self.group1)
        self.user2.groups.add(self.group1)
        
        # Create permissions
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission1 = Permission.objects.create(
            codename='perm1',
            name='Permission 1',
            content_type=self.content_type
        )
        self.permission2 = Permission.objects.create(
            codename='perm2',
            name='Permission 2',
            content_type=self.content_type
        )
        
        # Create role
        self.role1 = Role.objects.create(
            group=self.group1,
            description='Role 1'
        )
        
        # Authentication
        self.client.force_authenticate(user=self.admin_user)

    def test_list_groups(self):
        """Test listing groups."""
        url = reverse('group-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_group(self):
        """Test retrieving a single group."""
        url = reverse('group-detail', args=[self.group1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Group 1')
        self.assertEqual(response.data['users_count'], 2)

    def test_create_group(self):
        """Test creating a new group."""
        url = reverse('group-list')
        data = {
            'name': 'New Group'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.count(), 3)
        
        # Check group was created
        created_group = Group.objects.get(name='New Group')
        self.assertIsNotNone(created_group)

    def test_update_group(self):
        """Test updating a group."""
        url = reverse('group-detail', args=[self.group1.id])
        data = {
            'name': 'Updated Group'
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.group1.refresh_from_db()
        
        # Check group was updated
        self.assertEqual(self.group1.name, 'Updated Group')

    def test_delete_group(self):
        """Test deleting a group."""
        url = reverse('group-detail', args=[self.group1.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Group.objects.count(), 1)
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=self.group1.id)

    def test_group_users(self):
        """Test getting users in a group."""
        url = reverse('group-users', args=[self.group1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check users are in response
        usernames = [user['username'] for user in response.data]
        self.assertIn(self.user1.username, usernames)
        self.assertIn(self.user2.username, usernames)

    def test_add_permissions(self):
        """Test adding permissions to a group."""
        url = reverse('group-add-permissions', args=[self.group1.id])
        data = {
            'permission_ids': [self.permission1.id, self.permission2.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check permissions were added
        self.group1.refresh_from_db()
        self.assertIn(self.permission1, self.group1.permissions.all())
        self.assertIn(self.permission2, self.group1.permissions.all())

    def test_remove_permissions(self):
        """Test removing permissions from a group."""
        # First add permissions
        self.group1.permissions.add(self.permission1, self.permission2)
        
        url = reverse('group-remove-permissions', args=[self.group1.id])
        data = {
            'permission_ids': [self.permission1.id]
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check permissions were updated
        self.group1.refresh_from_db()
        self.assertNotIn(self.permission1, self.group1.permissions.all())
        self.assertIn(self.permission2, self.group1.permissions.all())


class RoleViewSetTest(TransactionTestCase):
    """Test cases for the RoleViewSet API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create API client
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        # Create groups
        self.group1 = Group.objects.create(name='Role Group 1')
        self.group2 = Group.objects.create(name='Role Group 2')
        self.child_group = Group.objects.create(name='Child Role Group')
        
        # Create roles
        self.role1 = Role.objects.create(
            group=self.group1,
            description='Parent Role',
            is_system_role=True,
            priority=10
        )
        self.role2 = Role.objects.create(
            group=self.group2,
            description='Another Role',
            is_system_role=False,
            priority=5
        )
        
        # Authentication
        self.client.force_authenticate(user=self.admin_user)

    def test_list_roles(self):
        """Test listing roles."""
        url = reverse('role-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_role(self):
        """Test retrieving a single role."""
        url = reverse('role-detail', args=[self.role1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['group_name'], 'Role Group 1')
        self.assertEqual(response.data['description'], 'Parent Role')
        self.assertTrue(response.data['is_system_role'])
        self.assertEqual(response.data['priority'], 10)

    def test_create_role(self):
        """Test creating a new role."""
        url = reverse('role-list')
        data = {
            'group': self.child_group.id,
            'description': 'New Role',
            'is_system_role': False,
            'priority': 3,
            'parent_role': self.role1.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), 3)
        
        # Check role was created with correct data
        created_role = Role.objects.get(group=self.child_group)
        self.assertEqual(created_role.description, 'New Role')
        self.assertFalse(created_role.is_system_role)
        self.assertEqual(created_role.priority, 3)
        self.assertEqual(created_role.parent_role, self.role1)

    def test_update_role(self):
        """Test updating a role."""
        url = reverse('role-detail', args=[self.role2.id])
        data = {
            'group': self.role2.group.id,
            'description': 'Updated Role',
            'is_system_role': True,
            'priority': 7,
            'parent_role': self.role1.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh from database
        self.role2.refresh_from_db()
        
        # Check role was updated with correct data
        self.assertEqual(self.role2.description, 'Updated Role')
        self.assertTrue(self.role2.is_system_role)
        self.assertEqual(self.role2.priority, 7)
        self.assertEqual(self.role2.parent_role, self.role1)

    def test_delete_role(self):
        """Test deleting a role."""
        url = reverse('role-detail', args=[self.role2.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Role.objects.count(), 1)
        with self.assertRaises(Role.DoesNotExist):
            Role.objects.get(id=self.role2.id)

    def test_add_child_role(self):
        """Test adding a child role to a parent role."""
        # Create a child role with add_child_role endpoint
        url = reverse('role-add-child-role', args=[self.role1.id])
        data = {
            'group': self.child_group.id,
            'description': 'Child Role',
            'is_system_role': False,
            'priority': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check child role was created with correct parent
        child_role = Role.objects.get(group=self.child_group)
        self.assertEqual(child_role.description, 'Child Role')
        self.assertEqual(child_role.parent_role, self.role1)

    def test_get_child_roles(self):
        """Test getting child roles of a parent role."""
        # First create a child role
        child_role = Role.objects.create(
            group=self.child_group,
            description='Child Role',
            parent_role=self.role1
        )
        
        url = reverse('role-child-roles', args=[self.role1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], child_role.id)
        self.assertEqual(response.data[0]['description'], 'Child Role')


class PermissionViewSetTest(TransactionTestCase):
    """Test cases for the PermissionViewSet API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        # Create API client
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        # Get content types for permission creation
        user_content_type = ContentType.objects.get_for_model(User)
        
        # Create or get permissions with unique codenames
        self.user_perm1, created = Permission.objects.get_or_create(
            content_type=user_content_type,
            codename='test_view_user',
            defaults={'name': 'Test Can view user'}
        )
        
        self.user_perm2, created = Permission.objects.get_or_create(
            content_type=user_content_type,
            codename='test_add_user',
            defaults={'name': 'Test Can add user'}
        )
        
        self.user_perm3, created = Permission.objects.get_or_create(
            content_type=user_content_type,
            codename='test_change_user',
            defaults={'name': 'Test Can change user'}
        )
        
        # Create permission categories
        self.user_category, created = PermissionCategory.objects.get_or_create(
            name='User Management',
            defaults={'icon': 'user-circle'}
        )
        
        self.admin_category, created = PermissionCategory.objects.get_or_create(
            name='Administration',
            defaults={'icon': 'users-cog'}
        )
        
        # Update icons if they already existed
        if not created:
            self.user_category.icon = 'user-circle'
            self.user_category.save()
            
            self.admin_category.icon = 'users-cog'
            self.admin_category.save()
        
        # Add permissions to categories
        PermissionCategoryItem.objects.get_or_create(
            category=self.user_category,
            permission=self.user_perm1
        )
        
        PermissionCategoryItem.objects.get_or_create(
            category=self.user_category,
            permission=self.user_perm2
        )
        
        PermissionCategoryItem.objects.get_or_create(
            category=self.admin_category,
            permission=self.user_perm3
        )
        
        # Authentication
        self.client.force_authenticate(user=self.admin_user)

    def test_list_permissions(self):
        """Test listing permissions."""
        url = reverse('permission-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 3)  # At least our 3 test permissions

    def test_retrieve_permission(self):
        """Test retrieving a single permission."""
        url = reverse('permission-detail', args=[self.user_perm1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Can view user')
        self.assertEqual(response.data['codename'], 'test_view_user')
        self.assertEqual(response.data['content_type'], self.user_perm1.content_type.id)
        self.assertEqual(response.data['content_type_name'], 'User')
        self.assertEqual(response.data['app_label'], 'auth')

    def test_permissions_by_category(self):
        """Test getting permissions organized by category."""
        url = reverse('permission-by-category')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have three categories (two created + uncategorized)
        self.assertEqual(len(response.data), 3)
        
        # Check category data
        categories = {cat['name']: cat for cat in response.data}
        self.assertIn('User Management', categories)
        self.assertIn('Administration', categories)
        self.assertIn('Uncategorized', categories)
        
        # Check user management permissions
        user_cat = categories['User Management']
        self.assertEqual(user_cat['icon'], 'user-circle')
        self.assertEqual(len(user_cat['permissions']), 2)
        
        # Check administration permissions
        admin_cat = categories['Administration']
        self.assertEqual(admin_cat['icon'], 'users-cog')
        self.assertEqual(len(admin_cat['permissions']), 1)

    def test_search_permissions(self):
        """Test searching for permissions."""
        url = reverse('permission-list')
        response = self.client.get(url, {'search': 'user'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 2)  # At least our test permissions
        
        # Check if our test permissions are in results
        codenames = [p['codename'] for p in response.data]
        self.assertIn('test_view_user', codenames) 