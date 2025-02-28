"""
Models for the products app.

These models represent product-related entities in the ERP system,
with only essential fields required for import.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ProductCategory(models.Model):
    """
    Product category model for organizing products.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Unique category code')
    )
    name = models.CharField(
        max_length=100,
        help_text=_('Category name')
    )
    
    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BaseProduct(models.Model):
    """
    Abstract base class for common product fields.
    """
    # Basic identification
    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Stock Keeping Unit (maps to Nummer in legacy system)')
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_('ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)')
    )
    
    # Basic information
    name = models.CharField(
        max_length=255,
        help_text=_('Product name (maps to Bezeichnung in legacy system)')
    )
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the product is active')
    )
    
    class Meta:
        abstract = True


class ParentProduct(BaseProduct):
    """
    Parent product model representing product families.
    Maps to Artikel_Familie in the legacy system.
    """
    # Additional fields specific to parent products
    base_sku = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_('Base SKU for variants')
    )
    
    is_placeholder = models.BooleanField(
        default=False,
        help_text=_('Indicates if this is a placeholder parent created for orphaned variants')
    )
    
    class Meta:
        verbose_name = _('Parent Product')
        verbose_name_plural = _('Parent Products')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


class VariantProduct(BaseProduct):
    """
    Variant product model representing specific product variants.
    Maps to Artikel_Variante in the legacy system.
    """
    # Variant-specific fields
    parent = models.ForeignKey(
        ParentProduct,
        null=True,
        on_delete=models.CASCADE,
        related_name='variants',
        help_text=_('Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie')
    )
    variant_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Variant code')
    )
    legacy_sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Legacy SKU (maps to alteNummer in Artikel_Variante)')
    )
    base_sku = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_('Base SKU without variant')
    )
    
    # Original legacy system field names - keeping only Familie_ reference
    legacy_familie = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Original Familie_ field from Artikel_Variante'),
        db_column='Familie_'  # Actual column name in the database
    )
    
    # HIGH PRIORITY - Core product data from legacy system
    is_verkaufsartikel = models.BooleanField(
        default=False,
        help_text=_('Whether this is a sales article (maps to Verkaufsartikel in Artikel_Variante)')
    )
    release_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Release date (maps to Release_Date in Artikel_Variante)')
    )
    auslaufdatum = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Discontinuation date (maps to Auslaufdatum in Artikel_Variante)')
    )
    
    # HIGH PRIORITY - Pricing structure from legacy system
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Retail price (maps to Preise.Coll[Art="Laden"].Preis in Artikel_Variante)')
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Wholesale price (maps to Preise.Coll[Art="Handel"].Preis in Artikel_Variante)')
    )
    retail_unit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Retail packaging unit (maps to Preise.Coll[Art="Laden"].VE in Artikel_Variante)')
    )
    wholesale_unit = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Wholesale packaging unit (maps to Preise.Coll[Art="Handel"].VE in Artikel_Variante)')
    )
    
    # Physical attributes
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Color of the variant')
    )
    size = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Size of the variant')
    )
    material = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Material composition')
    )
    weight_grams = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Weight in grams')
    )
    length_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Length in millimeters')
    )
    width_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Width in millimeters')
    )
    height_mm = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Height in millimeters')
    )
    
    # Inventory and supply chain
    min_stock_level = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Minimum stock level to maintain')
    )
    max_stock_level = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum stock level to maintain')
    )
    current_stock = models.IntegerField(
        default=0,
        help_text=_('Current inventory level')
    )
    reorder_point = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Point at which to reorder inventory')
    )
    lead_time_days = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Lead time for replenishment in days')
    )
    
    # Sales and performance data
    units_sold_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in current year')
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in previous year')
    )
    
    # Status and categorization
    is_featured = models.BooleanField(
        default=False,
        help_text=_('Whether this variant is featured')
    )
    is_new = models.BooleanField(
        default=False,
        help_text=_('Whether this is a new variant')
    )
    is_bestseller = models.BooleanField(
        default=False,
        help_text=_('Whether this is a bestselling variant')
    )
    
    # Timestamps and tracking
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text=_('Creation timestamp')
    )
    updated_at = models.DateTimeField(
        default=timezone.now,
        help_text=_('Last update timestamp')
    )
    last_ordered_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date when this variant was last ordered')
    )
    
    class Meta:
        verbose_name = _('Variant Product')
        verbose_name_plural = _('Variant Products')
        ordering = ['parent__name', 'variant_code']


class ProductImage(models.Model):
    """
    Cached information about product images from external system
    """
    product = models.ForeignKey(
        'VariantProduct', 
        on_delete=models.CASCADE, 
        related_name='images',
        help_text=_('Product this image belongs to')
    )
    external_id = models.CharField(
        max_length=255, 
        help_text=_('ID from external image database')
    )
    image_url = models.URLField(
        max_length=500,
        help_text=_('URL to the full-size image')
    )
    thumbnail_url = models.URLField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text=_('URL to the thumbnail image')
    )
    image_type = models.CharField(
        max_length=50, 
        help_text=_('Type of image (e.g., "Produktfoto")')
    )
    is_primary = models.BooleanField(
        default=False, 
        help_text=_('Whether this is the primary image for the product')
    )
    is_front = models.BooleanField(
        default=False, 
        help_text=_('Whether this image is marked as "front" in the source system')
    )
    priority = models.IntegerField(
        default=0, 
        help_text=_('Display priority (lower numbers shown first)')
    )
    alt_text = models.CharField(
        max_length=255, 
        blank=True,
        help_text=_('Alternative text for the image')
    )
    metadata = models.JSONField(
        default=dict, 
        blank=True, 
        help_text=_('Additional metadata from the source system')
    )
    last_synced = models.DateTimeField(
        auto_now=True,
        help_text=_('When the image was last synced from the external system')
    )
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['priority', 'id']
        unique_together = [('product', 'external_id')]
    
    def __str__(self):
        return f"Image for {self.product.sku} - {self.image_type}"


class ImageSyncLog(models.Model):
    """
    Track image synchronization history and results
    """
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the sync process started')
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_('When the sync process completed')
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='in_progress',
        help_text=_('Current status of the sync process')
    )
    images_added = models.IntegerField(
        default=0,
        help_text=_('Number of new images added')
    )
    images_updated = models.IntegerField(
        default=0,
        help_text=_('Number of existing images updated')
    )
    images_deleted = models.IntegerField(
        default=0,
        help_text=_('Number of images deleted')
    )
    products_affected = models.IntegerField(
        default=0,
        help_text=_('Number of products affected by the sync')
    )
    error_message = models.TextField(
        blank=True,
        help_text=_('Error message if the sync failed')
    )
    
    class Meta:
        verbose_name = _('Image Sync Log')
        verbose_name_plural = _('Image Sync Logs')
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Image sync {self.pk} - {self.status} - {self.started_at}" 