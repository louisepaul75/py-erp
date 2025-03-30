"""
Admin interface for the products app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
    ProductImage,
)
from pyerp.business_modules.products.tag_models import FieldOverride, M2MOverride
from pyerp.core.models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    """
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FieldOverride)
class FieldOverrideAdmin(admin.ModelAdmin):
    """
    Admin interface for FieldOverride model.
    """
    list_display = ('content_type', 'object_id', 'field_name', 'inherit')
    list_filter = ('content_type', 'inherit')
    search_fields = ('field_name',)


@admin.register(M2MOverride)
class M2MOverrideAdmin(admin.ModelAdmin):
    """
    Admin interface for M2MOverride model.
    """
    list_display = ('content_type', 'object_id', 'relationship_name', 'inherit')
    list_filter = ('content_type', 'inherit')
    search_fields = ('relationship_name',)


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


# Define the inline admin for ProductImage
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Allow adding one image at a time
    fields = ('image', 'is_primary')
    # You might want readonly_fields or other customizations here


@admin.register(ParentProduct)
class ParentProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "legacy_base_sku", "is_active", "is_new", "release_date")
    list_filter = ("is_active", "is_new", "tags")
    search_fields = ("sku", "name", "legacy_base_sku", "legacy_id")
    fieldsets = (
        (
            _("Basic Information"),
            {
                "fields": ("sku", "legacy_base_sku", "legacy_id", "name"),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "is_new", "release_date"),
            },
        ),
        (
            _("Dimensions"),
            {
                "fields": ("length_mm", "width_mm", "height_mm", "weight"),
            },
        ),
        (
            _("Categorization"),
            {
                "fields": ("tags",),
            },
        ),
    )
    inlines = [VariantInline]


@admin.register(VariantProduct)
class VariantProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "parent", "variant_code", "legacy_base_sku", "is_active")
    list_filter = ("parent", "is_active", "is_new", "is_featured", "is_bestseller", "is_verkaufsartikel", "tags")
    search_fields = (
        "sku",
        "name",
        "legacy_base_sku",
        "variant_code",
        "legacy_id",
        "legacy_sku",
    )
    
    # Explicitly define fields to exclude the weight field from the admin interface
    # Since weight is defined in BaseProduct but doesn't exist in the database for VariantProduct
    fields = (
        "sku",
        "parent",
        "variant_code",
        "legacy_base_sku",
        "legacy_id",
        "legacy_sku",
        "name",
        "name_en",
        "description",
        "description_en",
        "short_description",
        "short_description_en",
        "keywords",
        "is_active",
        "is_verkaufsartikel",
        "is_featured",
        "is_new",
        "is_bestseller",
        "is_discontinued",
        "retail_price",
        "wholesale_price",
        "retail_unit",
        "wholesale_unit",
        "release_date",
        "auslaufdatum",
        "width_mm",
        "color",
        "tags",
        "category_id",
    )
    
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_url", "is_primary")
    search_fields = ("product__name", "image_url")
