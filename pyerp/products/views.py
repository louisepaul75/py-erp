"""
Views for the products app.
"""

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View

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