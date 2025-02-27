"""
Admin interface for the products app.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models

from pyerp.products.models import Product, ProductCategory, ProductImage


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for ProductCategory model.
    """
    list_display = ('code', 'name', 'parent')
    list_filter = ('parent',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)


class ProductImageInline(admin.TabularInline):
    """
    Inline admin interface for ProductImage model.
    """
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface for Product model.
    """
    list_display = ('sku', 'name', 'category', 'list_price', 'stock_quantity', 'is_active', 'is_parent')
    list_filter = ('is_active', 'is_discontinued', 'category', 'has_bom', 'is_parent')
    search_fields = ('sku', 'base_sku', 'name', 'name_en', 'description', 'keywords')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('sku', 'base_sku', 'variant_code', 'legacy_id')
        }),
        (_('Relationship'), {
            'fields': ('parent', 'is_parent'),
            'classes': ('collapse',),
        }),
        (_('Basic Information'), {
            'fields': ('name', 'name_en', 'category', 'keywords')
        }),
        (_('Descriptions'), {
            'fields': ('short_description', 'short_description_en', 'description', 'description_en'),
            'classes': ('collapse',),
        }),
        (_('Physical Attributes'), {
            'fields': ('dimensions', 'weight')
        }),
        (_('Pricing'), {
            'fields': ('list_price', 'wholesale_price', 'gross_price', 'cost_price')
        }),
        (_('Inventory'), {
            'fields': ('stock_quantity', 'min_stock_quantity', 'backorder_quantity', 
                      'open_purchase_quantity', 'last_receipt_date', 'last_issue_date')
        }),
        (_('Sales Statistics'), {
            'fields': ('units_sold_current_year', 'units_sold_previous_year', 'revenue_previous_year'),
            'classes': ('collapse',),
        }),
        (_('Flags'), {
            'fields': ('is_active', 'is_discontinued', 'has_bom', 'is_one_sided', 'is_hanging')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    def get_queryset(self, request):
        """
        Add a count of variants to parent products.
        """
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(variant_count=models.Count('variants'))
        return queryset
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make certain fields readonly based on whether the product is a parent or not.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Editing an existing object
            readonly_fields.extend(['sku', 'legacy_id'])
            
        if obj and obj.variants.exists():
            # Don't allow changing is_parent if product has variants
            readonly_fields.append('is_parent')
        return readonly_fields 