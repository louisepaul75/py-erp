"""
Views for the products app.
"""

from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from pyerp.products.models import Product, ProductCategory
from pyerp.products.forms import ProductSearchForm


class ProductListView(LoginRequiredMixin, ListView):
    """
    View for listing products with filtering options.
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        """
        Filter products based on category and search query.
        """
        queryset = Product.objects.filter(is_active=True)
        
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
                queryset = queryset.filter(list_price__gte=min_price)
            
            max_price = form.cleaned_data.get('max_price')
            if max_price:
                queryset = queryset.filter(list_price__lte=max_price)
            
            # Filter by stock status if requested
            in_stock = form.cleaned_data.get('in_stock')
            if in_stock:
                queryset = queryset.filter(stock_quantity__gt=0)
        else:
            # If form is not valid, use basic filtering
            category_id = self.request.GET.get('category')
            if category_id:
                queryset = queryset.filter(category_id=category_id)
            
            search_query = self.request.GET.get('q')
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data.
        """
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Add search form to context
        context['search_form'] = ProductSearchForm(self.request.GET)
        
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying product details.
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        
        # Get related products from the same category
        if self.object.category:
            related_products = Product.objects.filter(
                category=self.object.category,
                is_active=True
            ).exclude(id=self.object.id)[:4]
            context['related_products'] = related_products
        
        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """
    View for listing product categories.
    """
    model = ProductCategory
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        """
        Add additional context data.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Product Categories')
        return context 