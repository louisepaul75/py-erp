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
        'weight_capacity',
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
            'fields': ('length', 'width', 'height', 'weight_capacity')
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


class ProductStorageInline(admin.TabularInline):
    """Inline admin for products in a box slot."""
    model = ProductStorage
    extra = 0
    fields = (
        'product',
        'quantity',
        'reservation_status',
        'reservation_reference',
        'batch_number',
    )


@admin.register(BoxSlot)
class BoxSlotAdmin(admin.ModelAdmin):
    """Admin interface for box slots."""
    list_display = (
        '__str__',
        'box',
        'slot_code',
        'occupied',
    )
    list_filter = ('occupied', 'box__box_type')
    search_fields = ('slot_code', 'barcode', 'box__code')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('box', 'slot_code', 'barcode')
        }),
        (_('Status'), {
            'fields': ('occupied',)
        }),
    )
    inlines = [ProductStorageInline]
    readonly_fields = ('occupied',)


@admin.register(ProductStorage)
class ProductStorageAdmin(admin.ModelAdmin):
    """Admin interface for product storage."""
    list_display = (
        'product',
        'box_slot',
        'quantity',
        'reservation_status',
        'batch_number',
        'date_stored',
    )
    list_filter = (
        'reservation_status',
        'date_stored',
        'box_slot__box__storage_location__country',
    )
    search_fields = (
        'product__name',
        'product__sku',
        'batch_number',
        'reservation_reference',
        'box_slot__box__code',
    )
    fieldsets = (
        (_('Product Information'), {
            'fields': ('product', 'quantity', 'batch_number', 'expiry_date')
        }),
        (_('Storage Location'), {
            'fields': ('box_slot',)
        }),
        (_('Reservation'), {
            'fields': ('reservation_status', 'reservation_reference')
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