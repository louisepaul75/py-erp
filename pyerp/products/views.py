"""
Views for the products app.
"""

from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory
from pyerp.products.forms import ProductSearchForm


class ProductListView(LoginRequiredMixin, ListView):
    """
    View for listing products with filtering options.
    """
    model = ParentProduct
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """
        Filter products based on category and search query.
        """
        queryset = ParentProduct.objects.filter(is_active=True)
        
        # Get form data
        form = ProductSearchForm(self.request.GET)
        if form.is_valid():
            # Filter by category if provided
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Filter by search query if provided
            search_query = form.cleaned_data.get('q')
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)
            
            # Filter by price range if provided
            min_price = form.cleaned_data.get('min_price')
            if min_price:
                queryset = queryset.filter(price__gte=min_price)
                
            max_price = form.cleaned_data.get('max_price')
            if max_price:
                queryset = queryset.filter(price__lte=max_price)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add search form and categories to context.
        """
        context = super().get_context_data(**kwargs)
        context['form'] = ProductSearchForm(self.request.GET)
        context['categories'] = ProductCategory.objects.all()
        
        # Prepare primary images for products to avoid template filtering
        primary_images = {}
        for product in context['products']:
            if hasattr(product, 'images') and product.images.exists():
                try:
                    primary_image = product.images.filter(is_primary=True).first()
                    if primary_image:
                        primary_images[product.id] = primary_image
                except Exception as e:
                    # Just log or handle the error and continue
                    pass
        
        context['primary_images'] = primary_images
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying product details.
    """
    model = ParentProduct
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_object(self, queryset=None):
        """
        Get product by ID or slug.
        """
        if self.kwargs.get('pk'):
            return get_object_or_404(ParentProduct, pk=self.kwargs['pk'])
        elif self.kwargs.get('slug'):
            return get_object_or_404(ParentProduct, slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        """
        Add variants to context.
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['variants'] = VariantProduct.objects.filter(parent=product)
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """
    View for listing product categories.
    """
    model = ProductCategory
    template_name = 'products/category_list.html'
    context_object_name = 'categories'


@login_required
@require_POST
def save_product_images(request, pk):
    """
    Save product images from external API.
    """
    product = get_object_or_404(ParentProduct, pk=pk)
    
    # This functionality is no longer supported with the simplified model
    return JsonResponse({
        'status': 'error',
        'message': 'Image functionality has been removed in the simplified model'
    })


# API Views
# ---------

class ProductAPIView(LoginRequiredMixin, View):
    """Base class for API views"""
    
    def get_product_data(self, product):
        """Convert a product model to a dictionary for JSON response"""
        product_data = {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'description': getattr(product, 'description', ''),
            'list_price': float(product.list_price) if product.list_price else None,
            'stock_quantity': product.stock_quantity,
        }
        
        # Add primary image if available
        if hasattr(product, 'images') and product.images.exists():
            try:
                primary_image = product.images.filter(is_primary=True).first()
                if primary_image:
                    product_data['image_url'] = primary_image.image_url
                else:
                    first_image = product.images.first()
                    if first_image:
                        product_data['image_url'] = first_image.image_url
            except:
                pass
                
        return product_data


class ProductListAPIView(ProductAPIView):
    """API view for listing products"""
    
    def get(self, request):
        """Handle GET request for product listing"""
        # Start with all active products
        products = ParentProduct.objects.filter(is_active=True)
        
        # Apply filters from query parameters
        category_id = request.GET.get('category')
        if category_id:
            products = products.filter(category_id=category_id)
            
        search_query = request.GET.get('q')
        if search_query:
            products = products.filter(name__icontains=search_query)
            
        # Convert products to JSON-serializable format
        products_data = [self.get_product_data(product) for product in products]
        
        # Return JSON response
        return JsonResponse({
            'count': len(products_data),
            'results': products_data
        })


class ProductDetailAPIView(ProductAPIView):
    """API view for product details"""
    
    def get(self, request, pk=None, slug=None):
        """Handle GET request for product detail"""
        # Get the product
        if pk:
            product = get_object_or_404(ParentProduct, pk=pk)
        elif slug:
            product = get_object_or_404(ParentProduct, slug=slug)
        else:
            return JsonResponse({'error': 'Product not found'}, status=404)
            
        # Get basic product data
        product_data = self.get_product_data(product)
        
        # Add variants
        variants = VariantProduct.objects.filter(parent=product)
        variants_data = []
        for variant in variants:
            variant_data = self.get_product_data(variant)
            variants_data.append(variant_data)
        product_data['variants'] = variants_data
        
        # Add all images
        if hasattr(product, 'images') and product.images.exists():
            product_data['images'] = []
            for image in product.images.all():
                product_data['images'].append({
                    'id': image.id,
                    'url': image.image_url,
                    'is_primary': image.is_primary,
                })
        
        # Return JSON response
        return JsonResponse(product_data)


class CategoryListAPIView(LoginRequiredMixin, View):
    """API view for listing categories"""
    
    def get(self, request):
        """Handle GET request for category listing"""
        categories = ProductCategory.objects.all()
        
        # Convert categories to JSON-serializable format
        categories_data = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'code': category.code,
            }
            categories_data.append(category_data)
        
        # Return JSON response
        return JsonResponse({
            'count': len(categories_data),
            'results': categories_data
        }) 