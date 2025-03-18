"""
Admin configuration for the users app.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Permission

from .models import (
    UserProfile,
    Role,
    PermissionCategory,
    PermissionCategoryItem,
    DataPermission,
)

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "get_department",
        "get_status",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_active", "is_staff", "profile__department", "profile__status")
    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__department",
    )

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, "profile") else ""

    get_department.short_description = "Department"

    def get_status(self, obj):
        return obj.profile.status if hasattr(obj, "profile") else ""

    get_status.short_description = "Status"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "group_name",
        "description",
        "is_system_role",
        "priority",
        "parent_role",
    )
    list_filter = ("is_system_role",)
    search_fields = ("group__name", "description")

    def group_name(self, obj):
        return obj.group.name

    group_name.short_description = "Group Name"


class PermissionCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "icon", "order")
    list_filter = ("icon",)
    search_fields = ("name", "description")


class PermissionCategoryItemAdmin(admin.ModelAdmin):
    list_display = ("category", "permission", "order")
    list_filter = ("category",)
    search_fields = ("permission__name", "permission__codename", "category__name")


class DataPermissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "content_type",
        "object_id",
        "permission_type",
        "user",
        "group",
    )
    list_filter = ("permission_type", "content_type")
    search_fields = ("user__username", "group__name", "object_id")


# Unregister the default UserAdmin
admin.site.unregister(User)

# Register models with customized admin interfaces
admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(PermissionCategory, PermissionCategoryAdmin)
admin.site.register(PermissionCategoryItem, PermissionCategoryItemAdmin)
admin.site.register(DataPermission, DataPermissionAdmin)
admin.site.register(Permission)
