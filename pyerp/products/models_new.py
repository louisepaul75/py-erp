from django.db import models
from django.utils.translation import gettext_lazy as _


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
    description = models.TextField(
        blank=True,
        help_text=_('Category description')
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text=_('Parent category')
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
        help_text=_('Stock Keeping Unit (maps to ArtNr in legacy system)')
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_('ID in the legacy system')
    )
    
    # Names and descriptions
    name = models.CharField(
        max_length=255,
        help_text=_('Product name (maps to Bezeichnung in legacy system)')
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Product name in English (maps to Bezeichnung_ENG in legacy system)')
    )
    short_description = models.TextField(
        blank=True,
        help_text=_('Short product description (maps to Beschreibung_kurz in legacy system)')
    )
    short_description_en = models.TextField(
        blank=True,
        help_text=_('Short product description in English')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Full product description (maps to Beschreibung in legacy system)')
    )
    description_en = models.TextField(
        blank=True,
        help_text=_('Full product description in English')
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Search keywords')
    )
    
    # Physical attributes
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Product dimensions (LxWxH)')
    )
    weight = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Weight in grams')
    )
    
    # Pricing
    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Retail price (maps to Laden price in legacy system)')
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Wholesale price (maps to Handel price in legacy system)')
    )
    gross_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Recommended retail price (maps to Empf. price in legacy system)')
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Cost price (maps to Einkauf price in legacy system)')
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Current stock quantity')
    )
    min_stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Minimum stock quantity before reordering')
    )
    backorder_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on backorder')
    )
    open_purchase_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on open purchase orders')
    )
    last_receipt_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock receipt')
    )
    last_issue_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock issue')
    )
    
    # Sales statistics
    units_sold_current_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in current year')
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in previous year')
    )
    revenue_previous_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_('Revenue in previous year')
    )
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the product is active')
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text=_('Whether the product is discontinued')
    )
    
    # Manufacturing flags
    has_bom = models.BooleanField(
        default=False,
        help_text=_('Whether the product has a bill of materials')
    )
    
    # Product-specific flags
    is_one_sided = models.BooleanField(
        default=False,
        help_text=_('Whether the product is one-sided')
    )
    is_hanging = models.BooleanField(
        default=False,
        help_text=_('Whether the product is hanging')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Creation timestamp')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Last update timestamp')
    )
    
    # Category
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(class)s_products',
        help_text=_('Product category')
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
        on_delete=models.CASCADE,
        related_name='variants',
        help_text=_('Parent product')
    )
    variant_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Variant code (maps to ArtikelArt in legacy system)')
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
        help_text=_('Base SKU without variant (maps to fk_ArtNr in legacy system)')
    )
    
    class Meta:
        verbose_name = _('Variant Product')
        verbose_name_plural = _('Variant Products')
        ordering = ['parent__name', 'variant_code']
        unique_together = [['parent', 'variant_code']]
    
    def __str__(self):
        return f"{self.name} ({self.sku})"


# Keep the original Product model for backward compatibility during migration
class Product(models.Model):
    """
    Legacy Product model representing items sold or manufactured.
    This model is kept for backward compatibility during migration.
    """
    # Basic identification
    sku = models.CharField(
        max_length=50,
        unique=True,
        help_text=_('Stock Keeping Unit (maps to ArtNr in legacy system)')
    )
    base_sku = models.CharField(
        max_length=50,
        db_index=True,
        help_text=_('Base SKU without variant (maps to fk_ArtNr in legacy system)')
    )
    variant_code = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Variant code (maps to ArtikelArt in legacy system)')
    )
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text=_('ID in the legacy system')
    )
    legacy_sku = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Legacy SKU (maps to alteNummer in Artikel_Variante)')
    )
    
    # Parent-child relationship
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='variants',
        help_text=_('Parent product (for variants)')
    )
    is_parent = models.BooleanField(
        default=False, 
        help_text=_('Whether this is a parent product (maps to Art_Kalkulation records)')
    )
    
    # Names and descriptions
    name = models.CharField(
        max_length=255,
        help_text=_('Product name (maps to Bezeichnung in legacy system)')
    )
    name_en = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Product name in English (maps to Bezeichnung_ENG in legacy system)')
    )
    short_description = models.TextField(
        blank=True,
        help_text=_('Short product description (maps to Beschreibung_kurz in legacy system)')
    )
    short_description_en = models.TextField(
        blank=True,
        help_text=_('Short product description in English')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Full product description (maps to Beschreibung in legacy system)')
    )
    description_en = models.TextField(
        blank=True,
        help_text=_('Full product description in English')
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Search keywords')
    )
    
    # Physical attributes
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Product dimensions (LxWxH)')
    )
    weight = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Weight in grams')
    )
    
    # Pricing
    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Retail price (maps to Laden price in legacy system)')
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Wholesale price (maps to Handel price in legacy system)')
    )
    gross_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Recommended retail price (maps to Empf. price in legacy system)')
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Cost price (maps to Einkauf price in legacy system)')
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Current stock quantity')
    )
    min_stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Minimum stock quantity before reordering')
    )
    backorder_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on backorder')
    )
    open_purchase_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on open purchase orders')
    )
    last_receipt_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock receipt')
    )
    last_issue_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock issue')
    )
    
    # Sales statistics
    units_sold_current_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in current year')
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in previous year')
    )
    revenue_previous_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_('Revenue in previous year')
    )
    
    # Status flags
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the product is active')
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text=_('Whether the product is discontinued')
    )
    
    # Manufacturing flags
    has_bom = models.BooleanField(
        default=False,
        help_text=_('Whether the product has a bill of materials')
    )
    
    # Product-specific flags
    is_one_sided = models.BooleanField(
        default=False,
        help_text=_('Whether the product is one-sided')
    )
    is_hanging = models.BooleanField(
        default=False,
        help_text=_('Whether the product is hanging')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Creation timestamp')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Last update timestamp')
    )
    
    # Category
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        help_text=_('Product category')
    )
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})" 