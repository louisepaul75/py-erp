# Test comment to trigger reload with FINAL FIX
"""
Views for the products app.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import (
    DetailView, ListView, CreateView, UpdateView, DeleteView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework import status
import logging

from pyerp.business_modules.products.forms import (
    ProductSearchForm, TagInheritanceForm
)
from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)
from pyerp.core.models import Tag
from pyerp.business_modules.products.serializers import (
    ParentProductSerializer,
    ParentProductSummarySerializer,
    ProductSearchResultSerializer
)

# Get standard logger instance
logger = logging.getLogger(__name__)


class ProductListView(LoginRequiredMixin, ListView):
    """
    View for listing products with filtering options.
    """

    model = ParentProduct
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        """
        Filter products based on category and search query.
        """
        queryset = ParentProduct.objects.all()

        # Get form data
        form = ProductSearchForm(self.request.GET)
        if form.is_valid():
            search_query = form.cleaned_data.get("q")
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)

            # Filter by is_active if provided
            is_active = form.cleaned_data.get("is_active")
            if is_active is not None:  # Check if the field was included in the form
                queryset = queryset.filter(is_active=is_active)

            # Note: ParentProduct doesn't have category or price fields
            # These filters are commented out until the model is updated or the filtering logic is adjusted

            # Filter by category if provided
            # category = form.cleaned_data.get('category')
            # if category:
            #     queryset = queryset.filter(category=category)

            # Filter by price range if provided
            # min_price = form.cleaned_data.get('min_price')
            # if min_price:
            #     queryset = queryset.filter(price__gte=min_price)

            # max_price = form.cleaned_data.get('max_price')
            # if max_price:
            #     queryset = queryset.filter(price__lte=max_price)

            # Handle in_stock filter - this needs to be implemented differently
            # since ParentProduct doesn't have a direct stock field
            in_stock = form.cleaned_data.get("in_stock")
            if in_stock:
                pass  # Remove this line when implementing the actual filter

        return queryset

    def get_context_data(self, **kwargs):
        """
        Add search form and categories to context.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = ProductSearchForm(self.request.GET)
        context["categories"] = ProductCategory.objects.all()

        # Prepare primary images for products to avoid template filtering
        primary_images = {}
        for product in context["products"]:
            if hasattr(product, "images") and product.images.exists():
                try:
                    # 4. Any image marked as primary

                    # First priority: Produktfoto with front=True
                    primary_image = product.images.filter(
                        image_type__iexact="Produktfoto",
                        is_front=True,
                    ).first()

                    if not primary_image:
                        primary_image = product.images.filter(
                            image_type__iexact="Produktfoto",
                        ).first()

                    if not primary_image:
                        primary_image = product.images.filter(is_front=True).first()

                    if not primary_image:
                        primary_image = product.images.filter(is_primary=True).first()

                    if not primary_image:
                        primary_image = product.images.first()

                    if primary_image:
                        primary_images[product.id] = primary_image
                except Exception:
                    pass

        context["primary_images"] = primary_images
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying product details.
    """

    model = ParentProduct
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        """
        Get product by ID.
        """
        if self.kwargs.get("pk"):
            return get_object_or_404(ParentProduct, pk=self.kwargs["pk"])
        return None

    def get_context_data(self, **kwargs):
        """
        Add variants to context.
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Get variants and ensure they're ordered appropriately
        variants = VariantProduct.objects.filter(parent=product).order_by(
            "variant_code",
            "name",
        )
        context["variants"] = variants

        # Add flag to check if there's any Produktfoto with front=True
        has_front_produktfoto = False
        if hasattr(product, "images") and product.images.exists():
            for image in product.images.all():
                if image.image_type == "Produktfoto" and image.is_front:
                    has_front_produktfoto = True
                    break
        context["has_front_produktfoto"] = has_front_produktfoto

        # Get primary images for variants to avoid template filtering
        variant_images = {}
        for variant in variants:
            if hasattr(variant, "images") and variant.images.exists():
                try:
                    # 4. Any image marked as primary

                    # First priority: Produktfoto with front=True
                    primary_image = None
                    for image in variant.images.all():
                        if image.image_type == "Produktfoto" and image.is_front:
                            primary_image = image
                            break

                    if not primary_image:
                        for image in variant.images.all():
                            if image.image_type == "Produktfoto":
                                primary_image = image
                                break

                    if not primary_image:
                        for image in variant.images.all():
                            if image.is_front:
                                primary_image = image
                                break

                    if not primary_image:
                        for image in variant.images.all():
                            if image.is_primary:
                                primary_image = image
                                break

                    if not primary_image:
                        if variant.images.all():
                            primary_image = variant.images.all()[0]

                    if primary_image:
                        variant_images[variant.id] = primary_image
                except Exception:
                    pass

        context["variant_images"] = variant_images
        return context


class VariantDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying variant details.
    """

    model = VariantProduct
    template_name = "products/variant_detail.html"
    context_object_name = "variant"

    def get_context_data(self, **kwargs):
        """
        Add additional context.
        """
        context = super().get_context_data(**kwargs)
        variant = self.get_object()

        # Add parent product for navigation
        context["parent_product"] = variant.parent

        # Add flag to check if there's any Produktfoto with front=True
        has_front_produktfoto = False
        if hasattr(variant, "images") and variant.images.exists():
            for image in variant.images.all():
                if image.image_type == "Produktfoto" and image.is_front:
                    has_front_produktfoto = True
                    break
        context["has_front_produktfoto"] = has_front_produktfoto

        # Get primary image for variant
        if hasattr(variant, "images") and variant.images.exists():
            try:
                # 4. Any image marked as primary

                # First priority: Produktfoto with front=True
                primary_image = None
                for image in variant.images.all():
                    if image.image_type == "Produktfoto" and image.is_front:
                        primary_image = image
                        break

                if not primary_image:
                    for image in variant.images.all():
                        if image.image_type == "Produktfoto":
                            primary_image = image
                            break

                if not primary_image:
                    for image in variant.images.all():
                        if image.is_front:
                            primary_image = image
                            break

                if not primary_image:
                    for image in variant.images.all():
                        if image.is_primary:
                            primary_image = image
                            break

                if not primary_image:
                    if variant.images.all():
                        primary_image = variant.images.all()[0]

                if primary_image:
                    context["primary_image"] = primary_image
            except Exception:
                pass

        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """
    View for listing product categories.
    """

    model = ProductCategory
    template_name = "products/category_list.html"
    context_object_name = "categories"


@login_required
@require_POST
def save_product_images(_, _pk):
    """
    Save product images from external API.
    """
    # This functionality is no longer supported with the simplified model
    return JsonResponse(
        {
            "status": "error",
            "message": ("Image functionality has been removed "
                        "in the simplified model"),
        },
    )


# API Views
# ---------

class ProductAPIView(APIView):
    """Base class for API views in the products module."""
    permission_classes = [IsAuthenticated]
    # We can add back the get_product_data method later if needed

class ProductListAPIView(APIView):
    """API view for listing products - TEMPORARY DEBUGGING VERSION"""

    def get(self, request, *args, **kwargs):
        """Minimal GET method for debugging"""
        message = "--- ProductListAPIView GET method executed ---"
        print(message)
        # In a real scenario, you might want basic authentication check
        # if not request.user.is_authenticated:
        #     return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message": message, "count": -1, "results": []})


class ProductDetailAPIView(APIView):
    """
    Get product by ID.
    """

    def get_object(self, pk):
        """Get product by ID."""
        return get_object_or_404(ParentProduct, pk=pk)

    def get(self, request, pk=None):
        """Get product details."""
        product = self.get_object(pk)
        serializer = ParentProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        """Update product details."""
        product = self.get_object(pk)
        serializer = ParentProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VariantDetailAPIView(ProductAPIView):
    """API view for variant details"""

    def get(self, request, pk):
        """Handle GET request for variant detail"""
        variant = get_object_or_404(VariantProduct, pk=pk)

        # Get basic variant data - now includes all variant fields thanks to updated get_product_data
        variant_data = self.get_product_data(variant)

        # Add parent product info with more details
        if variant.parent:
            variant_data["parent"] = {
                "id": variant.parent.id,
                "name": variant.parent.name,
                "sku": variant.parent.sku,
            }

        # Add all images
        if hasattr(variant, "images") and variant.images.exists():
            variant_data["images"] = []
            for image in variant.images.all():
                variant_data["images"].append(
                    {
                        "id": image.id,
                        "url": image.image_url,
                        "thumbnail_url": (
                            image.thumbnail_url
                            if hasattr(image, "thumbnail_url")
                            else image.image_url
                        ),
                        "is_primary": image.is_primary,
                        "is_front": getattr(image, "is_front", False),
                        "image_type": getattr(image, "image_type", None),
                    },
                )

        # Add attributes
        if hasattr(variant, "attributes") and variant.attributes.exists():
            variant_data["attributes"] = []
            for attr in variant.attributes.all():
                variant_data["attributes"].append(
                    {
                        "name": attr.name,
                        "value": attr.value,
                    },
                )

        # Add information about tags inheritance if applicable
        if hasattr(variant, "inherits_tags"):
            variant_data["inherits_tags"] = variant.inherits_tags()

        # Return JSON response
        return Response(variant_data)

    def patch(self, request, pk):
        """Handle PATCH request for variant update"""
        variant = get_object_or_404(VariantProduct, pk=pk)
        
        # Update basic fields
        if "name" in request.data:
            variant.name = request.data["name"]
        if "description" in request.data:
            variant.description = request.data["description"]
        if "is_active" in request.data:
            variant.is_active = request.data["is_active"]
            
        # Update variant-specific fields
        if "variant_code" in request.data:
            variant.variant_code = request.data["variant_code"]
        if "is_featured" in request.data:
            variant.is_featured = request.data["is_featured"]
        if "is_bestseller" in request.data:
            variant.is_bestseller = request.data["is_bestseller"]
        if "is_new" in request.data:
            variant.is_new = request.data["is_new"]
        if "is_verkaufsartikel" in request.data:
            variant.is_verkaufsartikel = request.data["is_verkaufsartikel"]
        if "retail_price" in request.data:
            variant.retail_price = request.data["retail_price"]
        if "wholesale_price" in request.data:
            variant.wholesale_price = request.data["wholesale_price"]
        if "retail_unit" in request.data:
            variant.retail_unit = request.data["retail_unit"]
        if "wholesale_unit" in request.data:
            variant.wholesale_unit = request.data["wholesale_unit"]
        if "color" in request.data:
            variant.color = request.data["color"]
        if "width_mm" in request.data:
            variant.width_mm = request.data["width_mm"]
            
        # Handle tags inheritance if applicable
        if "inherits_tags" in request.data and hasattr(variant, "set_tags_inheritance"):
            variant.set_tags_inheritance(request.data["inherits_tags"])
            
        # Save changes
        variant.save()
        
        # Return updated variant data
        return Response(self.get_product_data(variant))


class CategoryListAPIView(ProductAPIView):
    """API view for listing categories"""

    def get(self, request):
        """Handle GET request for category listing"""
        categories = ProductCategory.objects.all()

        # Convert categories to JSON-serializable format
        categories_data = []
        for category in categories:
            category_data = {
                "id": category.id,
                "name": category.name,
                "code": category.code,
            }
            categories_data.append(category_data)

        # Return JSON response
        return Response(
            {
                "count": len(categories_data),
                "results": categories_data,
            },
        )


class TagListView(LoginRequiredMixin, ListView):
    """
    View for listing all tags
    """
    model = Tag
    template_name = 'products/tag_list.html'
    context_object_name = 'tags'


class TagCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new tag
    """
    model = Tag
    template_name = 'products/tag_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('products:tag_list')

    def form_valid(self, form):
        messages.success(self.request, _("Tag created successfully."))
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing tag
    """
    model = Tag
    template_name = 'products/tag_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('products:tag_list')

    def form_valid(self, form):
        messages.success(self.request, _("Tag updated successfully."))
        return super().form_valid(form)


class TagDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a tag
    """
    model = Tag
    template_name = 'products/tag_confirm_delete.html'
    success_url = reverse_lazy('products:tag_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Tag deleted successfully."))
        return super().delete(request, *args, **kwargs)


class VariantProductTagUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for managing tags on a variant product
    """
    model = VariantProduct
    form_class = TagInheritanceForm
    template_name = 'products/variant_product_tags_form.html'
    
    def get_success_url(self):
        return reverse_lazy('products:variant_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, _("Product tags updated successfully."))
        return super().form_valid(form)


class ProductListWithTagFilterView(ListView):
    """List products filtered by tag."""
    model = ParentProduct
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        """Get products filtered by tag."""
        queryset = super().get_queryset()
        tag = get_object_or_404(Tag, id=self.kwargs.get('tag_id'))
        return queryset.filter(tags=tag)

    def get_context_data(self, **kwargs):
        """Add tag to context for filter display."""
        context = super().get_context_data(**kwargs)
        context['filter_tag'] = get_object_or_404(Tag, id=self.kwargs.get('tag_id'))
        return context


class TagDetailView(DetailView):
    """View for displaying tag details."""
    model = Tag
    template_name = "products/tag_detail.html"
    context_object_name = "tag"

    def get_context_data(self, **kwargs):
        """Add products with this tag to context."""
        context = super().get_context_data(**kwargs)
        context["products"] = ParentProduct.objects.filter(tags=self.object)
        return context


class ProductSearchAPIView(APIView):
    """
    API endpoint for searching Parent and Variant products.
    Accepts a 'q' query parameter for searching by SKU or Name.
    Returns a list of matched products, identifying the parent product for each match.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([], status=status.HTTP_200_OK)

        # Search in ParentProduct
        parent_matches = ParentProduct.objects.filter(
            Q(sku__icontains=query) | Q(name__icontains=query)
        ).distinct()

        # Search in VariantProduct
        variant_matches = VariantProduct.objects.filter(
            Q(sku__icontains=query) | Q(name__icontains=query)
        ).select_related('parent').distinct()

        results = []
        added_parent_ids = set()

        # Process parent matches first
        for parent in parent_matches:
            if parent.id not in added_parent_ids:
                results.append({
                    'id': parent.id,
                    'sku': parent.sku,
                    'name': parent.name,
                    'matched_sku': parent.sku,
                    'matched_name': parent.name,
                    'is_variant': False
                })
                added_parent_ids.add(parent.id)

        # Process variant matches, ensuring parent is included only once if matched directly too
        for variant in variant_matches:
            if variant.parent_id not in added_parent_ids:
                results.append({
                    'id': variant.parent.id,
                    'sku': variant.parent.sku,
                    'name': variant.parent.name,
                    'matched_sku': variant.sku,
                    'matched_name': variant.name,
                    'is_variant': True
                })
                added_parent_ids.add(variant.parent_id)

        # Optional: Limit the number of results
        MAX_RESULTS = 20
        results = results[:MAX_RESULTS]

        serializer = ProductSearchResultSerializer(results, many=True)
        return Response(serializer.data)
