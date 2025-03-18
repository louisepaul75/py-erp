"""
Unit tests for the users app services.

Test cases for UserService, RoleService, and PermissionService.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase
from django.utils import timezone

from users.models import (
    UserProfile, Role, PermissionCategory, 
    PermissionCategoryItem, DataPermission
)
from users.services import UserService, RoleService, PermissionService

User = get_user_model()


class UserServiceTest(TransactionTestCase):
    """Test cases for the UserService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test users
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
        
        # Create test groups
        self.group1 = Group.objects.create(name='Group 1')
        self.group2 = Group.objects.create(name='Group 2')
        self.group3 = Group.objects.create(name='Group 3')
        
        # Create test permissions
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission1 = Permission.objects.create(
            codename='test_perm1',
            name='Test Permission 1',
            content_type=self.content_type
        )
        self.permission2 = Permission.objects.create(
            codename='test_perm2',
            name='Test Permission 2',
            content_type=self.content_type
        )
        
        # Assign permissions to groups
        self.group1.permissions.add(self.permission1)
        self.group2.permissions.add(self.permission2)
        
        # Update user profile for testing
        self.user1.profile.department = 'IT'
        self.user1.profile.status = 'active'
        self.user1.profile.save()
        
        self.user2.profile.department = 'HR'
        self.user2.profile.status = 'inactive'
        self.user2.profile.save()

    def test_assign_user_to_groups(self):
        """Test assigning a user to multiple groups."""
        # Assign user to groups
        groups = UserService.assign_user_to_groups(
            self.user1, 
            [self.group1.id, self.group2.id]
        )
        
        # Check results
        self.assertEqual(len(groups), 2)
        self.assertIn(self.group1, groups)
        self.assertIn(self.group2, groups)
        
        # Check user's groups
        self.assertIn(self.group1, self.user1.groups.all())
        self.assertIn(self.group2, self.user1.groups.all())

    def test_remove_user_from_groups(self):
        """Test removing a user from multiple groups."""
        # First add user to groups
        self.user1.groups.add(self.group1, self.group2, self.group3)
        
        # Remove from specific groups
        groups = UserService.remove_user_from_groups(
            self.user1, 
            [self.group1.id, self.group3.id]
        )
        
        # Check results
        self.assertEqual(len(groups), 2)
        self.assertIn(self.group1, groups)
        self.assertIn(self.group3, groups)
        
        # Check user's groups
        self.assertNotIn(self.group1, self.user1.groups.all())
        self.assertIn(self.group2, self.user1.groups.all())
        self.assertNotIn(self.group3, self.user1.groups.all())

    def test_get_users_by_department(self):
        """Test getting users by department."""
        # Get users by department
        it_users = UserService.get_users_by_department('IT')
        hr_users = UserService.get_users_by_department('HR')
        
        # Check results
        self.assertEqual(len(it_users), 1)
        self.assertEqual(len(hr_users), 1)
        self.assertEqual(it_users[0], self.user1)
        self.assertEqual(hr_users[0], self.user2)

    def test_get_users_by_status(self):
        """Test getting users by status."""
        # Get users by status
        active_users = UserService.get_users_by_status('active')
        inactive_users = UserService.get_users_by_status('inactive')
        
        # Check results
        self.assertEqual(len(active_users), 1)
        self.assertEqual(len(inactive_users), 1)
        self.assertEqual(active_users[0], self.user1)
        self.assertEqual(inactive_users[0], self.user2)

    def test_update_user_status(self):
        """Test updating user status."""
        # Update user status
        UserService.update_user_status(self.user1, 'pending')
        
        # Check result
        self.assertEqual(self.user1.profile.status, 'pending')

    def test_create_user_with_profile(self):
        """Test creating a user with profile data."""
        # Create user with profile
        new_user = UserService.create_user_with_profile(
            username='newuser',
            email='newuser@example.com',
            password='newpassword',
            department='Finance',
            position='Manager',
            phone='555-1234',
            language_preference='fr',
            status='pending'
        )
        
        # Check user was created
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.username, 'newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        
        # Check profile was created with correct data
        self.assertIsInstance(new_user.profile, UserProfile)
        self.assertEqual(new_user.profile.department, 'Finance')
        self.assertEqual(new_user.profile.position, 'Manager')
        self.assertEqual(new_user.profile.phone, '555-1234')
        self.assertEqual(new_user.profile.language_preference, 'fr')
        self.assertEqual(new_user.profile.status, 'pending')


