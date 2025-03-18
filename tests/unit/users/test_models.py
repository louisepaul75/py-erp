"""
Unit tests for the users app models.

Test cases for UserProfile, Role, PermissionCategory, PermissionCategoryItem, and DataPermission models.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TransactionTestCase

from users.models import (
    UserProfile,
    Role,
    PermissionCategory,
    PermissionCategoryItem,
    DataPermission,
)

User = get_user_model()


class UserProfileModelTest(TransactionTestCase):
    """Test cases for the UserProfile model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        # UserProfile should be created automatically via signal

    def test_profile_creation(self):
        """Test that a profile is created automatically for a new user."""
        # Check that the profile was created
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertIsInstance(self.user.profile, UserProfile)

    def test_profile_string_representation(self):
        """Test the string representation of a UserProfile."""
        expected_string = f"Profile for {self.user.username}"
        self.assertEqual(str(self.user.profile), expected_string)

    def test_profile_default_values(self):
        """Test that a new profile has the expected default values."""
        profile = self.user.profile
        self.assertEqual(profile.department, "")
        self.assertEqual(profile.position, "")
        self.assertEqual(profile.phone, "")
        self.assertEqual(profile.language_preference, "en")
        self.assertEqual(profile.status, "active")
        self.assertFalse(profile.two_factor_enabled)
        self.assertIsNone(profile.profile_picture.name)
        self.assertIsNone(profile.last_password_change)

    def test_profile_update(self):
        """Test updating profile fields."""
        profile = self.user.profile
        profile.department = "IT"
        profile.position = "Developer"
        profile.phone = "123-456-7890"
        profile.status = "inactive"
        profile.save()

        # Fetch from DB to make sure it's saved
        refreshed_profile = UserProfile.objects.get(id=profile.id)
        self.assertEqual(refreshed_profile.department, "IT")
        self.assertEqual(refreshed_profile.position, "Developer")
        self.assertEqual(refreshed_profile.phone, "123-456-7890")
        self.assertEqual(refreshed_profile.status, "inactive")


class RoleModelTest(TransactionTestCase):
    """Test cases for the Role model."""

    def setUp(self):
        """Set up test fixtures."""
        self.group = Group.objects.create(name="Test Role Group")
        self.role = Role.objects.create(
            group=self.group,
            description="Test role description",
            is_system_role=True,
            priority=10,
        )

        # Create a parent-child relationship
        self.child_group = Group.objects.create(name="Child Role Group")
        self.child_role = Role.objects.create(
            group=self.child_group,
            description="Child role description",
            parent_role=self.role,
        )

    def test_role_string_representation(self):
        """Test the string representation of a Role."""
        expected_string = f"Role: {self.group.name}"
        self.assertEqual(str(self.role), expected_string)

    def test_role_attributes(self):
        """Test that a role has the expected attributes."""
        self.assertEqual(self.role.group, self.group)
        self.assertEqual(self.role.description, "Test role description")
        self.assertTrue(self.role.is_system_role)
        self.assertEqual(self.role.priority, 10)
        self.assertIsNone(self.role.parent_role)

    def test_role_hierarchy(self):
        """Test parent-child relationship between roles."""
        self.assertEqual(self.child_role.parent_role, self.role)
        self.assertIn(self.child_role, self.role.child_roles.all())


class PermissionCategoryModelTest(TransactionTestCase):
    """Test cases for the PermissionCategory model."""

    def setUp(self):
        """Set up test fixtures."""
        self.category = PermissionCategory.objects.create(
            name="User Management",
            description="Permissions for managing users",
            icon="user-circle",
            order=1,
        )

        # Create a content type and permission for testing
        self.content_type = ContentType.objects.get_for_model(User)
        self.permission = Permission.objects.create(
            codename="test_user_perm",
            name="Test User Permission",
            content_type=self.content_type,
        )

        # Link permission to category
        self.category_item = PermissionCategoryItem.objects.create(
            category=self.category, permission=self.permission, order=5
        )

    def test_category_string_representation(self):
        """Test the string representation of a PermissionCategory."""
        self.assertEqual(str(self.category), "User Management")

    def test_category_attributes(self):
        """Test that a category has the expected attributes."""
        self.assertEqual(self.category.name, "User Management")
        self.assertEqual(self.category.description, "Permissions for managing users")
        self.assertEqual(self.category.icon, "user-circle")
        self.assertEqual(self.category.order, 1)

    def test_category_has_permissions(self):
        """Test that a category can have associated permissions."""
        self.assertEqual(self.category.permissions.count(), 1)
        self.assertEqual(self.category.permissions.first(), self.category_item)
        self.assertEqual(self.category_item.permission, self.permission)
        self.assertEqual(self.category_item.order, 5)

    def test_category_item_string_representation(self):
        """Test the string representation of a PermissionCategoryItem."""
        expected_string = f"{self.category.name} - {self.permission.name}"
        self.assertEqual(str(self.category_item), expected_string)


class DataPermissionModelTest(TransactionTestCase):
    """Test cases for DataPermission model."""

    def setUp(self):
        """Set up test fixtures."""
        # Create users
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="adminpassword",
            is_staff=True,
            is_superuser=True,
        )

        self.test_user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )

        # Create group
        self.test_group = Group.objects.create(name="Test Group")

        # Get content type for User model
        self.user_content_type = ContentType.objects.get_for_model(User)

        # Create DataPermission instances
        self.user_permission = DataPermission.objects.create(
            user=self.test_user,
            content_type=self.user_content_type,
            object_id=self.admin.id,
            permission_type="view",
            created_by=self.admin,
        )

        # Group permission
        self.group_permission = DataPermission.objects.create(
            user=self.admin,  # Required field
            group=self.test_group,
            content_type=self.user_content_type,
            object_id=self.test_user.id,
            permission_type="edit",
            created_by=self.admin,
        )

    def test_data_permission_attributes(self):
        """Test that DataPermission has the correct attributes."""
        # Test user permission attributes
        self.assertEqual(self.user_permission.user, self.test_user)
        self.assertIsNone(self.user_permission.group)
        self.assertEqual(self.user_permission.content_type, self.user_content_type)
        self.assertEqual(self.user_permission.object_id, self.admin.id)
        self.assertEqual(self.user_permission.permission_type, "view")
        self.assertEqual(self.user_permission.created_by, self.admin)

    def test_data_permission_string_representation(self):
        """Test the string representation of DataPermission."""
        expected = f"{self.test_user.username} - view - {self.admin}"
        self.assertEqual(str(self.user_permission), expected)

    def test_group_permission_attributes(self):
        """Test that a group DataPermission has the correct attributes."""
        self.assertEqual(self.group_permission.user, self.admin)
        self.assertEqual(self.group_permission.group, self.test_group)
        self.assertEqual(self.group_permission.content_type, self.user_content_type)
        self.assertEqual(self.group_permission.object_id, self.test_user.id)
        self.assertEqual(self.group_permission.permission_type, "edit")
