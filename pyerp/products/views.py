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

from pyerp.products.models import Product, ProductCategory, ProductImage
from pyerp.products.forms import ProductSearchForm
from pyerp.products.image_api import ImageAPIClient


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
        
        # Preload images for products in the list
        try:
            # Initialize the API client
            api_client = ImageAPIClient()
            
            # Create a mapping of products to their appropriate article numbers
            product_article_mapping = {}
            product_images = {}
            
            # For each product, determine the appropriate article number
            for product in context['products']:
                article_number = api_client.get_appropriate_article_number(product)
                product_article_mapping[product.id] = article_number
            
            # Get unique article numbers to search for
            article_numbers = list(set(product_article_mapping.values()))
            
            # Preload images for these article numbers
            article_images = api_client.preload_product_images(article_numbers)
            
            # Map the images back to products
            for product in context['products']:
                article_number = product_article_mapping[product.id]
                if article_number in article_images:
                    product_images[product.sku] = article_images[article_number]
            
            # Add the images to the context
            context['product_images'] = product_images
            
        except Exception as e:
            # Log the error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error preloading product images: {str(e)}")
            context['product_images'] = {}
        
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
        
        # Check if product has images, if not try to fetch from API
        if not self.object.images.exists():
            try:
                # Initialize the API client
                api_client = ImageAPIClient()
                
                # Get images for the product using the improved method with fallback logic
                product_images = api_client.get_product_images(self.object)
                
                if product_images:
                    # Process and save images
                    api_images = []
                    for image_data in product_images:
                        parsed_image = api_client.parse_image(image_data)
                        api_images.append(parsed_image)
                    
                    # Sort images by priority
                    api_images = sorted(api_images, key=lambda x: api_client.get_image_priority(x))
                    
                    # Create temporary image objects for display (not saved to database)
                    temp_images = []
                    for i, img in enumerate(api_images):
                        temp_image = ProductImage(
                            product=self.object,
                            external_id=img.get('external_id', ''),
                            image_url=img.get('image_url', ''),
                            thumbnail_url=img.get('images', [])[0].get('url') if img.get('images') else '',
                            image_type=img.get('image_type', ''),
                            is_primary=(i == 0),  # First image is primary
                            priority=i
                        )
                        temp_images.append(temp_image)
                    
                    context['temp_images'] = temp_images
            except Exception as e:
                # Log the error but don't break the page
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error fetching images for product {self.object.sku}: {str(e)}")
        
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


@login_required
@require_POST
def save_product_images(request, pk):
    """
    Save images from the external API to the database for a specific product.
    
    Args:
        request: The HTTP request
        pk: The primary key of the product
        
    Returns:
        JsonResponse with the result of the operation
    """
    product = get_object_or_404(Product, pk=pk)
    
    # Check if product already has images
    if product.images.exists():
        return JsonResponse({
            'success': False,
            'message': _('Product already has images in the database.')
        })
    
    try:
        # Initialize the API client
        api_client = ImageAPIClient()
        
        # Get images for the product using the improved method with fallback logic
        product_images = api_client.get_product_images(product)
        
        if not product_images:
            return JsonResponse({
                'success': False,
                'message': _('No images found for this product.')
            })
        
        # Process and save images
        api_images = []
        for image_data in product_images:
            parsed_image = api_client.parse_image(image_data)
            api_images.append(parsed_image)
        
        # Sort images by priority
        api_images = sorted(api_images, key=lambda x: api_client.get_image_priority(x))
        
        # Save images to database
        saved_images = []
        for i, img in enumerate(api_images):
            # Create image record
            product_image = ProductImage(
                product=product,
                external_id=img.get('external_id', ''),
                image_url=img.get('image_url', ''),
                thumbnail_url=img.get('images', [])[0].get('url') if img.get('images') else '',
                image_type=img.get('image_type', ''),
                is_primary=(i == 0),  # First image is primary
                priority=i,
                alt_text=product.name,
                metadata=img.get('metadata', {})
            )
            product_image.save()
            saved_images.append(product_image)
        
        return JsonResponse({
            'success': True,
            'message': _('Successfully saved {} images.').format(len(saved_images)),
            'image_count': len(saved_images)
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error saving images for product {product.sku}: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'message': _('Error saving images: {}').format(str(e))
        }, status=500) 