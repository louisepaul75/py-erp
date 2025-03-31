"""
Models for the users app that extend Django's built-in authentication.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

# Get the default User model
User = get_user_model()


class UserProfile(models.Model):
    """
    Extension of the User model with additional fields for pyERP.
    This uses a OneToOneField to link to Django's built-in User model.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Additional profile fields
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    language_preference = models.CharField(max_length=10, default="en")

    # Profile picture using the existing storage backend
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", null=True, blank=True
    )

    # Last password change (for enforcing password policies)
    last_password_change = models.DateTimeField(null=True, blank=True)

    # Account status with more options than just is_active
    STATUS_CHOICES = (
        ("active", _("Active")),
        ("inactive", _("Inactive")),
        ("pending", _("Pending Activation")),
        ("locked", _("Temporarily Locked")),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Two-factor authentication enabled
    two_factor_enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
    else:
        # Create profile if it doesn't exist
        UserProfile.objects.create(user=instance)


class Role(models.Model):
    """
    Role model for organizing permissions at a functional level.
    Links to Django's built-in Group model.
    """

    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)

    # Role hierarchy (optional, for complex organizations)
    parent_role = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="child_roles",
    )

    def __str__(self):
        return f"Role: {self.group.name}"


class PermissionCategory(models.Model):
    """
    Organizes permissions into logical categories for UI representation.
    Supports hierarchical structure with parent-child relationships.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    # Hierarchy support
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    is_subcategory = models.BooleanField(default=False)
    
    # Code identifier (optional, for mapping in UI)
    code = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = "Permission Categories"
        ordering = ["order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """Return the full hierarchical path of this category."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    @property
    def permissions_count(self):
        """Return total count of permissions in this category and its subcategories."""
        count = self.permissions.count()
        for subcategory in self.subcategories.all():
            count += subcategory.permissions.count()
        return count


class PermissionCategoryItem(models.Model):
    """
    Maps Django permissions to categories.
    """

    category = models.ForeignKey(
        PermissionCategory, on_delete=models.CASCADE, related_name="permissions"
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("category", "permission")
        ordering = ["order", "permission__codename"]

    def __str__(self):
        return f"{self.category.name} - {self.permission.name}"


class DataPermission(models.Model):
    """
    Row-level security model for controlling access to specific data.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="data_permissions"
    )
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="data_permissions",
    )

    # The object this permission applies to
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # Permission level
    PERMISSION_CHOICES = (
        ("view", _("View")),
        ("edit", _("Edit")),
        ("delete", _("Delete")),
        ("full", _("Full Access")),
    )
    permission_type = models.CharField(max_length=10, choices=PERMISSION_CHOICES)

    # Additional metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_data_permissions",
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id", "permission_type")

    def __str__(self):
        return f"{self.user.username} - {self.permission_type} - {self.content_object}"
