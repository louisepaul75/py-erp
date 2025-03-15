"""
Admin interface for inventory and warehouse management.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    StorageLocation,
    BoxType,
    Box,
    BoxSlot,
    ProductStorage,
    InventoryMovement,
    BoxStorage,
)


class BoxInline(admin.TabularInline):
    """Inline admin for boxes in a storage location."""
    model = Box
    extra = 0
    fields = ('code', 'box_type', 'status', 'barcode')
    readonly_fields = ('status',)


@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    """Admin interface for storage locations."""
    list_display = (
        'name',
        'country',
        'city_building',
        'unit',
        'compartment',
        'shelf',
        'sale',
        'special_spot',
        'is_active',
    )
    list_filter = (
        'country',
        'city_building',
        'sale',
        'special_spot',
        'is_active',
    )
    search_fields = (
        'name',
        'country',
        'city_building',
        'unit',
        'compartment',
        'shelf',
    )
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active', 'capacity')
        }),
        (_('Location Details'), {
            'fields': (
                'country',
                'city_building',
                'unit',
                'compartment',
                'shelf',
            )
        }),
        (_('Flags'), {
            'fields': ('sale', 'special_spot')
        }),
        (_('Legacy Information'), {
            'fields': ('legacy_id',),
            'classes': ('collapse',),
        }),
    )
    inlines = [BoxInline]


class BoxSlotInline(admin.TabularInline):
    """Inline admin for slots in a box."""
    model = BoxSlot
    extra = 0
    fields = ('slot_code', 'barcode', 'occupied')
    readonly_fields = ('occupied',)


@admin.register(BoxType)
class BoxTypeAdmin(admin.ModelAdmin):
    """Admin interface for box types."""
    list_display = (
        'name',
        'length',
        'width',
        'height',
        'weight_empty',
        'slot_count',
        'slot_naming_scheme',
    )
    list_filter = ('slot_naming_scheme',)
    search_fields = ('name', 'description')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description')
        }),
        (_('Dimensions'), {
            'fields': ('length', 'width', 'height', 'weight_empty')
        }),
        (_('Slot Configuration'), {
            'fields': ('slot_count', 'slot_naming_scheme')
        }),
    )


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    """Admin interface for boxes."""
    list_display = (
        'code',
        'box_type',
        'storage_location',
        'status',
        'available_slots',
    )
    list_filter = ('status', 'box_type', 'storage_location__country')
    search_fields = ('code', 'barcode', 'notes', 'storage_location__name')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('code', 'barcode', 'box_type', 'status', 'notes')
        }),
        (_('Location'), {
            'fields': ('storage_location',)
        }),
    )
    inlines = [BoxSlotInline]
    readonly_fields = ('available_slots',)

    def available_slots(self, obj):
        """Display available slots."""
        return obj.available_slots
    available_slots.short_description = _('Available Slots')


class BoxStorageInline(admin.TabularInline):
    """Inline admin for box storage assignments."""
    model = BoxStorage
    extra = 0
    fields = (
        'product_storage',
        'position_in_slot',
        'quantity',
        'batch_number',
    )


@admin.register(BoxSlot)
class BoxSlotAdmin(admin.ModelAdmin):
    """Admin interface for box slots."""
    list_display = (
        'box',
        'slot_number',
        'slot_code',
        'occupied',
    )
    list_filter = (
        'occupied',
        'box__storage_location__country',
    )
    search_fields = (
        'slot_code',
        'box__code',
    )
    readonly_fields = (
        'box',
        'slot_number',
        'barcode',
        'occupied',
    )
    inlines = [BoxStorageInline]
    
    def occupied(self, obj):
        """Return whether the box slot is occupied."""
        return obj.is_occupied
    occupied.boolean = True
    
    actions = ['mark_available', 'mark_reserved', 'mark_maintenance']
    
    def mark_available(self, request, queryset):
        """Mark selected box slots as available."""
        queryset.update(status=BoxSlot.Status.AVAILABLE)
    mark_available.short_description = _('Mark selected box slots as available')
    
    def mark_reserved(self, request, queryset):
        """Mark selected box slots as reserved."""
        queryset.update(status=BoxSlot.Status.RESERVED)
    mark_reserved.short_description = _('Mark selected box slots as reserved')
    
    def mark_maintenance(self, request, queryset):
        """Mark selected box slots as in maintenance."""
        queryset.update(status=BoxSlot.Status.MAINTENANCE)
    mark_maintenance.short_description = _('Mark selected box slots as in maintenance')


@admin.register(ProductStorage)
class ProductStorageAdmin(admin.ModelAdmin):
    """Admin interface for product storage."""
    list_display = (
        'product',
        'storage_location',
        'quantity',
        'reservation_status',
    )
    list_filter = (
        'reservation_status',
        'storage_location__country',
        'storage_location__city_building',
    )
    search_fields = (
        'product__name',
        'product__sku',
        'reservation_reference',
        'storage_location__location_code',
    )
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product', 'quantity')
        }),
        (_('Storage Location'), {
            'fields': ('storage_location',)
        }),
        (_('Reservation'), {
            'fields': ('reservation_status', 'reservation_reference')
        }),
    )
    inlines = [BoxStorageInline]
    
    def get_inline_instances(self, request, obj=None):
        """Only show inlines when editing an existing object."""
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(BoxStorage)
class BoxStorageAdmin(admin.ModelAdmin):
    """Admin interface for box storage."""
    list_display = (
        'product_storage',
        'box_slot',
        'quantity',
        'batch_number',
        'date_stored',
    )
    list_filter = (
        'date_stored',
        'box_slot__box__storage_location__country',
    )
    search_fields = (
        'product_storage__product__name',
        'product_storage__product__sku',
        'batch_number',
        'box_slot__box__code',
    )
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product_storage', 'quantity', 'batch_number', 'expiry_date')
        }),
        (_('Box Location'), {
            'fields': ('box_slot', 'position_in_slot')
        }),
    )
    readonly_fields = ('date_stored',)
    date_hierarchy = 'date_stored'


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    """Admin interface for inventory movements."""
    list_display = (
        'product',
        'movement_type',
        'quantity',
        'from_slot',
        'to_slot',
        'reference',
        'timestamp',
    )
    list_filter = (
        'movement_type',
        'timestamp',
    )
    search_fields = (
        'product__name',
        'product__sku',
        'reference',
        'notes',
    )
    fieldsets = (
        (_('Movement Details'), {
            'fields': (
                'product',
                'quantity',
                'movement_type',
                'from_slot',
                'to_slot',
            )
        }),
        (_('Reference Information'), {
            'fields': (
                'reference',
                'notes',
            )
        }),
    )
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp' 