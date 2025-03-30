"""Forms for the products app."""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
    UnifiedProduct,
    VariantProduct,
)
from pyerp.business_modules.products.tag_models import M2MOverride
from pyerp.core.models import Tag


class ProductCategoryForm(forms.ModelForm):
    """Form for creating and editing product categories."""

    class Meta:
        model = ProductCategory
        fields = ["code", "name"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""

    class Meta:
        model = UnifiedProduct
        fields = [
            "sku",
            "name",
            "description",
            "price",
            "is_active",
            "is_parent",
            "is_variant",
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get("sku")
        instance = getattr(self, "instance", None)

        if instance and instance.pk:
            if UnifiedProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(
                    _("A product with this SKU already exists."),
                )
        elif UnifiedProduct.objects.filter(sku=sku).exists():
            raise forms.ValidationError(_("A product with this SKU already exists."))

        return sku

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        is_parent = cleaned_data.get("is_parent")
        is_variant = cleaned_data.get("is_variant")

        # A product cannot be both a parent and a variant
        if is_parent and is_variant:
            self.add_error(
                "is_parent",
                _("A product cannot be both a parent and a variant."),
            )
            self.add_error(
                "is_variant",
                _("A product cannot be both a parent and a variant."),
            )

        return cleaned_data


class ParentProductForm(forms.ModelForm):
    """Form for creating and editing parent products."""

    class Meta:
        model = ParentProduct
        fields = [
            "sku",
            "legacy_base_sku",
            "name",
            "is_active",
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get("sku")
        instance = getattr(self, "instance", None)

        if instance and instance.pk:
            if ParentProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(
                    _("A product with this SKU already exists."),
                )
        elif ParentProduct.objects.filter(sku=sku).exists():
            raise forms.ValidationError(_("A product with this SKU already exists."))

        return sku


class VariantProductForm(forms.ModelForm):
    """Form for creating and editing variant products."""

    class Meta:
        model = VariantProduct
        fields = [
            "sku",
            "name",
            "parent",
            "variant_code",
            "is_active",
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get("sku")
        instance = getattr(self, "instance", None)

        if instance and instance.pk:
            if VariantProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(
                    _("A product with this SKU already exists."),
                )
        elif VariantProduct.objects.filter(sku=sku).exists():
            raise forms.ValidationError(_("A product with this SKU already exists."))

        return sku


class ProductSearchForm(forms.Form):
    """Form for searching products."""

    q = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search products..."),
                "class": "form-control",
            },
        ),
    )

    category = forms.ModelChoiceField(
        label=_("Category"),
        queryset=ProductCategory.objects.all(),
        required=False,
        empty_label=_("All Categories"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    min_price = forms.DecimalField(
        label=_("Min Price"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _("Min"),
                "class": "form-control",
            },
        ),
    )

    max_price = forms.DecimalField(
        label=_("Max Price"),
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": _("Max"),
                "class": "form-control",
            },
        ),
    )

    in_stock = forms.BooleanField(
        label=_("In Stock Only"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_active = forms.BooleanField(
        label=_("Active Only"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        min_price = cleaned_data.get("min_price")
        max_price = cleaned_data.get("max_price")

        if min_price and max_price and min_price > max_price:
            self.add_error(
                "min_price",
                _("Minimum price cannot be greater than maximum price."),
            )

        return cleaned_data


class TagInheritanceForm(forms.ModelForm):
    """
    Form for managing variant product tags and inheritance settings.
    NOTE: The inheritance logic needs review after switching to GenericRelation for tags.
    """
    inherit_tags = forms.BooleanField(
        label=_("Inherit tags from parent"),
        required=False,
        help_text=_("When enabled, this variant will display tags from its parent product in addition to its own tags.")
    )
    
    class Meta:
        model = VariantProduct
        fields = ['inherit_tags']
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        
        # If we have an instance, populate the inherit_tags field
        if instance and instance.id:
            content_type = ContentType.objects.get_for_model(VariantProduct)
            try:
                override = M2MOverride.objects.get(
                    content_type=content_type,
                    object_id=instance.id,
                    relationship_name='tags'
                )
                initial['inherit_tags'] = override.inherit
            except M2MOverride.DoesNotExist:
                initial['inherit_tags'] = True  # Default to inherit if not set
        
        kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
        
        # If no parent, disable inheritance option
        if instance and not instance.parent:
            self.fields['inherit_tags'].disabled = True
            self.fields['inherit_tags'].help_text = _("Tag inheritance requires a parent product.")
    
    def save(self, commit=True):
        instance = self.instance
        
        if commit:
            content_type = ContentType.objects.get_for_model(VariantProduct)
            override, created = M2MOverride.objects.update_or_create(
                content_type=content_type,
                object_id=instance.id,
                relationship_name='tags',
                defaults={'inherit': self.cleaned_data['inherit_tags']}
            )
        
        return instance
