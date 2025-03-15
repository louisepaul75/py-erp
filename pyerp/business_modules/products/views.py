"""
Views for the products app.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pyerp.business_modules.products.forms import ProductSearchForm
from pyerp.business_modules.products.models import (
    ParentProduct,
    ProductCategory,
    VariantProduct,
)


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
        Get product by ID or slug.
        """
        if self.kwargs.get("pk"):
            return get_object_or_404(ParentProduct, pk=self.kwargs["pk"])
        if self.kwargs.get("slug"):
            return get_object_or_404(ParentProduct, slug=self.kwargs["slug"])

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
            "message": "Image functionality has been removed in the simplified model",
        },
    )


# API Views
# ---------


class ProductAPIView(APIView):
    """Base class for API views"""

    permission_classes = [IsAuthenticated]

    def get_product_data(self, product):
        """Convert a product model to a dictionary for JSON response"""
        try:
            product_data = {
                "id": product.id,
                "name": product.name,
                "sku": product.sku,
                "description": getattr(product, "description", ""),
                "list_price": float(product.list_price) if product.list_price else None,
                "stock_quantity": product.stock_quantity,
                "is_hanging": getattr(product, "is_hanging", False),
                "is_one_sided": getattr(product, "is_one_sided", False),
            }

            # Initialize images as empty to avoid undefined
            product_data["images"] = []
            product_data["primary_image"] = None

            # Add category if available
            if hasattr(product, "category") and product.category:
                try:
                    product_data["category"] = {
                        "id": product.category.id,
                        "name": product.category.name,
                        "code": getattr(product.category, "code", ""),
                    }
                except Exception as e:
                    print(f"Error getting category for product {product.id}: {e!s}")
                    product_data["category"] = None

            # Add variants count for parent products
            if isinstance(product, ParentProduct):
                try:
                    # Skip the query if we already have the count from annotation
                    if hasattr(product, 'variants_count'):
                        product_data["variants_count"] = product.variants_count
                    else:
                        variants_count = VariantProduct.objects.filter(
                            parent=product,
                        ).count()
                        product_data["variants_count"] = variants_count
                except Exception as e:
                    print(
                        f"Error getting variants count for product {product.id}: {e!s}",
                    )
                    product_data["variants_count"] = 0

            # Add images if available
            if hasattr(product, "images"):
                try:
                    images = list(product.images.all().select_related())

                    # Find primary image using priority order
                    primary_image = None
                    for priority in [
                        "Produktfoto_front",
                        "Produktfoto",
                        "front",
                        "primary",
                        "any",
                    ]:
                        if primary_image:
                            break

                        for img in images:
                            if (
                                (
                                    priority == "Produktfoto_front"
                                    and img.image_type == "Produktfoto"
                                    and img.is_front
                                )
                                or (
                                    priority == "Produktfoto"
                                    and img.image_type == "Produktfoto"
                                )
                                or (priority == "front" and img.is_front)
                                or (priority == "primary" and img.is_primary)
                                or priority == "any"
                            ):
                                primary_image = img
                                break

                    # Add primary image if found
                    if primary_image:
                        product_data["primary_image"] = {
                            "id": primary_image.id,
                            "url": primary_image.image_url,
                            "thumbnail_url": getattr(
                                primary_image,
                                "thumbnail_url",
                                primary_image.image_url,
                            ),
                            "is_primary": primary_image.is_primary,
                            "is_front": primary_image.is_front,
                            "image_type": primary_image.image_type,
                        }

                    # Add all valid images
                    for image in images:
                        if hasattr(image, "image_url") and image.image_url:
                            product_data["images"].append(
                                {
                                    "id": image.id,
                                    "url": image.image_url,
                                    "thumbnail_url": getattr(
                                        image,
                                        "thumbnail_url",
                                        image.image_url,
                                    ),
                                    "is_primary": image.is_primary,
                                    "is_front": image.is_front,
                                    "image_type": image.image_type,
                                },
                            )
                except Exception as e:
                    print(f"Error processing images for product {product.id}: {e!s}")

            return product_data

        except Exception as e:
            print(
                f"Error in get_product_data for product {getattr(product, 'id', 'unknown')}: {e!s}",
            )
            return {
                "id": getattr(product, "id", None),
                "name": getattr(product, "name", "Unknown Product"),
                "sku": getattr(product, "sku", ""),
                "images": [],
                "primary_image": None,
            }


