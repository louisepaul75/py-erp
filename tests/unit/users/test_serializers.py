"""
Unit tests for the users app serializers.

Test cases for the serializers used in the users app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase

from users.models import (
    UserProfile, Role, PermissionCategory, 
    PermissionCategoryItem, DataPermission
)
from users.serializers import (
    UserSerializer, UserDetailSerializer, UserProfileSerializer,
    GroupSerializer, RoleSerializer, PermissionSerializer,
    PermissionCategorySerializer
)

User = get_user_model()


class UserSerializerTest(TransactionTestCase):
    """Test cases for the UserSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # Update profile
        self.user.profile.department = 'IT'
        self.user.profile.status = 'active'
        self.user.profile.save()
        
        # Serialize the user
        self.serializer = UserSerializer(instance=self.user)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'date_joined', 'department', 'status'
        ]
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_department_field_content(self):
        """Test that the department field contains the correct value."""
        self.assertEqual(self.data['department'], 'IT')

    def test_status_field_content(self):
        """Test that the status field contains the correct value."""
        self.assertEqual(self.data['status'], 'active')


class UserDetailSerializerTest(TransactionTestCase):
    """Test cases for the UserDetailSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )
        
        # Create groups and add user to one of them
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')
        self.user.groups.add(self.group1)
        
        # Update profile
        self.user.profile.department = 'IT'
        self.user.profile.phone = '123-456-7890'
        self.user.profile.save()
        
        # Serialize the user
        self.serializer = UserDetailSerializer(instance=self.user)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login',
            'profile', 'groups'
        ]
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_profile_field_content(self):
        """Test that the profile field contains the correct data."""
        profile_data = self.data['profile']
        self.assertEqual(profile_data['department'], 'IT')
        self.assertEqual(profile_data['phone'], '123-456-7890')
        self.assertEqual(profile_data['status'], 'active')

    def test_groups_field_content(self):
        """Test that the groups field contains the correct data."""
        groups_data = self.data['groups']
        self.assertEqual(len(groups_data), 1)
        self.assertEqual(groups_data[0]['id'], self.group1.id)
        self.assertEqual(groups_data[0]['name'], 'Group 1')

    def test_update_user_with_profile(self):
        """Test updating a user with profile data."""
        update_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name',
            'profile': {
                'department': 'HR',
                'position': 'Manager',
                'phone': '555-1234',
                'status': 'inactive'
            }
        }
        
        serializer = UserDetailSerializer(instance=self.user, data=update_data)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()
        
        # Check user fields were updated
        self.assertEqual(updated_user.username, 'updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        
        # Check profile fields were updated
        self.assertEqual(updated_user.profile.department, 'HR')
        self.assertEqual(updated_user.profile.position, 'Manager')
        self.assertEqual(updated_user.profile.phone, '555-1234')
        self.assertEqual(updated_user.profile.status, 'inactive')


class UserProfileSerializerTest(TransactionTestCase):
    """Test cases for the UserProfileSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Update profile
        profile = self.user.profile
        profile.department = 'IT'
        profile.position = 'Developer'
        profile.phone = '123-456-7890'
        profile.language_preference = 'fr'
        profile.status = 'active'
        profile.two_factor_enabled = True
        profile.save()
        
        # Serialize the profile
        self.serializer = UserProfileSerializer(instance=profile)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = [
            'department', 'position', 'phone', 'language_preference',
            'profile_picture', 'status', 'two_factor_enabled', 'last_password_change'
        ]
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_field_content(self):
        """Test that fields contain the correct values."""
        self.assertEqual(self.data['department'], 'IT')
        self.assertEqual(self.data['position'], 'Developer')
        self.assertEqual(self.data['phone'], '123-456-7890')
        self.assertEqual(self.data['language_preference'], 'fr')
        self.assertEqual(self.data['status'], 'active')
        self.assertTrue(self.data['two_factor_enabled'])


