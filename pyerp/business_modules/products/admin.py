"""
Admin interface for the products app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductCategory model.
    """

    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


class VariantInline(admin.TabularInline):
    model = VariantProduct
    extra = 0
    fields = ("sku", "variant_code", "name", "is_active")
    readonly_fields = ("sku",)


@admin.register(ParentProduct)
class ParentProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "base_sku", "is_active", "is_new", "release_date")
    list_filter = ("is_active", "is_new")
    search_fields = ("sku", "name", "base_sku", "legacy_id")
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("sku", "base_sku", "legacy_id", "name"),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "is_new", "release_date"),
            },
        ),
    )
    inlines = [VariantInline]


@admin.register(VariantProduct)
class VariantProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "parent", "variant_code", "base_sku", "is_active")
    list_filter = ("parent", "is_active")
    search_fields = (
        "sku",
        "name",
        "base_sku",
        "variant_code",
        "legacy_id",
        "legacy_sku",
    )
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": (
                    "sku",
                    "parent",
                    "variant_code",
                    "base_sku",
                    "legacy_id",
                    "legacy_sku",
                    "name",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active",),
            },
        ),
    )
