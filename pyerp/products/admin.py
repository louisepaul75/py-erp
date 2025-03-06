"""
Admin interface for the products app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _  # noqa: F401

from pyerp.products.models import ProductCategory, ParentProduct, VariantProduct  # noqa: E501


@admin.register(ProductCategory)


class ProductCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductCategory model.
    """
    list_display = ('code', 'name')  # noqa: F841
    search_fields = ('code', 'name')  # noqa: F841
    ordering = ('code',)  # noqa: F841
  # noqa: F841


class VariantInline(admin.TabularInline):
    model = VariantProduct  # noqa: F841
  # noqa: F841
    extra = 0  # noqa: F841
  # noqa: F841
    fields = ('sku', 'variant_code', 'name', 'is_active')  # noqa: F841
    readonly_fields = ('sku',)  # noqa: F841
  # noqa: F841


@admin.register(ParentProduct)


class ParentProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'base_sku', 'is_active')  # noqa: F841
    list_filter = ('is_active',)  # noqa: F841
    search_fields = ('sku', 'name', 'base_sku', 'legacy_id')  # noqa: F841
    fieldsets = (  # noqa: F841
        (_('Basic Information'), {  # noqa: E128
            'fields': ('sku', 'base_sku', 'legacy_id', 'name')
        }),
        (_('Status'), {
            'fields': ('is_active',)  # noqa: E128
        }),
    )
    inlines = [VariantInline]  # noqa: F841
  # noqa: F841


@admin.register(VariantProduct)


class VariantProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'parent', 'variant_code', 'base_sku', 'is_active')  # noqa: E501
  # noqa: E501, F841
    list_filter = ('parent', 'is_active')  # noqa: F841
  # noqa: F841
    search_fields = ('sku', 'name', 'base_sku', 'variant_code', 'legacy_id', 'legacy_sku')  # noqa: E501
  # noqa: E501, F841
    fieldsets = (  # noqa: F841
  # noqa: F841
        (_('Basic Information'), {
            'fields': ('sku', 'parent', 'variant_code', 'base_sku', 'legacy_id', 'legacy_sku', 'name')  # noqa: E501
        }),
        (_('Status'), {
            'fields': ('is_active',)  # noqa: E128
        }),
    )
