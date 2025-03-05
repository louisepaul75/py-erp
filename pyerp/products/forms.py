"""Forms for the products app."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ParentProduct, VariantProduct, ProductCategory, Product, UnifiedProduct


class ProductCategoryForm(forms.ModelForm):
    """Form for creating and editing product categories."""
    
    class Meta:
        model = ProductCategory
        fields = ['code', 'name']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""
    
    class Meta:
        model = UnifiedProduct
        fields = [
            # Basic information
            'sku', 'name', 'description', 'price', 
            'is_active', 'is_parent', 'is_variant'
        ]
        
    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check
            if UnifiedProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        else:
            # If this is a new product
            if UnifiedProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        
        return sku
        
    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        is_parent = cleaned_data.get('is_parent')
        is_variant = cleaned_data.get('is_variant')
        
        # A product cannot be both a parent and a variant
        if is_parent and is_variant:
            self.add_error('is_parent', _('A product cannot be both a parent and a variant.'))
            self.add_error('is_variant', _('A product cannot be both a parent and a variant.'))
            
        return cleaned_data


class ParentProductForm(forms.ModelForm):
    """Form for creating and editing parent products."""
    
    class Meta:
        model = ParentProduct
        fields = [
            # Basic information
            'sku', 'base_sku', 'name', 'is_active',
        ]
        
    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check
            if ParentProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        else:
            # If this is a new product
            if ParentProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        
        return sku


class VariantProductForm(forms.ModelForm):
    """Form for creating and editing variant products."""
    
    class Meta:
        model = VariantProduct
        fields = [
            # Basic information
            'sku', 'name', 'parent', 'variant_code', 'is_active',
        ]
        
    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check
            if VariantProduct.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        else:
            # If this is a new product
            if VariantProduct.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        
        return sku


class ProductSearchForm(forms.Form):
    """Form for searching products."""
    
    q = forms.CharField(
        label=_('Search'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search products...'),
            'class': 'form-control'
        })
    )
    
    category = forms.ModelChoiceField(
        label=_('Category'),
        queryset=ProductCategory.objects.all(),
        required=False,
        empty_label=_('All Categories'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    min_price = forms.DecimalField(
        label=_('Min Price'),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Min'),
            'class': 'form-control'
        })
    )
    
    max_price = forms.DecimalField(
        label=_('Max Price'),
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': _('Max'),
            'class': 'form-control'
        })
    )
    
    in_stock = forms.BooleanField(
        label=_('In Stock Only'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    is_active = forms.BooleanField(
        label=_('Active Only'),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            self.add_error('min_price', _('Minimum price cannot be greater than maximum price.'))
            
        return cleaned_data 