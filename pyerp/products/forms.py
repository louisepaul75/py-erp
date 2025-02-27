"""Forms for the products app."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Product, ProductCategory, ProductImage


class ProductCategoryForm(forms.ModelForm):
    """Form for creating and editing product categories."""
    
    class Meta:
        model = ProductCategory
        fields = ['name', 'slug', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images."""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_primary']


class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""
    
    class Meta:
        model = Product
        fields = [
            # Basic information
            'name', 'sku', 'slug', 'category', 'manufacturer', 'manufacturer_part_number',
            
            # Descriptions
            'short_description', 'description', 'features', 'keywords',
            
            # Physical attributes
            'weight', 'length', 'width', 'height',
            
            # Pricing
            'cost', 'list_price', 'sale_price',
            
            # Inventory
            'stock_quantity', 'min_stock_level', 'max_stock_level', 'reorder_point',
            
            # Flags
            'is_active', 'is_featured', 'is_on_sale',
            
            # SEO
            'meta_keywords', 'meta_description',
        ]
        widgets = {
            'short_description': forms.Textarea(attrs={'rows': 2}),
            'description': forms.Textarea(attrs={'rows': 5}),
            'features': forms.Textarea(attrs={'rows': 5}),
            'keywords': forms.Textarea(attrs={'rows': 2}),
            'meta_keywords': forms.Textarea(attrs={'rows': 2}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }
        
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
        
        # Ensure sale price is less than list price if provided
        sale_price = cleaned_data.get('sale_price')
        list_price = cleaned_data.get('list_price')
        
        if sale_price and list_price and sale_price >= list_price:
            self.add_error('sale_price', _('Sale price must be less than list price.'))
        
        # Ensure min_stock_level is less than max_stock_level if both are provided
        min_stock = cleaned_data.get('min_stock_level')
        max_stock = cleaned_data.get('max_stock_level')
        
        if min_stock is not None and max_stock is not None and min_stock > max_stock:
            self.add_error('min_stock_level', _('Minimum stock level must be less than maximum stock level.'))
        
        return cleaned_data


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
            self.add_error('min_price', _('Minimum price must be less than maximum price.'))
        
        return cleaned_data 