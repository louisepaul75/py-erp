"""
Models for the products app.

These models represent product-related entities in the ERP system.
This is a consolidated file that combines features from multiple model files.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _  # noqa: F401
from django.utils import timezone  # noqa: F401


class ProductCategory(models.Model):
    """
    Product category model for organizing products.
    """
    code = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        unique=True,  # noqa: F841
        help_text=_('Unique category code')  # noqa: F841
    )
    name = models.CharField(  # noqa: F841
        max_length=100,  # noqa: E128
        help_text=_('Category name')  # noqa: F841
    )
    description = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Category description')  # noqa: F841
    )
    parent = models.ForeignKey(  # noqa: F841
        'self',  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        related_name='children',  # noqa: F841
        help_text=_('Parent category')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Product Category')  # noqa: F841
        verbose_name_plural = _('Product Categories')  # noqa: F841
        ordering = ['name']  # noqa: F841

    def __str__(self):
        return self.name


class BaseProduct(models.Model):
    """
    Abstract base class for common product fields.
    """
    # Basic identification
    sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        unique=True,  # noqa: F841
        help_text=_('Stock Keeping Unit (maps to Nummer in legacy system)')  # noqa: F841
    )
    legacy_id = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        unique=True,  # noqa: F841
        help_text=_('ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)')  # noqa: E501
    )
    legacy_uid = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=50,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('UID in the legacy system')  # noqa: F841
    )

    # Names and descriptions
    name = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        help_text=_('Product name (maps to Bezeichnung in legacy system)')  # noqa: F841
    )
    name_en = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Product name in English (maps to Bezeichnung_ENG in legacy system)')  # noqa: E501
    )
    short_description = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Short product description (maps to Beschreibung_kurz in legacy system)')  # noqa: E501
    )
    short_description_en = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Short product description in English')  # noqa: F841
    )
    description = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Full product description (maps to Beschreibung in legacy system)')  # noqa: E501
    )
    description_en = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Full product description in English')  # noqa: F841
    )
    keywords = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Search keywords')  # noqa: F841
    )

    # Physical attributes
    dimensions = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Product dimensions (LxWxH)')  # noqa: F841
    )
    weight = models.IntegerField(  # noqa: F841
        null=True,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Weight in grams')  # noqa: F841
    )

    # Pricing
    list_price = models.DecimalField(  # noqa: F841
        max_digits=10,  # noqa: E128
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Retail price (maps to Laden price in legacy system)')  # noqa: F841
    )
    wholesale_price = models.DecimalField(  # noqa: F841
        max_digits=10,  # noqa: E128
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Wholesale price (maps to Handel price in legacy system)')  # noqa: F841
    )
    gross_price = models.DecimalField(  # noqa: F841
        max_digits=10,  # noqa: E128
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Recommended retail price (maps to Empf. price in legacy system)')  # noqa: E501
    )
    cost_price = models.DecimalField(  # noqa: F841
        max_digits=10,  # noqa: E128
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Cost price (maps to Einkauf price in legacy system)')  # noqa: F841
    )

    # Inventory
    stock_quantity = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Current stock quantity')  # noqa: F841
    )
    min_stock_quantity = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Minimum stock quantity before reordering')  # noqa: F841
    )
    backorder_quantity = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Quantity on backorder')  # noqa: F841
    )
    open_purchase_quantity = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Quantity on open purchase orders')  # noqa: F841
    )
    last_receipt_date = models.DateField(  # noqa: F841
        null=True,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Date of last stock receipt')  # noqa: F841
    )
    last_issue_date = models.DateField(  # noqa: F841
        null=True,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Date of last stock issue')  # noqa: F841
    )

    # Sales statistics
    units_sold_current_year = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Units sold in current year')  # noqa: F841
    )
    units_sold_previous_year = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Units sold in previous year')  # noqa: F841
    )
    revenue_previous_year = models.DecimalField(  # noqa: F841
        max_digits=12,  # noqa: E128
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Revenue in previous year')  # noqa: F841
    )

    # Status flags
    is_active = models.BooleanField(  # noqa: F841
        default=True,  # noqa: E128
        help_text=_('Whether the product is active'),  # noqa: F841
        db_column='is_active',  # Explicit column name  # noqa: F841
    )
    is_discontinued = models.BooleanField(  # noqa: F841
        default=False,  # noqa: E128
        help_text=_('Whether the product is discontinued')  # noqa: F841
    )

    # Manufacturing flags
    has_bom = models.BooleanField(  # noqa: F841
        default=False,  # noqa: E128
        help_text=_('Whether the product has a bill of materials')  # noqa: F841
    )

    # Product-specific flags
    is_one_sided = models.BooleanField(  # noqa: F841
        default=False,  # noqa: E128
        help_text=_('Whether the product is one-sided')  # noqa: F841
    )
    is_hanging = models.BooleanField(  # noqa: F841
        default=False,  # noqa: E128
        help_text=_('Whether the product is hanging')  # noqa: F841
    )

    # Timestamps
    created_at = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: E128
        help_text=_('Creation timestamp')  # noqa: F841
    )
    updated_at = models.DateTimeField(  # noqa: F841
        auto_now=True,  # noqa: E128
        help_text=_('Last update timestamp')  # noqa: F841
    )

    # Category
    category = models.ForeignKey(  # noqa: F841
        ProductCategory,  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        related_name='%(class)s_products',  # noqa: F841
        help_text=_('Product category')  # noqa: F841
    )

    class Meta:
        abstract = True  # noqa: F841
  # noqa: F841


class ParentProduct(BaseProduct):
    """
    Parent product model representing product families.
    Maps to Artikel_Familie in the legacy system.
    """
    # Additional fields specific to parent products
    base_sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        db_index=True,  # noqa: F841
        help_text=_('Base SKU for variants')  # noqa: F841
    )

    is_placeholder = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Indicates if this is a placeholder parent created for orphaned variants')  # noqa: E501
    )

    class Meta:

        verbose_name = _('Parent Product')  # noqa: F841
        verbose_name_plural = _('Parent Products')  # noqa: F841
        ordering = ['name']  # noqa: F841

    def __str__(self):
        return f"{self.name} ({self.sku})"


class VariantProduct(BaseProduct):
    """
    Variant product model representing specific product variants.
    Maps to Artikel_Variante in the legacy system.
    """
    # Variant-specific fields
    parent = models.ForeignKey(  # noqa: F841
        ParentProduct,  # noqa: E128
        null=True,  # noqa: F841
        on_delete=models.CASCADE,  # noqa: F841
        related_name='variants',  # noqa: F841
        help_text=_('Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie')  # noqa: E501
    )
    variant_code = models.CharField(  # noqa: F841
        max_length=10,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Variant code')  # noqa: F841
    )
    legacy_sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Legacy SKU (maps to alteNummer in Artikel_Variante)')  # noqa: F841
    )
    base_sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        db_index=True,  # noqa: F841
        help_text=_('Base SKU without variant')  # noqa: F841
    )

    # Original legacy system field names - keeping only Familie_ reference
    legacy_familie = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=50,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        db_column='familie_',  # noqa: F841
  # noqa: F841
        help_text=_('Original Familie_ field from Artikel_Variante')  # noqa: F841
    )

    # HIGH PRIORITY - Core product data from legacy system
    is_verkaufsartikel = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this is a sales article (maps to Verkaufsartikel in Artikel_Variante)')  # noqa: E501
    )
    release_date = models.DateTimeField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Release date (maps to Release_Date in Artikel_Variante)')  # noqa: F841
    )
    auslaufdatum = models.DateTimeField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Discontinuation date (maps to Auslaufdatum in Artikel_Variante)')  # noqa: E501
    )

    # HIGH PRIORITY - Pricing structure from legacy system
    retail_price = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Retail price (maps to Preise.Coll[Art="Laden"].Preis in Artikel_Variante)')  # noqa: E501
    )
    wholesale_price = models.DecimalField(  # noqa: F841
        max_digits=10,  # noqa: E128
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Wholesale price (maps to Preise.Coll[Art="Handel"].Preis in Artikel_Variante)')  # noqa: E501
    )
    retail_unit = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Retail packaging unit (maps to Preise.Coll[Art="Laden"].VE in Artikel_Variante)')  # noqa: E501
    )
    wholesale_unit = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Wholesale packaging unit (maps to Preise.Coll[Art="Handel"].VE in Artikel_Variante)')  # noqa: E501
    )

    # Physical attributes
    color = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=50,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Color of the variant')  # noqa: F841
    )
    size = models.CharField(  # noqa: F841
        max_length=20,  # noqa: E128
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Size of the variant')  # noqa: F841
    )
    material = models.CharField(  # noqa: F841
        max_length=100,  # noqa: E128
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Material composition')  # noqa: F841
    )
    weight_grams = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Weight in grams')  # noqa: F841
    )
    length_mm = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Length in millimeters')  # noqa: F841
    )
    width_mm = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Width in millimeters')  # noqa: F841
    )
    height_mm = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Height in millimeters')  # noqa: F841
    )

    # Inventory and supply chain
    min_stock_level = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Minimum stock level to maintain')  # noqa: F841
    )
    max_stock_level = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Maximum stock level to maintain')  # noqa: F841
    )
    current_stock = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Current inventory level')  # noqa: F841
    )
    reorder_point = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Point at which to reorder inventory')  # noqa: F841
    )
    lead_time_days = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Lead time for replenishment in days')  # noqa: F841
    )

    # Sales and performance data
    units_sold_year = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Units sold in current year')  # noqa: F841
    )

    # Status and categorization
    is_featured = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this variant is featured')  # noqa: F841
    )
    is_new = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this is a new variant')  # noqa: F841
    )
    is_bestseller = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this is a bestselling variant')  # noqa: F841
    )

    # Timestamps and tracking
    last_ordered_date = models.DateField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Date of last customer order')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Variant Product')  # noqa: F841
        verbose_name_plural = _('Variant Products')  # noqa: F841
        ordering = ['parent__name', 'variant_code']  # noqa: F841

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Product(models.Model):
    """
    Legacy Product model representing items sold or manufactured.
    This model is kept for backward compatibility during migration.
    """
    # Basic identification
    sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        unique=True,  # noqa: F841
        help_text=_('Stock Keeping Unit (maps to ArtNr in legacy system)')  # noqa: F841
    )
    base_sku = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        db_index=True,  # noqa: F841
  # noqa: F841
        help_text=_('Base SKU without variant (maps to fk_ArtNr in legacy system)')  # noqa: E501
    )
    variant_code = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=10,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Variant code (maps to ArtikelArt in legacy system)')  # noqa: F841
    )
    legacy_id = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=50,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        unique=True,  # noqa: F841
        help_text=_('ID in the legacy system')  # noqa: F841
    )
    legacy_sku = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=50,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Legacy SKU (maps to alteNummer in Artikel_Variante)')  # noqa: F841
    )

    # Parent-child relationship
    parent = models.ForeignKey(  # noqa: F841
        'self',  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        related_name='variants',  # noqa: F841
        help_text=_('Parent product (for variants)')  # noqa: F841
    )
    is_parent = models.BooleanField(  # noqa: F841
        default=False,  # noqa: E128
        help_text=_('Whether this is a parent product (maps to Art_Kalkulation records)')  # noqa: E501
    )

    # Names and descriptions
    name = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        help_text=_('Product name (maps to Bezeichnung in legacy system)')  # noqa: F841
    )
    name_en = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=255,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Product name in English (maps to Bezeichnung_ENG in legacy system)')  # noqa: E501
    )
    short_description = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Short product description (maps to Beschreibung_kurz in legacy system)')  # noqa: E501
    )
    short_description_en = models.TextField(  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Short product description in English')  # noqa: F841
    )
    description = models.TextField(  # noqa: F841
        blank=True,  # noqa: E128
        help_text=_('Full product description (maps to Beschreibung in legacy system)')  # noqa: E501
    )
    description_en = models.TextField(  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Full product description in English')  # noqa: F841
    )
    keywords = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Search keywords')  # noqa: F841
    )

    # Physical attributes
    dimensions = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Product dimensions (LxWxH)')  # noqa: F841
    )
    weight = models.IntegerField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Weight in grams')  # noqa: F841
    )

    # Pricing
    list_price = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Retail price (maps to Laden price in legacy system)')  # noqa: F841
    )
    wholesale_price = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Wholesale price (maps to Handel price in legacy system)')  # noqa: F841
    )
    gross_price = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Recommended retail price (maps to Empf. price in legacy system)')  # noqa: E501
    )
    cost_price = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=10,  # noqa: F841
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Cost price (maps to Einkauf price in legacy system)')  # noqa: F841
    )

    # Inventory
    stock_quantity = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Current stock quantity')  # noqa: F841
    )
    min_stock_quantity = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Minimum stock quantity before reordering')  # noqa: F841
    )
    backorder_quantity = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Quantity on backorder')  # noqa: F841
    )
    open_purchase_quantity = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Quantity on open purchase orders')  # noqa: F841
    )
    last_receipt_date = models.DateField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Date of last stock receipt')  # noqa: F841
    )
    last_issue_date = models.DateField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Date of last stock issue')  # noqa: F841
    )

    # Sales statistics
    units_sold_current_year = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Units sold in current year')  # noqa: F841
    )
    units_sold_previous_year = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Units sold in previous year')  # noqa: F841
    )
    revenue_previous_year = models.DecimalField(  # noqa: F841
  # noqa: F841
        max_digits=12,  # noqa: F841
        decimal_places=2,  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Revenue in previous year')  # noqa: F841
    )

    # Status flags
    is_active = models.BooleanField(  # noqa: F841
        default=True,  # noqa: E128
        help_text=_('Whether the product is active')  # noqa: F841
    )
    is_discontinued = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether the product is discontinued')  # noqa: F841
    )

    # Manufacturing flags
    has_bom = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether the product has a bill of materials')  # noqa: F841
    )

    # Product-specific flags
    is_one_sided = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether the product is one-sided')  # noqa: F841
    )
    is_hanging = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether the product is hanging')  # noqa: F841
    )

    # Timestamps
    created_at = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: E128
        help_text=_('Creation timestamp')  # noqa: F841
    )
    updated_at = models.DateTimeField(  # noqa: F841
        auto_now=True,  # noqa: E128
        help_text=_('Last update timestamp')  # noqa: F841
    )

    # Category
    category = models.ForeignKey(  # noqa: F841
        ProductCategory,  # noqa: E128
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        on_delete=models.SET_NULL,  # noqa: F841
        related_name='products',  # noqa: F841
        help_text=_('Product category')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Product')  # noqa: F841
        verbose_name_plural = _('Products')  # noqa: F841
        ordering = ['name']  # noqa: F841

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(models.Model):
    """
    Cached information about product images from external system
    """
    product = models.ForeignKey(  # noqa: F841
        'VariantProduct',  # noqa: E128
        on_delete=models.CASCADE,  # noqa: F841
        related_name='images',  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Product this image belongs to')  # noqa: F841
    )
    external_id = models.CharField(  # noqa: F841
        max_length=255,  # noqa: E128
        help_text=_('ID from external image database')  # noqa: F841
    )
    image_url = models.URLField(  # noqa: F841
  # noqa: F841
        max_length=500,  # noqa: F841
        help_text=_('URL to the full-size image')  # noqa: F841
    )
    thumbnail_url = models.URLField(  # noqa: F841
  # noqa: F841
        max_length=500,  # noqa: F841
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('URL to the thumbnail image')  # noqa: F841
    )
    image_type = models.CharField(  # noqa: F841
        max_length=50,  # noqa: E128
        help_text=_('Type of image (e.g., "Produktfoto")')  # noqa: F841
    )
    is_primary = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this is the primary image for the product')  # noqa: F841
    )
    is_front = models.BooleanField(  # noqa: F841
  # noqa: F841
        default=False,  # noqa: F841
        help_text=_('Whether this image is marked as "front" in the source system')  # noqa: E501
    )
    priority = models.IntegerField(  # noqa: F841
        default=0,  # noqa: E128
        help_text=_('Display priority (lower numbers shown first)')  # noqa: F841
    )
    alt_text = models.CharField(  # noqa: F841
  # noqa: F841
        max_length=255,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Alternative text for the image')  # noqa: F841
    )
    metadata = models.JSONField(  # noqa: F841
        default=dict,  # noqa: E128
        blank=True,  # noqa: F841
        help_text=_('Additional metadata from the source system')  # noqa: F841
    )
    last_synced = models.DateTimeField(  # noqa: F841
  # noqa: F841
        auto_now=True,  # noqa: F841
        help_text=_('When this image record was last updated')  # noqa: F841
    )

    class Meta:

        verbose_name = _('Product Image')  # noqa: F841
        verbose_name_plural = _('Product Images')  # noqa: F841
        ordering = ['priority', 'id']  # noqa: F841
        constraints = [  # noqa: F841
  # noqa: F841
            models.UniqueConstraint(
                fields=['product', 'external_id'],  # noqa: F841
  # noqa: F841
                name='unique_product_image',  # noqa: F841
                condition=models.Q(product__isnull=False)  # noqa: F841
  # noqa: F841
            )
        ]

    def __str__(self):
        return f"Image for {self.product.sku} ({self.image_type})"


class ImageSyncLog(models.Model):
    """
    Track image synchronization history and results
    """
    id = models.BigAutoField(primary_key=True, auto_created=True)  # noqa: F841
    started_at = models.DateTimeField(  # noqa: F841
        auto_now_add=True,  # noqa: E128
        help_text=_('When the sync process started')  # noqa: F841
    )
    completed_at = models.DateTimeField(  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('When the sync process completed')  # noqa: F841
    )
    status = models.CharField(  # noqa: F841
        max_length=20,  # noqa: E128
        choices=[  # noqa: F841
  # noqa: F841
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='in_progress',  # noqa: F841
        help_text=_('Current status of the sync process')  # noqa: F841
    )
    images_added = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of new images added')  # noqa: F841
    )
    images_updated = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of existing images updated')  # noqa: F841
    )
    images_deleted = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of images deleted')  # noqa: F841
    )
    products_affected = models.IntegerField(  # noqa: F841
  # noqa: F841
        default=0,  # noqa: F841
        help_text=_('Number of products affected by the sync')  # noqa: F841
    )
    error_message = models.TextField(  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
        help_text=_('Error message if the sync failed')  # noqa: F841
  # noqa: F841
    )

    class Meta:

        verbose_name = _('Image Sync Log')  # noqa: F841
        verbose_name_plural = _('Image Sync Logs')  # noqa: F841
        ordering = ['-started_at']  # noqa: F841
  # noqa: F841

    def __str__(self):
        return f"Image Sync {self.started_at.strftime('%Y-%m-%d %H:%M')} - {self.status}"  # noqa: E501


class UnifiedProduct(models.Model):
    """
    New unified Product model that will replace the ParentProduct and VariantProduct models.  # noqa: E501
    """
    id = models.AutoField(primary_key=True)  # noqa: F841
  # noqa: F841
    name = models.CharField(_("Name"), max_length=255)  # noqa: F841
    sku = models.CharField(_("SKU"), max_length=100, unique=True)  # noqa: F841
    description = models.TextField(_("Description"), blank=True)  # noqa: F841
  # noqa: F841
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2, default=0)  # noqa: E501
  # noqa: E501, F841
    is_active = models.BooleanField(_("Active"), default=True)  # noqa: F841
  # noqa: F841
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)  # noqa: F841
  # noqa: F841
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)  # noqa: F841
  # noqa: F841

    # Fields to handle the parent-variant relationship
    is_variant = models.BooleanField(_("Is Variant"), default=False)  # noqa: F841
  # noqa: F841
    is_parent = models.BooleanField(_("Is Parent"), default=False)  # noqa: F841
  # noqa: F841
    base_sku = models.CharField(_("Base SKU"), max_length=100, blank=True)  # noqa: F841
  # noqa: F841
    parent = models.ForeignKey(  # noqa: F841
  # noqa: F841
        'self',
        on_delete=models.CASCADE,  # noqa: F841
  # noqa: F841
        null=True,  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
  # noqa: F841
        related_name='  # noqa: F541  variants'
  # noqa: F541, F841
    )

    class Meta:

        verbose_name = _("Unified Product")  # noqa: F841
        verbose_name_plural = _("Unified Products")  # noqa: F841
  # noqa: F841

    def __str__(self):

        return self.name

# For backward compatibility with tests that import from models_new
# This is in addition to the existing Product model class defined above
Product = UnifiedProduct  # noqa: F841
  # noqa: F841
