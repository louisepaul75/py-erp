"""
Admin interface for the production module.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ProductionOrder, ProductionOrderItem


class ProductionOrderItemInline(admin.TabularInline):
    """Inline admin for production order items."""
    
    model = ProductionOrderItem
    extra = 0
    fields = (
        'item_number', 
        'operation_type', 
        'product_sku', 
        'target_quantity', 
        'completed_quantity',
        'remaining_quantity',
        'status'
    )
    readonly_fields = ('remaining_quantity',)
    show_change_link = True


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    """Admin interface for production orders."""
    
    list_display = (
        'order_number', 
        'form_number', 
        'quantity', 
        'status', 
        'creation_date', 
        'planned_date', 
        'priority'
    )
    list_filter = ('status', 'creation_date', 'planned_date')
    search_fields = ('order_number', 'form_number', 'legacy_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (ProductionOrderItemInline,)
    fieldsets = (
        (None, {
            'fields': (
                'order_number', 
                'form_number', 
                'quantity', 
                'status',
                'priority'
            )
        }),
        (_('Dates'), {
            'fields': (
                'creation_date', 
                'planned_date',
                'created_at',
                'updated_at'
            )
        }),
        (_('Legacy Information'), {
            'classes': ('collapse',),
            'fields': (
                'legacy_id',
                'legacy_key',
                'legacy_form_id'
            )
        }),
        (_('User Information'), {
            'fields': ('created_by',)
        })
    )


@admin.register(ProductionOrderItem)
class ProductionOrderItemAdmin(admin.ModelAdmin):
    """Admin interface for production order items."""
    
    list_display = (
        'item_number',
        'production_order', 
        'operation_type',
        'parent_product',
        'product_sku',
        'target_quantity',
        'completed_quantity',
        'remaining_quantity',
        'status'
    )
    list_display_links = ('item_number', 'operation_type')
    list_filter = ('status', 'operation_type', 'start_date', 'parent_product')
    search_fields = ('production_order__order_number', 'product_sku', 'legacy_id', 'operation_type', 'parent_product__sku', 'parent_product__legacy_base_sku')
    readonly_fields = ('remaining_quantity', 'created_at', 'updated_at')
    
    def get_operation_type_display(self, obj):
        """Get a user-friendly display for the operation type code."""
        operation_descriptions = {
            'E': _('Assembly'),
            'G': _('Manufacturing'),
            'P': _('Packaging'),
            'Q': _('Quality Control'),
            'T': _('Testing'),
        }
        return f"{obj.operation_type} - {operation_descriptions.get(obj.operation_type, _('Other'))}"
    get_operation_type_display.short_description = _('Operation Type')
    
    fieldsets = (
        (None, {
            'fields': (
                'production_order',
                'item_number',
                'operation_type',
                'status'
            )
        }),
        (_('Quantities'), {
            'fields': (
                'target_quantity',
                'completed_quantity',
                'remaining_quantity'
            )
        }),
        (_('Product Information'), {
            'fields': (
                'parent_product',
                'product_sku',
                'product_share'
            )
        }),
        (_('Time and Value'), {
            'fields': (
                'start_date',
                'estimated_time',
                'standard_time',
                'value'
            )
        }),
        (_('Legacy Information'), {
            'classes': ('collapse',),
            'fields': (
                'legacy_id',
                'legacy_key',
                'legacy_kostenstelle_id',
                'legacy_form_artikel_id'
            )
        }),
        (_('Metadata'), {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        })
    ) 