"""
Models for inventory and warehouse management.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from pyerp.business_modules.sales.models import SalesModel


class StorageLocation(SalesModel):
    """
    Storage location model for warehouse management.
    
    This model represents physical storage locations in warehouses,
    mapped from the legacy Stamm_Lagerorte table.
    """
    # Legacy system fields
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text=_("Country code (maps to Land_LKZ in legacy system)"),
    )
    city_building = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("City and building (maps to Ort_Gebaeude in legacy system)"),
    )
    sale = models.BooleanField(
        default=False,
        help_text=_("Whether products in this location are for sale (maps to Abverkauf in legacy system)"),
    )
    special_spot = models.BooleanField(
        default=False,
        help_text=_("Whether this is a special storage spot (maps to Sonderlager in legacy system)"),
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Storage unit identifier (maps to Regal in legacy system)"),
    )
    compartment = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Compartment within unit (maps to Fach in legacy system)"),
    )
    shelf = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Shelf identifier (maps to Boden in legacy system)"),
    )
    location_code = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Formatted location code (maps to Lagerort in legacy system)"),
    )
    
    # Additional fields
    name = models.CharField(
        max_length=100,
        help_text=_("Descriptive name for the storage location"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of the storage location"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this storage location is currently active"),
    )
    capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum capacity of the storage location (number of boxes)"),
    )
    
    class Meta:
        verbose_name = _("Storage Location")
        verbose_name_plural = _("Storage Locations")
        app_label = "inventory"
        ordering = ["country", "city_building", "unit", "compartment", "shelf"]
        indexes = [
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["country", "city_building"]),
            models.Index(fields=["unit", "compartment", "shelf"]),
        ]
        unique_together = (
            ("country", "city_building", "unit", "compartment", "shelf"),
        )
    
    def __str__(self):
        """Return a string representation of the storage location."""
        if self.location_code:
            return self.location_code
        return self.name


class BoxType(SalesModel):
    """
    Box type model for defining different types of storage boxes.
    """
    class BoxColor(models.TextChoices):
        BLUE = "blue", _("Blue")
        YELLOW = "yellow", _("Yellow")
        GREEN = "green", _("Green")
        RED = "red", _("Red")
        GRAY = "gray", _("Gray")
        ORANGE = "orange", _("Orange")
        BLACK = "black", _("Black")
        TRANSPARENT = "transparent", _("Transparent")
        WHITE = "white", _("White")
        OTHER = "other", _("Other")

    name = models.CharField(
        max_length=100,
        help_text=_("Name of the box type"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of the box type"),
    )
    color = models.CharField(
        max_length=20,
        choices=BoxColor.choices,
        blank=True,
        help_text=_("Color of the box type"),
    )
    length = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Length of the box in cm"),
    )
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Width of the box in cm"),
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Height of the box in cm"),
    )
    weight_capacity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Maximum weight capacity in kg"),
    )
    slot_count = models.IntegerField(
        default=1,
        help_text=_("Number of slots in this box type"),
    )
    slot_naming_scheme = models.CharField(
        max_length=50,
        default="numeric",
        help_text=_("Naming scheme for slots (numeric, alphabetic, etc.)"),
    )
    
    class Meta:
        verbose_name = _("Box Type")
        verbose_name_plural = _("Box Types")
        app_label = "inventory"
        ordering = ["name"]
    
    def __str__(self):
        """Return a string representation of the box type."""
        return self.name


class Box(SalesModel):
    """
    Box model for physical storage containers.
    """
    class BoxStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", _("Available")
        IN_USE = "IN_USE", _("In Use")
        RESERVED = "RESERVED", _("Reserved")
        DAMAGED = "DAMAGED", _("Damaged")
        RETIRED = "RETIRED", _("Retired")
    
    class BoxPurpose(models.TextChoices):
        STORAGE = "STORAGE", _("Storage")
        PICKING = "PICKING", _("Picking")
        TRANSPORT = "TRANSPORT", _("Transport")
        WORKSHOP = "WORKSHOP", _("Workshop")
    
    code = models.CharField(
        max_length=50,
        help_text=_("Unique code for the box"),
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Barcode for the box"),
    )
    box_type = models.ForeignKey(
        BoxType,
        on_delete=models.PROTECT,
        related_name="boxes",
        help_text=_("Type of box"),
    )
    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.PROTECT,
        related_name="boxes",
        null=True,
        blank=True,
        help_text=_("Storage location where the box is placed"),
    )
    status = models.CharField(
        max_length=20,
        choices=BoxStatus.choices,
        default=BoxStatus.AVAILABLE,
        help_text=_("Current status of the box"),
    )
    purpose = models.CharField(
        max_length=20,
        choices=BoxPurpose.choices,
        default=BoxPurpose.STORAGE,
        help_text=_("Primary purpose of this box"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about the box"),
    )
    
    class Meta:
        verbose_name = _("Box")
        verbose_name_plural = _("Boxes")
        app_label = "inventory"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
        ]
    
    def __str__(self):
        """Return a string representation of the box."""
        return f"{self.code} ({self.box_type})"
    
    @property
    def available_slots(self):
        """Return the number of available slots in this box."""
        return self.slots.filter(occupied=False).count()


class BoxSlot(SalesModel):
    """
    Box slot model for individual storage slots within a box.
    
    Each box slot can contain multiple products, allowing for efficient
    use of storage space. The occupied status is updated automatically
    when products are added or removed from the slot.
    """
    box = models.ForeignKey(
        Box,
        on_delete=models.CASCADE,
        related_name="slots",
        help_text=_("Box containing this slot"),
    )
    legacy_slot_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_(
            "Unique identifier from legacy system (ID_Lager_Schuetten_Slots)"
        ),
    )
    slot_number = models.IntegerField(
        default=1,
        help_text=_(
            "Sequential number within the box (maps to Lfd_Nr in legacy system)"
        ),
    )
    slot_code = models.CharField(
        max_length=20,
        help_text=_("Code for the slot within the box"),
    )
    unit_number = models.IntegerField(
        default=1,
        help_text=_(
            "Unit number within the slot (maps to Einheiten_Nr in legacy system)"
        ),
    )
    color_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_(
            "Color code identifier (maps to Einheitenfabe in legacy system)"
        ),
    )
    order_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Associated order number (maps to Auftrags_Nr in legacy system)"
        ),
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Barcode for the slot"),
    )
    occupied = models.BooleanField(
        default=False,
        help_text=_("Whether the slot is currently occupied"),
    )
    max_products = models.IntegerField(
        default=100,
        help_text=_("Maximum number of different products that can be stored in this slot"),
    )
    
    class Meta:
        verbose_name = _("Box Slot")
        verbose_name_plural = _("Box Slots")
        app_label = "inventory"
        ordering = ["box", "slot_code"]
        unique_together = (("box", "slot_code"),)
    
    def __str__(self):
        """Return a string representation of the box slot."""
        return f"{self.box.code}.{self.slot_code}"
    
    def update_occupied_status(self):
        """Update the occupied status based on whether there are products in the slot."""
        has_products = self.box_storage_items.exists()
        if self.occupied != has_products:
            self.occupied = has_products
            self.save(update_fields=['occupied'])
    
    @property
    def product_count(self):
        """Return the number of different products stored in this slot."""
        return self.box_storage_items.values('product_storage__product').distinct().count()
    
    @property
    def is_full(self):
        """Return whether the slot has reached its maximum product capacity."""
        return self.product_count >= self.max_products
    
    @property
    def available_space(self):
        """Return the number of additional product types that can be added to this slot."""
        return max(0, self.max_products - self.product_count)
    
    def get_products_summary(self):
        """Return a summary of products stored in this slot."""
        return self.box_storage_items.values(
            'product_storage__product__name', 
            'product_storage__product__sku',
            'position_in_slot'
        ).annotate(
            total_quantity=models.Sum('quantity')
        ).order_by('product_storage__product__name')


class ProductStorage(SalesModel):
    """
    Product storage model that maps to the legacy Artikel_Lagerorte table.
    
    This model represents the relationship between products and storage locations,
    tracking inventory quantities at the location level.
    """
    class ReservationStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", _("Available")
        RESERVED = "RESERVED", _("Reserved")
        ALLOCATED = "ALLOCATED", _("Allocated")
        PICKED = "PICKED", _("Picked")
    
    product = models.ForeignKey(
        "products.VariantProduct",
        on_delete=models.PROTECT,
        related_name="storage_locations",
        help_text=_("Product stored in this location"),
    )
    storage_location = models.ForeignKey(
        StorageLocation,
        on_delete=models.PROTECT,
        related_name="stored_products",
        null=True,
        help_text=_("Storage location where the product is stored"),
    )
    quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity of the product in this location (maps to Bestand in legacy system)"),
    )
    reservation_status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.AVAILABLE,
        help_text=_("Current reservation status of the product"),
    )
    reservation_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Reference for the reservation (e.g., order number)"),
    )
    
    class Meta:
        verbose_name = _("Product Storage")
        verbose_name_plural = _("Product Storage")
        app_label = "inventory"
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["storage_location"]),
            models.Index(fields=["reservation_status"]),
        ]
        unique_together = [
            ("product", "storage_location")
        ]
    
    def __str__(self):
        """Return a string representation of the product storage."""
        return f"{self.product} ({self.quantity}) @ {self.storage_location}"


class BoxStorage(SalesModel):
    """
    Box storage model that maps to the legacy Lager_Schuetten table.
    
    This model represents the physical placement of products in specific boxes,
    tracking the box assignments for products stored in locations.
    """
    product_storage = models.ForeignKey(
        ProductStorage,
        on_delete=models.CASCADE,
        related_name="box_assignments",
        help_text=_("Product storage record (maps to UUID_Artikel_Lagerorte in legacy system)"),
    )
    box_slot = models.ForeignKey(
        BoxSlot,
        on_delete=models.PROTECT,
        related_name="box_storage_items",
        help_text=_("Box slot where the product is stored"),
    )
    position_in_slot = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Position identifier within the slot (e.g., front, back, left, right)"),
    )
    quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity of the product in this box slot"),
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Batch or lot number for the product"),
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Expiry date for the product"),
    )
    date_stored = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date and time when the product was stored"),
    )
    
    class Meta:
        verbose_name = _("Box Storage")
        verbose_name_plural = _("Box Storage")
        app_label = "inventory"
        ordering = ["-date_stored"]
        indexes = [
            models.Index(fields=["product_storage"]),
            models.Index(fields=["box_slot"]),
            models.Index(fields=["batch_number"]),
        ]
        unique_together = [
            ("box_slot", "product_storage", "batch_number", "position_in_slot")
        ]
    
    def __str__(self):
        """Return a string representation of the box storage."""
        position_info = f" [{self.position_in_slot}]" if self.position_in_slot else ""
        product_info = f"{self.product_storage.product}" if self.product_storage else "Unknown product"
        return f"{product_info} ({self.quantity}){position_info} @ {self.box_slot}"
    
    def save(self, *args, **kwargs):
        """Update box slot status when saving box storage."""
        super().save(*args, **kwargs)
        # Update the occupied status of the box slot
        self.box_slot.update_occupied_status()


class InventoryMovement(SalesModel):
    """
    Inventory movement model for tracking product movements.
    """
    class MovementType(models.TextChoices):
        RECEIPT = "RECEIPT", _("Receipt")
        TRANSFER = "TRANSFER", _("Transfer")
        PICK = "PICK", _("Pick")
        RETURN = "RETURN", _("Return")
        ADJUSTMENT = "ADJUSTMENT", _("Adjustment")
        DISPOSAL = "DISPOSAL", _("Disposal")
    
    product = models.ForeignKey(
        "products.VariantProduct",
        on_delete=models.PROTECT,
        related_name="inventory_movements",
        help_text=_("Product being moved"),
    )
    from_slot = models.ForeignKey(
        BoxSlot,
        on_delete=models.PROTECT,
        related_name="outgoing_movements",
        null=True,
        blank=True,
        help_text=_("Box slot the product is moved from"),
    )
    to_slot = models.ForeignKey(
        BoxSlot,
        on_delete=models.PROTECT,
        related_name="incoming_movements",
        null=True,
        blank=True,
        help_text=_("Box slot the product is moved to"),
    )
    quantity = models.IntegerField(
        help_text=_("Quantity of the product moved"),
    )
    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices,
        help_text=_("Type of movement"),
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Reference for the movement (e.g., order number)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about the movement"),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date and time of the movement"),
    )
    
    class Meta:
        verbose_name = _("Inventory Movement")
        verbose_name_plural = _("Inventory Movements")
        app_label = "inventory"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["timestamp"]),
        ]
    
    def __str__(self):
        """Return a string representation of the inventory movement."""
        return f"{self.movement_type}: {self.product} ({self.quantity})" 