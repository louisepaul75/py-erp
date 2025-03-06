"""Forms for the products app."""
from django import forms
from django.utils.translation import gettext_lazy as _  # noqa: F401

from .models import ParentProduct, VariantProduct, ProductCategory, Product, UnifiedProduct  # noqa: E501


class ProductCategoryForm(forms.ModelForm):
    """Form for creating and editing product categories."""

    class Meta:
        model = ProductCategory  # noqa: F841
        fields = ['code', 'name']  # noqa: F841
        widgets = {  # noqa: F841
  # noqa: F841
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""

    class Meta:

        model = UnifiedProduct  # noqa: F841
        fields = [  # noqa: F841
            # Basic information  # noqa: E128
            'sku', 'name', 'description', 'price',
            'is_active', 'is_parent', 'is_variant'
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check  # noqa: E501
            if UnifiedProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():  # noqa: E501
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501
        else:
            # If this is a new product
            if UnifiedProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501

        return sku

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        is_parent = cleaned_data.get('is_parent')
        is_variant = cleaned_data.get('is_variant')

        # A product cannot be both a parent and a variant
        if is_parent and is_variant:
            self.add_error('is_parent', _('A product cannot be both a parent and a variant.'))  # noqa: E501
            self.add_error('is_variant', _('A product cannot be both a parent and a variant.'))  # noqa: E501

        return cleaned_data


class ParentProductForm(forms.ModelForm):
    """Form for creating and editing parent products."""

    class Meta:

        model = ParentProduct  # noqa: F841
        fields = [  # noqa: F841
            # Basic information  # noqa: E128
            'sku', 'base_sku', 'name', 'is_active',
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check  # noqa: E501
            if ParentProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():  # noqa: E501
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501
        else:
            # If this is a new product
            if ParentProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501

        return sku


class VariantProductForm(forms.ModelForm):
    """Form for creating and editing variant products."""

    class Meta:

        model = VariantProduct  # noqa: F841
  # noqa: F841
        fields = [  # noqa: F841
  # noqa: F841
            # Basic information
            'sku', 'name', 'parent', 'variant_code', 'is_active',
        ]

    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)

        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check  # noqa: E501
            if VariantProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():  # noqa: E501
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501
        else:
            # If this is a new product
            if VariantProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))  # noqa: E501

        return sku


class ProductSearchForm(forms.Form):
    """Form for searching products."""

    q = forms.CharField(  # noqa: F841
        label=_('Search'),  # noqa: E128
        required=False,  # noqa: F841
        widget=forms.TextInput(attrs={  # noqa: F841
            'placeholder': _('Search products...'),  # noqa: E128
            'class': 'form-control'
        })
    )

    category = forms.ModelChoiceField(  # noqa: F841
  # noqa: F841
        label=_('Category'),  # noqa: F841
        queryset=ProductCategory.objects.all(),  # noqa: F841
  # noqa: F841
        required=False,  # noqa: F841
        empty_label=_('All Categories'),  # noqa: F841
  # noqa: F841
        widget=forms.Select(attrs={'class': 'form-control'})  # noqa: F841
    )

    min_price = forms.DecimalField(
        label=_('Min Price'),  # noqa: E128
        required=False,  # noqa: F841
        min_value=0,  # noqa: F841
        widget=forms.NumberInput(attrs={  # noqa: F841
            'placeholder': _('Min'),  # noqa: E128
            'class': 'form-control'
        })
    )

    max_price = forms.DecimalField(
        label=_('Max Price'),  # noqa: E128
        required=False,  # noqa: F841
        min_value=0,  # noqa: F841
  # noqa: F841
        widget=forms.NumberInput(attrs={  # noqa: F841
            'placeholder': _('Max'),  # noqa: E128
            'class': 'form-control'
        })
    )

    in_stock = forms.BooleanField(  # noqa: F841
  # noqa: F841
        label=_('In Stock Only'),  # noqa: F841
        required=False,  # noqa: F841
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})  # noqa: F841
    )

    is_active = forms.BooleanField(  # noqa: F841
  # noqa: F841
        label=_('Active Only'),  # noqa: F841
  # noqa: F841
        required=False,  # noqa: F841
  # noqa: F841
        initial=True,  # noqa: F841
  # noqa: F841
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})  # noqa: F841
  # noqa: F841
    )

    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price and max_price and min_price > max_price:
            self.add_error('min_price', _('Minimum price cannot be greater than maximum price.'))  # noqa: E501

        return cleaned_data
