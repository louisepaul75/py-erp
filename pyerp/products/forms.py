"""Forms for the products app."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ParentProduct, VariantProduct, ProductCategory
from .models_new import Product  # Import the Product class from models_new.py


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
        model = Product
        fields = [
            # Basic information
            'sku', 'name', 'name_en', 'list_price', 'cost_price', 
            'is_active', 'stock_quantity', 'is_parent', 'variant_code'
        ]
        
    def clean_sku(self):
        """Validate that the SKU is unique."""
        sku = self.cleaned_data.get('sku')
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            # If this is an existing product, exclude it from the uniqueness check
            if Product.objects.filter(sku=sku).exclude(pk=instance.pk).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        else:
            # If this is a new product
            if Product.objects.filter(sku=sku).exists():
                raise forms.ValidationError(_('A product with this SKU already exists.'))
        
        return sku
        
    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        is_parent = cleaned_data.get('is_parent')
        variant_code = cleaned_data.get('variant_code')
        list_price = cleaned_data.get('list_price')
        cost_price = cleaned_data.get('cost_price')
        
        # Parent products should not have variant codes
        if is_parent and variant_code:
            self.add_error('variant_code', _('Parent products should not have variant codes.'))
            
        # List price should be greater than cost price
        if list_price and cost_price and list_price < cost_price:
            self.add_error('list_price', _('List price must be greater than or equal to cost price.'))
            
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
    
    def clean(self):
        """Validate the form data."""
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            self.add_error('min_price', _('Minimum price cannot be greater than maximum price.'))
            
        return cleaned_data 