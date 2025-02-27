"""
Models for the products app.

These models represent product-related entities in the ERP system.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ProductCategory(models.Model):
    """
    Product categories for organizing products.
    
    Maps to ArtGruppe in the legacy system.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Category code (maps to ArtGruppe in legacy system)')
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
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    """
    Product model representing items sold or manufactured.
    
    Maps to Artikel_Stamm in the legacy system.
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
        help_text=_('Short product description in English (maps to Beschreibung_kurz_ENG in legacy system)')
    )
    description = models.TextField(
        blank=True,
        help_text=_('Detailed product description (maps to Beschreibung in legacy system)')
    )
    description_en = models.TextField(
        blank=True,
        help_text=_('Detailed product description in English (maps to Beschreibung_ENG in legacy system)')
    )
    keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Keywords for search (maps to Keywords in legacy system)')
    )
    
    # Categorization
    category = models.ForeignKey(
        ProductCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
        help_text=_('Product category (maps to ArtGruppe in legacy system)')
    )
    
    # Physical attributes
    dimensions = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Product dimensions (maps to Masse in legacy system)')
    )
    weight = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Product weight in grams (maps to Gewicht in legacy system)')
    )
    
    # Pricing
    list_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('List price (maps to PreisL in legacy system)')
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Wholesale price (maps to PreisH in legacy system)')
    )
    gross_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Gross price including tax (maps to PreisL_Brutto in legacy system)')
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_('Cost price (maps to PreisEinkauf in legacy system)')
    )
    
    # Inventory
    stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Current stock quantity (maps to Bestand in legacy system)')
    )
    min_stock_quantity = models.IntegerField(
        default=0,
        help_text=_('Minimum stock quantity (maps to MindBestand in legacy system)')
    )
    backorder_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on backorder (maps to Auftragsbestand in legacy system)')
    )
    open_purchase_quantity = models.IntegerField(
        default=0,
        help_text=_('Quantity on open purchase orders (maps to bestelltOffen in legacy system)')
    )
    last_receipt_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock receipt (maps to letzterZugang in legacy system)')
    )
    last_issue_date = models.DateField(
        null=True,
        blank=True,
        help_text=_('Date of last stock issue (maps to letzterAbgang in legacy system)')
    )
    
    # Sales statistics
    units_sold_current_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in current year (maps to ZugangJahr in legacy system)')
    )
    units_sold_previous_year = models.IntegerField(
        default=0,
        help_text=_('Units sold in previous year (maps to StVorJahr in legacy system)')
    )
    revenue_previous_year = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_('Revenue in previous year (maps to EUR_VJahr in legacy system)')
    )
    
    # Flags
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether the product is active')
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text=_('Whether the product is discontinued (maps to Auslauf in legacy system)')
    )
    has_bom = models.BooleanField(
        default=False,
        help_text=_('Whether the product has a bill of materials (maps to Stückliste in legacy system)')
    )
    is_one_sided = models.BooleanField(
        default=False,
        help_text=_('Whether the product is one-sided (maps to eineSeite in legacy system)')
    )
    is_hanging = models.BooleanField(
        default=False,
        help_text=_('Whether the product is hanging (maps to haengen in legacy system)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When the product was created in the system')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When the product was last updated')
    )
    
    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['sku']
        indexes = [
            models.Index(fields=['base_sku']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    @property
    def available_quantity(self):
        """
        Calculate available quantity (stock minus backorders).
        """
        return max(0, self.stock_quantity - self.backorder_quantity)
    
    @property
    def needs_reordering(self):
        """
        Check if product needs reordering.
        """
        return (self.stock_quantity + self.open_purchase_quantity) < self.min_stock_quantity


class ProductImage(models.Model):
    """
    Images associated with products.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        help_text=_('Product this image belongs to')
    )
    image = models.ImageField(
        upload_to='products/',
        help_text=_('Product image file')
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Alternative text for the image')
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_('Whether this is the primary image for the product')
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text=_('Order in which to display the image')
    )
    
    class Meta:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['sort_order']
    
    def __str__(self):
        return f"Image for {self.product.sku}" 