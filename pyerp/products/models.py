"""
Models for the products app.

These models represent product-related entities in the ERP system,
with only essential fields required for import.
"""

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
    
    class Meta:
        verbose_name = _('Variant Product')
        verbose_name_plural = _('Variant Products')
        ordering = ['parent__name', 'variant_code'] 