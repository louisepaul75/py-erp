"""
Models for the production module.

This module contains the data models for production orders
and related entities.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
import logging

# Add import for ParentProduct
from pyerp.business_modules.products.models import ParentProduct

# Configure logger
logger = logging.getLogger(__name__)


class ProductionOrder(models.Model):
    """Represents a production/manufacturing order."""
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    order_number = models.CharField(
        max_length=50, 
        unique=True,
        verbose_name=_('Order Number'),
        help_text=_('Production order identifier')
    )
    form_number = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Form Number'),
        help_text=_('Reference to manufacturing form/template')
    )
    quantity = models.IntegerField(
        default=0,
        verbose_name=_('Quantity'),
        help_text=_('Total production quantity')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('Status')
    )
    creation_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('Creation Date')
    )
    planned_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('Planned Date')
    )
    priority = models.IntegerField(
        default=0,
        verbose_name=_('Priority'),
        help_text=_('Production priority (higher values indicate higher priority)')
    )
    
    # Legacy reference fields for sync
    legacy_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy ID'),
        help_text=_('UUID from legacy system')
    )
    legacy_key = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy Key'),
        help_text=_('__KEY from legacy system')
    )
    legacy_form_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy Form ID'),
        help_text=_('Form reference from legacy system')
    )
    
    # Relationships
    created_by = models.ForeignKey(
        'auth.User', 
        related_name='created_production_orders',
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name=_('Created By')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Production Order')
        verbose_name_plural = _('Production Orders')
        ordering = ['-creation_date', 'order_number']
    
    def __str__(self):
        return f"Production Order {self.order_number}"


class ProductionOrderItem(models.Model):
    """Represents an item/operation within a production order."""
    
    # Operation types used for reference only - not enforced in database
    # to allow for direct mapping of legacy codes
    OPERATION_TYPES = [
        ('E', _('Assembly')),
        ('G', _('Manufacturing')),
        ('P', _('Packaging')),
        ('Q', _('Quality Control')),
        ('T', _('Testing')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    production_order = models.ForeignKey(
        'ProductionOrder', 
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Production Order')
    )
    
    # Add parent_product foreign key relationship
    parent_product = models.ForeignKey(
        ParentProduct,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='production_items',
        verbose_name=_('Parent Product'),
        help_text=_('Reference to parent product (maps to Art_Nr in WerksauftrPos)')
    )
    
    operation_type = models.CharField(
        max_length=10, 
        verbose_name=_('Operation Type'),
        help_text=_('Production step type code from legacy system')
    )
    item_number = models.IntegerField(
        verbose_name=_('Item Number'),
        help_text=_('Sequential number within the production order')
    )
    target_quantity = models.IntegerField(
        default=0,
        verbose_name=_('Target Quantity')
    )
    completed_quantity = models.IntegerField(
        default=0,
        verbose_name=_('Completed Quantity')
    )
    remaining_quantity = models.IntegerField(
        default=0,
        verbose_name=_('Remaining Quantity')
    )
    start_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_('Start Date')
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Product reference fields
    product_sku = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name=_('Product SKU')
    )
    product_share = models.FloatField(
        default=1.0,
        verbose_name=_('Product Share'),
        help_text=_('Proportion of the product used in this operation')
    )
    
    # Time tracking
    estimated_time = models.IntegerField(
        default=0,
        verbose_name=_('Estimated Time'),
        help_text=_('Estimated time in seconds')
    )
    standard_time = models.FloatField(
        default=0,
        verbose_name=_('Standard Time'),
        help_text=_('Standard time per unit')
    )
    
    # Financial data
    value = models.FloatField(
        default=0,
        verbose_name=_('Value')
    )
    
    # Legacy reference fields for sync
    legacy_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy ID'),
        help_text=_('UUID from legacy system')
    )
    legacy_key = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy Key'),
        help_text=_('__KEY from legacy system')
    )
    legacy_kostenstelle_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy Cost Center ID')
    )
    legacy_form_artikel_id = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_('Legacy Form Article ID')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Production Order Item')
        verbose_name_plural = _('Production Order Items')
        ordering = ['production_order', 'item_number']
        unique_together = ('production_order', 'item_number')
    
    def __str__(self):
        return f"Item {self.item_number} for {self.production_order}"
    
    def save(self, *args, **kwargs):
        """Override save to update remaining quantity automatically."""
        if self.target_quantity and self.completed_quantity is not None:
            self.remaining_quantity = self.target_quantity - self.completed_quantity
        super().save(*args, **kwargs) 