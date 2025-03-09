"""
Models for the products app.

These models represent product-related entities in the ERP system.
This is a consolidated file that combines features from multiple model files.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductCategory(models.Model):
    """
    Product category model for organizing products.
    """

    code = models.CharField(
        max_length=255,
        db_index=True,
        unique=True,
        help_text=_("Unique category code"),
    )
    name = models.CharField(
        max_length=255,
        help_text=_("Category name"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Category description"),
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
        help_text=_("Parent category"),
    )

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class BaseProduct(models.Model):
    """
    Abstract base class for common product fields.
    """

    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Stock Keeping Unit (maps to Nummer in legacy system)"),
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_(
            "ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)",
        ),
    )
    legacy_uid = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("UID in the legacy system"),
    )

    # Names and descriptions
    name = models.CharField(
        max_length=255,
        help_text=_("Product name (maps to Bezeichnung in legacy system)"),
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Product name in English (maps to Bezeichnung_ENG in legacy system)",
        ),
    )
    short_description = models.TextField(
        blank=True,
        help_text=_(
            "Short product description (maps to Beschreibung_kurz in legacy system)",
        ),
    )
    short_description_en = models.TextField(
        blank=True,
        help_text=_("Short product description in English"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Full product description (maps to Beschreibung in legacy system)"),
    )
    description_en = models.TextField(
        blank=True,
        help_text=_("Full product description in English"),
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Search keywords"),
    )

    # Physical attributes
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Product dimensions (LxWxH)"),
    )
    weight = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Weight in grams"),
    )

    # Pricing
    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Retail price (maps to Laden price in legacy system)"),
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Wholesale price (maps to Handel price in legacy system)"),
    )
    gross_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Recommended retail price (maps to Empf. price in legacy system)"),
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Cost price (maps to Einkauf price in legacy system)"),
    )

    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        help_text=_("Current stock quantity"),
    )
    min_stock_quantity = models.IntegerField(
        default=0,
        help_text=_("Minimum stock quantity before reordering"),
    )
    backorder_quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity on backorder"),
    )
    open_purchase_quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity on open purchase orders"),
    )
    last_receipt_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of last stock receipt"),
    )
    last_issue_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of last stock issue"),
    )

    # Sales statistics
    units_sold_current_year = models.IntegerField(
        default=0,
        help_text=_("Units sold in current year"),
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_("Units sold in previous year"),
    )
    revenue_previous_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Revenue in previous year"),
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether the product is active"),
        db_column="is_active",  # Explicit column name
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text=_("Whether the product is discontinued"),
    )

    # Manufacturing flags
    has_bom = models.BooleanField(
        default=False,
        help_text=_("Whether the product has a bill of materials"),
    )

    # Product-specific flags
    is_one_sided = models.BooleanField(
        default=False,
        help_text=_("Whether the product is one-sided"),
    )
    is_hanging = models.BooleanField(
        default=False,
        help_text=_("Whether the product is hanging"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Creation timestamp"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp"),
    )

    # Category
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(class)s_products",
        help_text=_("Product category"),
    )

    class Meta:
        abstract = True


class ParentProduct(BaseProduct):
    """
    Parent product model representing product families.
    Maps to Artikel_Familie in the legacy system.
    """

    base_sku = models.CharField(
        max_length=255,
        db_index=True,
        help_text=_("Base SKU for variants"),
    )
    release_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Release date (maps to Release_date in Artikel_Familie)"),
    )
    is_new = models.BooleanField(
        default=False,
        help_text=_("Whether this is a new product (maps to Neu in Artikel_Familie)"),
    )

    class Meta:
        verbose_name = _("Parent Product")
        verbose_name_plural = _("Parent Products")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class VariantProduct(BaseProduct):
    """
    Variant product model representing specific product variants.
    Maps to Artikel_Variante in the legacy system.
    """

    parent = models.ForeignKey(
        ParentProduct,
        null=True,
        on_delete=models.CASCADE,
        related_name="variants",
        help_text=_(
            "Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie",
        ),
    )
    variant_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_("Variant code"),
    )
    legacy_sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Legacy SKU (maps to alteNummer in Artikel_Variante)"),
    )
    base_sku = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_("Base SKU without variant"),
    )

    # Original legacy system field names - keeping only Familie_ reference
    legacy_familie = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        db_column="familie_",
        help_text=_("Original Familie_ field from Artikel_Variante"),
    )

    # HIGH PRIORITY - Core product data from legacy system
    is_verkaufsartikel = models.BooleanField(
        default=False,
        help_text=_("Whether this is a sales article (maps to Verkaufsartikel in Artikel_Variante)"),
        db_column="is_verkaufsartikel",  # Explicit column name
    )
    release_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Release date (maps to Release_Date in Artikel_Variante)"),
    )
    auslaufdatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Discontinuation date (maps to Auslaufdatum in Artikel_Variante)"),
    )

    # HIGH PRIORITY - Pricing structure from legacy system
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_(
            'Retail price (maps to Preise.Coll[Art="Laden"].Preis in Artikel_Variante)',
        ),
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_(
            'Wholesale price (maps to Preise.Coll[Art="Handel"].Preis in Artikel_Variante)',
        ),
    )
    retail_unit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_(
            'Retail packaging unit (maps to Preise.Coll[Art="Laden"].VE in Artikel_Variante)',
        ),
    )
    wholesale_unit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_(
            'Wholesale packaging unit (maps to Preise.Coll[Art="Handel"].VE in Artikel_Variante)',
        ),
    )

    # Physical attributes
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Color of the variant"),
    )
    size = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_("Size of the variant"),
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Material composition"),
    )
    weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Weight in grams"),
    )
    length_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Length in millimeters"),
    )
    width_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Width in millimeters"),
    )
    height_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Height in millimeters"),
    )

    # Inventory and supply chain
    min_stock_level = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Minimum stock level to maintain"),
    )
    max_stock_level = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum stock level to maintain"),
    )
    current_stock = models.IntegerField(
        default=0,
        help_text=_("Current inventory level"),
    )
    reorder_point = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Point at which to reorder inventory"),
    )
    lead_time_days = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Lead time for replenishment in days"),
    )

    # Sales and performance data
    units_sold_year = models.IntegerField(
        default=0,
        help_text=_("Units sold in current year"),
    )

    # Status and categorization
    is_featured = models.BooleanField(
        default=False,
        help_text=_("Whether this variant is featured"),
    )
    is_new = models.BooleanField(
        default=False,
        help_text=_("Whether this is a new variant"),
    )
    is_bestseller = models.BooleanField(
        default=False,
        help_text=_("Whether this is a bestselling variant"),
    )

    # Timestamps and tracking
    last_ordered_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of last customer order"),
    )

    class Meta:
        verbose_name = _("Variant Product")
        verbose_name_plural = _("Variant Products")
        ordering = ["parent__name", "variant_code"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class Product(models.Model):
    """
    Legacy Product model representing items sold or manufactured.
    This model is kept for backward compatibility during migration.
    """

    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Stock Keeping Unit (maps to ArtNr in legacy system)"),
    )
    base_sku = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_("Base SKU without variant (maps to fk_ArtNr in legacy system)"),
    )
    variant_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_("Variant code (maps to ArtikelArt in legacy system)"),
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_("ID in the legacy system"),
    )
    legacy_sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Legacy SKU (maps to alteNummer in Artikel_Variante)"),
    )

    # Parent-child relationship
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="variants",
        help_text=_("Parent product (for variants)"),
    )
    is_parent = models.BooleanField(
        default=False,
        help_text=_(
            "Whether this is a parent product (maps to Art_Kalkulation records)",
        ),
    )

    # Names and descriptions
    name = models.CharField(
        max_length=255,
        help_text=_("Product name (maps to Bezeichnung in legacy system)"),
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "Product name in English (maps to Bezeichnung_ENG in legacy system)",
        ),
    )
    short_description = models.TextField(
        blank=True,
        help_text=_(
            "Short product description (maps to Beschreibung_kurz in legacy system)",
        ),
    )
    short_description_en = models.TextField(
        blank=True,
        help_text=_("Short product description in English"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Full product description (maps to Beschreibung in legacy system)"),
    )
    description_en = models.TextField(
        blank=True,
        help_text=_("Full product description in English"),
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Search keywords"),
    )

    # Physical attributes
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Product dimensions (LxWxH)"),
    )
    weight = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Weight in grams"),
    )

    # Pricing
    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Retail price (maps to Laden price in legacy system)"),
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Wholesale price (maps to Handel price in legacy system)"),
    )
    gross_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Recommended retail price (maps to Empf. price in legacy system)"),
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Cost price (maps to Einkauf price in legacy system)"),
    )

    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        help_text=_("Current stock quantity"),
    )
    min_stock_quantity = models.IntegerField(
        default=0,
        help_text=_("Minimum stock quantity before reordering"),
    )
    backorder_quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity on backorder"),
    )
    open_purchase_quantity = models.IntegerField(
        default=0,
        help_text=_("Quantity on open purchase orders"),
    )
    last_receipt_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of last stock receipt"),
    )
    last_issue_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of last stock issue"),
    )

    # Sales statistics
    units_sold_current_year = models.IntegerField(
        default=0,
        help_text=_("Units sold in current year"),
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_("Units sold in previous year"),
    )
    revenue_previous_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Revenue in previous year"),
    )

    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether the product is active"),
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text=_("Whether the product is discontinued"),
    )

    # Manufacturing flags
    has_bom = models.BooleanField(
        default=False,
        help_text=_("Whether the product has a bill of materials"),
    )

    # Product-specific flags
    is_one_sided = models.BooleanField(
        default=False,
        help_text=_("Whether the product is one-sided"),
    )
    is_hanging = models.BooleanField(
        default=False,
        help_text=_("Whether the product is hanging"),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Creation timestamp"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp"),
    )

    # Category
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
        help_text=_("Product category"),
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class ProductImage(models.Model):
    """
    Cached information about product images from external system
    """

    product = models.ForeignKey(
        "VariantProduct",
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
        help_text=_("Product this image belongs to"),
    )
    external_id = models.CharField(
        max_length=255,
        help_text=_("ID from external image database"),
    )
    image_url = models.URLField(
        max_length=500,
        help_text=_("URL to the full-size image"),
    )
    thumbnail_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text=_("URL to the thumbnail image"),
    )
    image_type = models.CharField(
        max_length=50,
        help_text=_('Type of image (e.g., "Produktfoto")'),
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("Whether this is the primary image for the product"),
    )
    is_front = models.BooleanField(
        default=False,
        help_text=_('Whether this image is marked as "front" in the source system'),
    )
    priority = models.IntegerField(
        default=0,
        help_text=_("Display priority (lower numbers shown first)"),
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Alternative text for the image"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional metadata from the source system"),
    )
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text=_("When this image record was last updated"),
    )

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        ordering = ["priority", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "external_id"],
                name="unique_product_image",
                condition=models.Q(product__isnull=False),
            ),
        ]

    def __str__(self) -> str:
        return f"Image for {self.product.sku} ({self.image_type})"


class ImageSyncLog(models.Model):
    """
    Track image synchronization history and results
    """

    id = models.BigAutoField(primary_key=True, auto_created=True)
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the sync process started"),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the sync process completed"),
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="in_progress",
        help_text=_("Current status of the sync process"),
    )
    images_added = models.IntegerField(
        default=0,
        help_text=_("Number of new images added"),
    )
    images_updated = models.IntegerField(
        default=0,
        help_text=_("Number of existing images updated"),
    )
    images_deleted = models.IntegerField(
        default=0,
        help_text=_("Number of images deleted"),
    )
    products_affected = models.IntegerField(
        default=0,
        help_text=_("Number of products affected by the sync"),
    )
    error_message = models.TextField(
        blank=True,
        help_text=_("Error message if the sync failed"),
    )

    class Meta:
        verbose_name = _("Image Sync Log")
        verbose_name_plural = _("Image Sync Logs")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return (
            f"Image Sync {self.started_at.strftime('%Y-%m-%d %H:%M')} - {self.status}"
        )


class UnifiedProduct(models.Model):
    """
    New unified Product model that will replace the ParentProduct and VariantProduct models.  # noqa: E501
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(_("Name"), max_length=255)
    sku = models.CharField(_("SKU"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_("Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    # Fields to handle the parent-variant relationship
    is_variant = models.BooleanField(_("Is Variant"), default=False)
    is_parent = models.BooleanField(_("Is Parent"), default=False)
    base_sku = models.CharField(_("Base SKU"), max_length=100, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="variants",
    )

    class Meta:
        verbose_name = _("Unified Product")
        verbose_name_plural = _("Unified Products")

    def __str__(self) -> str:
        return self.name


# For backward compatibility with tests that import from models_new
# This is in addition to the existing Product model class defined above
# Product = UnifiedProduct  # Removed redundant definition