class GroupSerializerTest(TransactionTestCase):
    """Test cases for the GroupSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a group
        self.group = Group.objects.create(name='Test Group')
        
        # Create users and add to group
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.group.user_set.add(self.user1, self.user2)
        
        # Create permissions
        self.content_type = ContentType.objects.get_for_model(User)
        self.perm1 = Permission.objects.create(
            codename='test_perm1',
            name='Test Permission 1',
            content_type=self.content_type
        )
        self.perm2 = Permission.objects.create(
            codename='test_perm2',
            name='Test Permission 2',
            content_type=self.content_type
        )
        
        # Add permissions to group
        self.group.permissions.add(self.perm1, self.perm2)
        
        # Create role for group
        self.role = Role.objects.create(
            group=self.group,
            description='Test role for group'
        )
        
        # Serialize the group
        self.serializer = GroupSerializer(instance=self.group)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = ['id', 'name', 'permissions_count', 'users_count', 'role']
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_permissions_count(self):
        """Test that permissions_count has the correct value."""
        self.assertEqual(self.data['permissions_count'], 2)

    def test_users_count(self):
        """Test that users_count has the correct value."""
        self.assertEqual(self.data['users_count'], 2)

    def test_role_field(self):
        """Test that the role field contains the correct data."""
        role_data = self.data['role']
        self.assertEqual(role_data['id'], self.role.id)
        self.assertEqual(role_data['description'], 'Test role for group')


class RoleSerializerTest(TransactionTestCase):
    """Test cases for the RoleSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a group and a parent role
        self.parent_group = Group.objects.create(name='Parent Role Group')
        self.parent_role = Role.objects.create(
            group=self.parent_group,
            description='Parent role',
            is_system_role=True,
            priority=10
        )
        
        # Create a child role
        self.group = Group.objects.create(name='Test Role Group')
        self.role = Role.objects.create(
            group=self.group,
            description='Test role',
            is_system_role=False,
            priority=5,
            parent_role=self.parent_role
        )
        
        # Serialize the role
        self.serializer = RoleSerializer(instance=self.role)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = [
            'id', 'group', 'group_name', 'description', 
            'is_system_role', 'priority', 'parent_role'
        ]
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_field_content(self):
        """Test that fields contain the correct values."""
        self.assertEqual(self.data['group'], self.group.id)
        self.assertEqual(self.data['group_name'], 'Test Role Group')
        self.assertEqual(self.data['description'], 'Test role')
        self.assertFalse(self.data['is_system_role'])
        self.assertEqual(self.data['priority'], 5)
        self.assertEqual(self.data['parent_role'], self.parent_role.id)


class PermissionSerializerTest(TransactionTestCase):
    """Test cases for the PermissionSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a content type and permission
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission = Permission.objects.create(
            codename='test_user_perm',
            name='Test User Permission',
            content_type=self.content_type
        )
        
        # Serialize the permission
        self.serializer = PermissionSerializer(instance=self.permission)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = [
            'id', 'name', 'codename', 'content_type', 
            'content_type_name', 'app_label'
        ]
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_field_content(self):
        """Test that fields contain the correct values."""
        self.assertEqual(self.data['name'], 'Test User Permission')
        self.assertEqual(self.data['codename'], 'test_user_perm')
        self.assertEqual(self.data['content_type'], self.content_type.id)
        self.assertEqual(self.data['content_type_name'], 'User')
        self.assertEqual(self.data['app_label'], 'auth')


class PermissionCategorySerializerTest(TransactionTestCase):
    """Test cases for the PermissionCategorySerializer."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a permission category
        self.category = PermissionCategory.objects.create(
            name='User Management',
            description='Permissions for managing users',
            icon='user-circle',
            order=1
        )
        
        # Create a content type and permission
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission = Permission.objects.create(
            codename='test_user_perm',
            name='Test User Permission',
            content_type=self.content_type
        )
        
        # Link permission to category
        self.category_item = PermissionCategoryItem.objects.create(
            category=self.category,
            permission=self.permission,
            order=1
        )
        
        # Serialize the category
        self.serializer = PermissionCategorySerializer(instance=self.category)
        self.data = self.serializer.data

    def test_contains_expected_fields(self):
        """Test that the serializer contains the expected fields."""
        expected_fields = ['id', 'name', 'description', 'icon', 'order', 'permissions']
        self.assertEqual(set(self.data.keys()), set(expected_fields))

    def test_field_content(self):
        """Test that fields contain the correct values."""
        self.assertEqual(self.data['name'], 'User Management')
        self.assertEqual(self.data['description'], 'Permissions for managing users')
        self.assertEqual(self.data['icon'], 'user-circle')
        self.assertEqual(self.data['order'], 1)

    def test_permissions_field(self):
        """Test that the permissions field contains the correct data."""
        permissions_data = self.data['permissions']
        self.assertEqual(len(permissions_data), 1)
        # The related permissions should be serialized with the PermissionSerializer
        self.assertEqual(permissions_data[0]['name'], 'Test User Permission')
        self.assertEqual(permissions_data[0]['codename'], 'test_user_perm') 