class ProductListAPIView(ProductAPIView):
    """API view for listing products"""

    def get(self, request):
        """Handle GET request for product listing"""
        # Start with an optimized queryset that includes related data
        products = ParentProduct.objects.select_related("category")
        
        # Use annotation to count variants in a single query instead of N+1 queries
        products = products.annotate(variants_count=Count('variants'))

        # Check if we need to include variants early to optimize the query
        include_variants = request.GET.get("include_variants", "").lower() in (
            "true",
            "1",
            "yes",
        )
        
        # Consolidate prefetch_related calls to avoid conflicts
        if include_variants:
            variant_qs = VariantProduct.objects.select_related(
                "category"
            ).prefetch_related("images")
            products = products.prefetch_related(
                Prefetch("variants", queryset=variant_qs)
            )
        else:
            # Only prefetch images for variants if we're not including full variant data
            products = products.prefetch_related('variants__images')

        # Apply filters from query parameters
        category_id = request.GET.get("category")
        if category_id:
            try:
                category_id = int(category_id)
                products = products.filter(category_id=category_id)
            except (ValueError, TypeError):
                print(f"Invalid category_id format: {category_id}")

        search_query = request.GET.get("q")
        if search_query:
            products = products.filter(name__icontains=search_query)

        # Handle in_stock filter
        in_stock = request.GET.get("in_stock")
        if in_stock and in_stock.lower() in ("true", "1", "yes"):
            products = products.exclude(stock_quantity__isnull=True).filter(
                stock_quantity__gt=0,
            )

        # Handle is_active filter
        is_active = request.GET.get("is_active")
        if is_active is not None:  # Check if parameter was provided
            is_active_bool = is_active.lower() in ("true", "1", "yes")
            products = products.filter(is_active=is_active_bool)

        # Handle pagination
        try:
            page = int(request.GET.get("page", 1))
            page_size = int(request.GET.get("page_size", 12))
        except (ValueError, TypeError):
            page = 1
            page_size = 12

        # Calculate start and end indices
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Get total count before slicing
        total_count = products.count()

        # Slice the queryset for pagination
        products = products[start_index:end_index]

        # Convert products to JSON-serializable format
        products_data = []
        for product in products:
            product_data = self.get_product_data(product)
            
            # Use the annotated variants_count instead of making a separate query
            if hasattr(product, 'variants_count'):
                product_data["variants_count"] = product.variants_count

            # Add variants data if requested
            if include_variants:
                variants_data = []
                # This will use the prefetched data
                for variant in product.variants.all():
                    variant_data = self.get_product_data(variant)
                    variants_data.append(variant_data)
                product_data["variants"] = variants_data

            products_data.append(product_data)

        # Return JSON response with pagination info
        return Response(
            {
                "count": total_count,
                "results": products_data,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
            },
        )


class ProductDetailAPIView(ProductAPIView):
    """API view for product details"""

    def get(self, request, pk=None, slug=None):
        """Handle GET request for product detail"""
        if pk:
            product = get_object_or_404(ParentProduct, pk=pk)
        elif slug:
            product = get_object_or_404(ParentProduct, slug=slug)
        else:
            return Response({"error": "Product not found"}, status=404)

        # Get basic product data
        product_data = self.get_product_data(product)

        # Add variants
        variants = VariantProduct.objects.filter(parent=product)
        variants_data = []
        for variant in variants:
            variant_data = self.get_product_data(variant)
            variants_data.append(variant_data)
        product_data["variants"] = variants_data

        # Return JSON response
        return Response(product_data)

    def patch(self, request, pk=None, slug=None):
        """Handle PATCH request for product update"""
        if pk:
            product = get_object_or_404(ParentProduct, pk=pk)
        elif slug:
            product = get_object_or_404(ParentProduct, slug=slug)
        else:
            return Response({"error": "Product not found"}, status=404)

        # Update fields
        if "name" in request.data:
            product.name = request.data["name"]
        if "description" in request.data:
            product.description = request.data["description"]
        if "is_hanging" in request.data:
            product.is_hanging = request.data["is_hanging"]
        if "is_one_sided" in request.data:
            product.is_one_sided = request.data["is_one_sided"]

        # Save changes
        product.save()

        # Return updated product data
        return Response(self.get_product_data(product))


class VariantDetailAPIView(ProductAPIView):
    """API view for variant details"""

    def get(self, request, pk):
        """Handle GET request for variant detail"""
        variant = get_object_or_404(VariantProduct, pk=pk)

        # Get basic variant data
        variant_data = self.get_product_data(variant)

        # Add parent product info
        if variant.parent:
            variant_data["parent"] = {
                "id": variant.parent.id,
                "name": variant.parent.name,
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

        # Return JSON response
        return Response(variant_data)


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
