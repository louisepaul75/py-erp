"""
Models for the product tagging and inheritance system.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Tag(models.Model):
    """
    Tag model for product categorization.
    """
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text=_("Tag name")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("URL-friendly tag name"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Tag description"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Creation timestamp"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp"),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class InheritableField:
    """
    Registry class for tracking fields that can be inherited from parent to variant products.
    """
    registry = {}

    @classmethod
    def register(cls, model, field_name, related_name=None):
        """
        Register a field as inheritable.
        
        Args:
            model: The model class
            field_name: The name of the field
            related_name: For M2M relationships, the related name to access related objects
        """
        if model not in cls.registry:
            cls.registry[model] = {}
        
        cls.registry[model][field_name] = {
            'related_name': related_name
        }
    
    @classmethod
    def get_inheritable_fields(cls, model):
        """Get all inheritable fields for a model."""
        return cls.registry.get(model, {})
    
    @classmethod
    def is_inheritable(cls, model, field_name):
        """Check if a field is inheritable."""
        return field_name in cls.registry.get(model, {})


class FieldOverride(models.Model):
    """
    Model to track inheritance status for scalar fields.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=_("Content type of the model containing the field"),
    )
    object_id = models.PositiveIntegerField(
        help_text=_("Primary key of the object"),
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    field_name = models.CharField(
        max_length=100,
        help_text=_("Name of the field being overridden"),
    )
    inherit = models.BooleanField(
        default=True,
        help_text=_("Whether to inherit the field value from parent"),
    )
    
    class Meta:
        verbose_name = _("Field Override")
        verbose_name_plural = _("Field Overrides")
        unique_together = ('content_type', 'object_id', 'field_name')
    
    def __str__(self) -> str:
        return f"Override for {self.content_object} - {self.field_name}"


class M2MOverride(models.Model):
    """
    Model to track inheritance status for Many-to-Many relationships.
    """
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        help_text=_("Content type of the model containing the M2M relationship"),
    )
    object_id = models.PositiveIntegerField(
        help_text=_("Primary key of the object"),
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    relationship_name = models.CharField(
        max_length=100,
        help_text=_("Name of the M2M relationship being overridden"),
    )
    inherit = models.BooleanField(
        default=True,
        help_text=_("Whether to inherit relationships from parent"),
    )
    
    class Meta:
        verbose_name = _("M2M Override")
        verbose_name_plural = _("M2M Overrides")
        unique_together = ('content_type', 'object_id', 'relationship_name')
    
    def __str__(self) -> str:
        return f"M2M Override for {self.content_object} - {self.relationship_name}" 