class RoleServiceTest(TransactionTestCase):
    """Test cases for the RoleService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create test groups
        self.group1 = Group.objects.create(name='Role 1')
        self.group2 = Group.objects.create(name='Role 2')
        
        # Create test permissions
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission1 = Permission.objects.create(
            codename='test_perm1',
            name='Test Permission 1',
            content_type=self.content_type
        )
        self.permission2 = Permission.objects.create(
            codename='test_perm2',
            name='Test Permission 2',
            content_type=self.content_type
        )
        
        # Create test users
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
        
        # Create a role
        self.role1 = Role.objects.create(
            group=self.group1,
            description='Test Role 1',
            is_system_role=True,
            priority=5
        )
        
        # Add user to group
        self.user1.groups.add(self.group1)

    def test_create_role(self):
        """Test creating a new role."""
        # Create a parent role first
        parent_role = Role.objects.create(
            name="Parent Role",
            description="Parent role for testing",
            is_active=True
        )
        
        # Create a new role with the parent
        role_data = {
            'name': 'Test Role',
            'description': 'A test role',
            'is_system_role': False,
            'is_active': True,
            'parent_role': parent_role.id
        }
        
        role = RoleService.create_role(**role_data)
        
        # Check role was created with correct attributes
        self.assertEqual(role.name, 'Test Role')
        self.assertEqual(role.description, 'A test role')
        self.assertEqual(role.is_system_role, False)
        self.assertEqual(role.is_active, True)
        self.assertEqual(role.parent_role, parent_role)

    def test_get_users_in_role(self):
        """Test getting users in a role."""
        # Get users in role
        users = RoleService.get_users_in_role(self.role1)
        
        # Check result
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], self.user1)

    def test_get_all_child_roles(self):
        """Test getting all child roles of a role."""
        # Create child roles
        group_child1 = Group.objects.create(name='Child Role 1')
        child_role1 = Role.objects.create(
            group=group_child1,
            description='Child Role 1 description',
            parent_role=self.role1
        )
        
        group_child2 = Group.objects.create(name='Child Role 2')
        child_role2 = Role.objects.create(
            group=group_child2,
            description='Child Role 2 description',
            parent_role=self.role1
        )
        
        # Create grandchild role
        group_grandchild = Group.objects.create(name='Grandchild Role')
        grandchild_role = Role.objects.create(
            group=group_grandchild,
            description='Grandchild Role description',
            parent_role=child_role1
        )
        
        # Get all child roles
        child_roles = RoleService.get_all_child_roles(self.role1)
        
        # Check result
        self.assertEqual(len(child_roles), 3)
        self.assertIn(child_role1, child_roles)
        self.assertIn(child_role2, child_roles)
        self.assertIn(grandchild_role, child_roles)


class PermissionServiceTest(TransactionTestCase):
    """Test cases for the PermissionService."""

    def setUp(self):
        """Set up test fixtures."""
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpassword'
        )
        
        # Get content type for permissions
        self.user_ct = ContentType.objects.get_for_model(User)
        
        # Create or get permissions
        self.view_user_perm, _ = Permission.objects.get_or_create(
            content_type=self.user_ct,
            codename='test_view_user',
            defaults={'name': 'Test Can view user'}
        )
        
        self.change_user_perm, _ = Permission.objects.get_or_create(
            content_type=self.user_ct,
            codename='test_change_user',
            defaults={'name': 'Test Can change user'}
        )
        
        self.delete_user_perm, _ = Permission.objects.get_or_create(
            content_type=self.user_ct,
            codename='test_delete_user',
            defaults={'name': 'Test Can delete user'}
        )
        
        # Create group with permissions
        self.test_group = Group.objects.create(name='Test Group')
        self.test_group.permissions.add(self.view_user_perm, self.change_user_perm)
        
        # Add user to group
        self.regular_user.groups.add(self.test_group)
        
        # Create categories
        self.user_cat, _ = PermissionCategory.objects.get_or_create(
            name='User Management', 
            defaults={'description': 'User management permissions'}
        )
        
        # Link permissions to categories
        PermissionCategoryItem.objects.get_or_create(
            category=self.user_cat,
            permission=self.view_user_perm
        )
        
        PermissionCategoryItem.objects.get_or_create(
            category=self.user_cat,
            permission=self.change_user_perm
        )
        
        PermissionCategoryItem.objects.get_or_create(
            category=self.user_cat,
            permission=self.delete_user_perm
        )

    def test_get_user_permissions(self):
        """Test getting a user's permissions."""
        permissions = PermissionService.get_user_permissions(self.regular_user)
        
        # User should have permissions from the group
        self.assertIn(self.view_user_perm, permissions)
        self.assertIn(self.change_user_perm, permissions)
        
        # User should not have permissions they don't have
        self.assertNotIn(self.delete_user_perm, permissions)
    
    def test_check_object_permission(self):
        """Test checking permissions for a specific object."""
        # Create data permission for testing
        data_permission = DataPermission.objects.create(
            user=self.regular_user,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.admin_user.id,
            permission_type='view'
        )
        
        # User should have permission
        self.assertTrue(
            PermissionService.check_object_permission(
                self.regular_user, 
                self.admin_user, 
                'view'
            )
        )
        
        # User should not have edit permission
        self.assertFalse(
            PermissionService.check_object_permission(
                self.regular_user, 
                self.admin_user, 
                'edit'
            )
        )
        
        # Clean up
        data_permission.delete()
    
    def test_organize_permissions_by_category(self):
        """Test organizing permissions by category."""
        categorized = PermissionService.organize_permissions_by_category()
        
        # There should be at least one category
        self.assertGreaterEqual(len(categorized), 1)
        
        # User Management category should be in the results
        category_names = [cat['name'] for cat in categorized]
        self.assertIn('User Management', category_names)
        
        # Find the User Management category
        user_cat = None
        for cat in categorized:
            if cat['name'] == 'User Management':
                user_cat = cat
                break
        
        # Category should contain our permissions
        perm_codenames = [p['codename'] for p in user_cat['permissions']]
        self.assertIn('test_view_user', perm_codenames)
        self.assertIn('test_change_user', perm_codenames)
        self.assertIn('test_delete_user', perm_codenames) 