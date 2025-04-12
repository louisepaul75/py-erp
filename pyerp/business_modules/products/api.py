"""
API ViewSets for the products module.

This module contains ViewSets and API classes that are documented 
using drf-spectacular to generate OpenAPI schema.
"""

from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from rest_framework import viewsets, filters, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
import logging
from django.db import connection

from pyerp.business_modules.products.models import ProductCategory, ParentProduct, VariantProduct
from pyerp.business_modules.products.serializers import ProductCategorySerializer, ParentProductSerializer, VariantProductSerializer
from pyerp.business_modules.business.models import Supplier
from pyerp.business_modules.products.serializers import SupplierSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List product categories",
        description="Returns a list of all product categories with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by category name (case-insensitive, partial match)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="code",
                description="Filter by category code (exact match)",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=ProductCategorySerializer(many=True),
                description="Successfully retrieved list of categories",
                examples=[
                    OpenApiExample(
                        name="category_list_example",
                        value=[
                            {
                                "id": 1,
                                "code": "CAT001",
                                "name": "Main Category",
                                "description": "This is the main category",
                                "parent": None,
                            },
                            {
                                "id": 2,
                                "code": "CAT002",
                                "name": "Sub Category",
                                "description": "This is a sub category",
                                "parent": 1,
                            }
                        ],
                    )
                ],
            ),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
        tags=["Products", "Categories"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a product category",
        description="Returns a single product category by its ID.",
        responses={
            200: ProductCategorySerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Category not found."),
        },
        tags=["Products", "Categories"],
    ),
    create=extend_schema(
        summary="Create a product category",
        description="Creates a new product category.",
        request=ProductCategorySerializer,
        responses={
            201: OpenApiResponse(
                response=ProductCategorySerializer,
                description="Category created successfully.",
            ),
            400: OpenApiResponse(description="Invalid data provided."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
        },
        tags=["Products", "Categories"],
    ),
    update=extend_schema(
        summary="Update a product category",
        description="Updates an existing product category.",
        request=ProductCategorySerializer,
        responses={
            200: ProductCategorySerializer,
            400: OpenApiResponse(description="Invalid data provided."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Category not found."),
        },
        tags=["Products", "Categories"],
    ),
    partial_update=extend_schema(
        summary="Partially update a product category",
        description="Updates specific fields of an existing product category.",
        request=ProductCategorySerializer,
        responses={
            200: ProductCategorySerializer,
            400: OpenApiResponse(description="Invalid data provided."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Category not found."),
        },
        tags=["Products", "Categories"],
    ),
    destroy=extend_schema(
        summary="Delete a product category",
        description="Deletes a product category. This action is irreversible.",
        responses={
            204: OpenApiResponse(description="Category deleted successfully."),
            401: OpenApiResponse(description="Authentication credentials were not provided."),
            404: OpenApiResponse(description="Category not found."),
        },
        tags=["Products", "Categories"],
    ),
)
class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    
    This ViewSet provides CRUD operations for ProductCategory objects.
    """
    
    queryset = ProductCategory.objects.all().order_by('name')
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code', 'name', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code']
    pagination_class = PageNumberPagination
    
    @extend_schema(
        summary="List child categories",
        description="Returns a list of child categories for a specified parent category.",
        responses={
            200: OpenApiResponse(
                response=ProductCategorySerializer(many=True),
                description="List of child categories",
            ),
            404: OpenApiResponse(description="Parent category not found."),
        },
        tags=["Products", "Categories"],
    )
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """Return all child categories for a given parent category."""
        try:
            parent = self.get_object()
            children = ProductCategory.objects.filter(parent=parent)
            serializer = self.get_serializer(children, many=True)
            return Response(serializer.data)
        except ProductCategory.DoesNotExist:
            return Response(
                {"detail": _("Parent category not found.")},
                status=status.HTTP_404_NOT_FOUND
            )
            
    @extend_schema(
        summary="Get category tree",
        description="Returns a hierarchical tree of all product categories.",
        responses={
            200: OpenApiResponse(
                description="Hierarchical tree of categories",
                examples=[
                    OpenApiExample(
                        name="category_tree_example",
                        value=[
                            {
                                "id": 1,
                                "code": "MAIN",
                                "name": "Main Category",
                                "children": [
                                    {
                                        "id": 2,
                                        "code": "SUB1",
                                        "name": "Sub Category 1",
                                        "children": []
                                    }
                                ]
                            }
                        ],
                    )
                ],
            ),
        },
        tags=["Products", "Categories"],
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get a hierarchical tree of categories."""
        # In a real implementation, this would build a nested tree structure
        # For simplicity, we're just returning a placeholder response
        root_categories = ProductCategory.objects.filter(parent=None)
        
        def build_tree(category):
            children = ProductCategory.objects.filter(parent=category)
            return {
                'id': category.id,
                'code': category.code,
                'name': category.name,
                'children': [build_tree(child) for child in children]
            }
            
        result = [build_tree(category) for category in root_categories]
        return Response(result)


@extend_schema(
    summary="List products",
    description="Returns a paginated list of products with optional filtering.",
    parameters=[
        OpenApiParameter(
            name="category",
            description="Filter by category ID",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="q",
            description="Search query for product name (case-insensitive, partial match)",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="in_stock",
            description="Filter by stock availability (true/1/yes to show only in-stock products)",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="is_active",
            description="Filter by active status (true/1/yes or false/0/no)",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="include_variants",
            description="Include variant details in the response (true/1/yes to include)",
            required=False,
            type=bool,
        ),
        OpenApiParameter(
            name="page",
            description="Page number for pagination",
            required=False,
            type=int,
            default=1,
        ),
        OpenApiParameter(
            name="page_size",
            description="Number of results per page",
            required=False,
            type=int,
            default=12,
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="List of products with pagination information",
            examples=[
                OpenApiExample(
                    name="product_list_example",
                    value={
                        "count": 100,
                        "results": [
                            {
                                "id": 1,
                                "sku": "PROD001",
                                "name": "Example Product",
                                "description": "This is an example product",
                                "is_active": True,
                                "is_new": False,
                                "variants_count": 3,
                                "primary_image": {
                                    "id": 101,
                                    "url": "https://example.com/image.jpg",
                                    "thumbnail_url": "https://example.com/thumbnail.jpg"
                                },
                                "variants": [
                                    {
                                        "id": 11,
                                        "sku": "PROD001-VAR1",
                                        "name": "Example Product - Red",
                                        "variant_code": "RED",
                                        "is_active": True,
                                        "parent": {
                                            "id": 1,
                                            "name": "Example Product",
                                            "sku": "PROD001"
                                        },
                                        "primary_image": {
                                            "id": 201,
                                            "url": "https://example.com/red.jpg",
                                            "thumbnail_url": "https://example.com/red-thumb.jpg"
                                        }
                                    }
                                ]
                            }
                        ],
                        "page": 1,
                        "page_size": 12,
                        "total_pages": 9
                    },
                )
            ],
        ),
        400: OpenApiResponse(description="Invalid input parameters."),
        401: OpenApiResponse(description="Authentication credentials were not provided."),
    },
    tags=["Products"],
)
class ProductListAPIView(APIView):
    """
    API view for listing products with filtering and pagination.
    """
    permission_classes = [IsAuthenticated]
    direct_search = False  # Default to normal search behavior
    
    def __init__(self, *args, **kwargs):
        self.direct_search = kwargs.pop('direct_search', False)
        super().__init__(*args, **kwargs)
    
    def get_product_data(self, product):
        """Helper method to format product data for API response."""
        product_data = {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "is_active": product.is_active,
            "is_new": product.is_new if hasattr(product, "is_new") else False,
            "legacy_base_sku": getattr(product, "legacy_base_sku", None),
        }
        
        # Add primary image if available
        if hasattr(product, "images") and product.images.exists():
            primary_image = None
            
            # Find the best image to use as primary
            for img_type in ["Produktfoto", ""]:
                for is_front in [True, False]:
                    for is_primary in [True, False]:
                        if not primary_image:
                            filters = {}
                            if img_type:
                                filters["image_type__iexact"] = img_type
                            if is_front:
                                filters["is_front"] = is_front
                            if is_primary:
                                filters["is_primary"] = is_primary
                                
                            candidate = product.images.filter(**filters).first()
                            if candidate:
                                primary_image = candidate
            
            # Fallback to first image if no primary found
            if not primary_image and product.images.exists():
                primary_image = product.images.first()
                
            if primary_image:
                product_data["primary_image"] = {
                    "id": primary_image.id,
                    "url": primary_image.image_url,
                    "thumbnail_url": getattr(primary_image, "thumbnail_url", primary_image.image_url),
                }
        
        return product_data
    
    def get(self, request):
        """Handle GET request for product listing with filtering and pagination."""
        try:
            # Start with the base queryset
            base_queryset = ParentProduct.objects.all()
            
            # Apply search filter (this is the most important part)
            search_query = request.GET.get("q")
            if search_query and search_query.strip():
                search_query = search_query.strip()
                print(f"Search query: '{search_query}'")  # Print to stdout for debugging
                
                # Use Q objects for OR conditions
                from django.db.models import Q
                
                # For direct search mode, only look for exact matches on specific fields
                if self.direct_search:
                    print(f"Using direct search mode for query '{search_query}'")
                    direct_matches = base_queryset.filter(
                        Q(sku=search_query) | 
                        Q(legacy_base_sku=search_query)
                    ).distinct()
                    
                    direct_match_count = direct_matches.count()
                    print(f"Direct matches found: {direct_match_count}")
                    
                    # If direct matches found, use only those results
                    if direct_match_count > 0:
                        products = direct_matches
                        print(f"Direct search matched products: {[p.name for p in products[:3]]}")
                    else:
                        # For direct search with no exact match, try a more permissive approach
                        products = base_queryset.filter(
                            Q(sku__icontains=search_query) |
                            Q(legacy_base_sku__icontains=search_query)
                        ).distinct()
                        print(f"Fallback search found {products.count()} products")
                else:
                    # Standard search behavior - prioritize direct matches but fall back to broader search
                    # Direct lookups for exact matches first
                    direct_match_products = base_queryset.filter(
                        Q(sku=search_query) | 
                        Q(legacy_base_sku=search_query)
                    ).distinct()
                    
                    direct_match_count = direct_match_products.count()
                    print(f"Direct match found {direct_match_count} products")
                    
                    # If direct matches found, use those results
                    if direct_match_count > 0:
                        products = direct_match_products
                        print(f"Using direct matches: {[p.sku for p in products[:5]]}")
                    else:
                        # Otherwise fall back to the broader search
                        products = base_queryset.filter(
                            Q(name__icontains=search_query) |
                            Q(sku__icontains=search_query) |
                            Q(legacy_base_sku__icontains=search_query)
                        ).distinct()
                        print(f"Fallback search found {products.count()} products")
                    
                    # If we still get no results but we have a numeric query, try again with specific patterns
                    if products.count() == 0 and search_query.isdigit():
                        products = base_queryset.filter(
                            Q(sku__contains=search_query) |
                            Q(legacy_base_sku=search_query)  # Direct match for legacy_base_sku
                        ).distinct()
                        print(f"Numeric search found {products.count()} products")
                        
                    # Debug output
                    if products.count() > 0:
                        print(f"First 3 results: {[f'{p.name} (SKU: {p.sku}, Legacy: {p.legacy_base_sku})' for p in products[:3]]}")
            else:
                products = base_queryset
            
            # Apply other filters below...
            category_id = request.GET.get("category")
            if category_id:
                try:
                    category_id = int(category_id)
                    products = products.filter(category_id=category_id)
                except (ValueError, TypeError):
                    return Response(
                        {"error": "Invalid category ID format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Apply stock filter
            in_stock = request.GET.get("in_stock")
            if in_stock and in_stock.lower() in ("true", "1", "yes"):
                products = products.exclude(stock_quantity__isnull=True).filter(stock_quantity__gt=0)
            
            # Apply active status filter
            is_active = request.GET.get("is_active")
            if is_active is not None:
                is_active_bool = is_active.lower() in ("true", "1", "yes")
                products = products.filter(is_active=is_active_bool)
            
            # Handle pagination
            try:
                page = int(request.GET.get("page", 1))
                page_size = int(request.GET.get("page_size", 12))
                
                if page < 1 or page_size < 1 or page_size > 100:
                    return Response(
                        {"error": "Invalid pagination parameters. Page must be ≥ 1 and page_size must be between 1 and 100."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {"error": "Invalid pagination parameters. Page and page_size must be integers."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get total count and paginate
            total_count = products.count()
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Make sure we're not returning empty results if we have matching products
            if total_count > 0 and start_index >= total_count:
                page = 1
                start_index = 0
                end_index = page_size
                
            products = products[start_index:end_index]
            
            # Format the response data
            products_data = []
            for product in products:
                product_data = self.get_product_data(product)
                products_data.append(product_data)
            
            # Return the response with pagination info
            return Response({
                "count": total_count,
                "results": products_data,
                "page": page,
                "page_size": page_size,
                "total_pages": max(1, (total_count + page_size - 1) // page_size),
                "next": self._get_next_page_url(request, page, page_size, total_count),
                "previous": self._get_prev_page_url(request, page),
                "search_query": search_query or "",  # Include the search query in response for debugging
            })
        except Exception as e:
            print(f"Error in ProductListAPIView.get: {str(e)}")
            import traceback
            traceback.print_exc()  # Print stack trace for better debugging
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def _get_next_page_url(self, request, current_page, page_size, total_count):
        """Helper to generate the next page URL."""
        total_pages = (total_count + page_size - 1) // page_size
        if current_page >= total_pages:
            return None
            
        params = request.GET.copy()
        params['page'] = current_page + 1
        base_url = request.build_absolute_uri(request.path)
        return f"{base_url}?{params.urlencode()}"
        
    def _get_prev_page_url(self, request, current_page):
        """Helper to generate the previous page URL."""
        if current_page <= 1:
            return None
            
        params = request.GET.copy()
        params['page'] = current_page - 1
        base_url = request.build_absolute_uri(request.path)
        return f"{base_url}?{params.urlencode()}"


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get product details",
        description="Retrieves detailed information about a specific product by ID.",
        responses={
            200: ParentProductSerializer,
            404: OpenApiResponse(description="Product not found."),
        },
        tags=["Products"],
    ),
    partial_update=extend_schema(
        summary="Update product",
        description="Updates specific fields of an existing product.",
        request=ParentProductSerializer,
        responses={
            200: ParentProductSerializer,
            400: OpenApiResponse(description="Invalid data provided."),
            404: OpenApiResponse(description="Product not found."),
        },
        tags=["Products"],
    ),
    create=extend_schema(
        summary="Create a product",
        description="Creates a new product (Parent or Variant based on payload).",
        request=ParentProductSerializer,
        responses={
            201: OpenApiResponse(
                response=ParentProductSerializer,
                description="Product created successfully.",
            ),
            400: OpenApiResponse(description="Invalid data provided."),
        },
        tags=["Products"],
    ),
)
class ProductDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving, updating, creating, and deleting product details.
    """
    queryset = ParentProduct.objects.all()
    serializer_class = ParentProductSerializer
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a product by its ID and include a list of all suppliers.
        """
        product = self.get_object()
        serializer = self.get_serializer(product)
        product_data = serializer.data  # Product data including the linked supplier

        # Fetch all suppliers and add the list to the response
        all_suppliers = Supplier.objects.all()
        suppliers_serializer = SupplierSerializer(all_suppliers, many=True)
        product_data['suppliers'] = suppliers_serializer.data

        return Response(product_data)
    
    def partial_update(self, request, pk=None):
        """
        Update specific fields of a product.
        """
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='variants')
    @extend_schema(
        summary="List variants for a product",
        description="Returns a list of variants associated with a specific parent product.",
        responses={
            200: VariantProductSerializer(many=True),
            404: OpenApiResponse(description="Parent product not found."),
        },
        tags=["Products", "Variants"]
    )
    def variants(self, request, pk=None):
        """Return a list of variants for the given parent product."""
        parent_product = self.get_object() # This gets the ParentProduct instance based on pk
        variants_queryset = VariantProduct.objects.filter(parent=parent_product).order_by('variant_code', 'name')
        serializer = VariantProductSerializer(variants_queryset, many=True)
        return Response(serializer.data)

    # create, retrieve, update, partial_update, destroy methods 
    # are now inherited from ModelViewSet.
    # We might need to override perform_create later for custom logic.


@extend_schema(
    summary="Get variant details",
    description="Retrieves detailed information about a specific product variant by ID.",
    responses={
        200: OpenApiResponse(
            description="Variant details",
            examples=[
                OpenApiExample(
                    name="variant_detail_example",
                    value={
                        "id": 1,
                        "sku": "VAR001",
                        "name": "Product Variant 1",
                        "variant_code": "V1",
                        "description": "This is a product variant",
                        "is_active": True,
                        "parent": {
                            "id": 101,
                            "name": "Parent Product",
                            "sku": "PROD101"
                        },
                        "attributes": [
                            {"name": "Color", "value": "Red"},
                            {"name": "Size", "value": "Large"}
                        ],
                        "images": [
                            {
                                "id": 1,
                                "url": "https://example.com/image.jpg",
                                "thumbnail_url": "https://example.com/thumbnail.jpg",
                                "is_primary": True,
                                "is_front": True,
                                "image_type": "Produktfoto"
                            }
                        ],
                        "inherits_tags": True
                    },
                )
            ],
        ),
        404: OpenApiResponse(description="Variant not found."),
    },
    tags=["Products", "Variants"],
)
class VariantDetailAPIView(APIView):
    """
    API view for retrieving variant details.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get variant details by ID."""
        variant = get_object_or_404(VariantProduct, pk=pk)
        
        # Build response data
        variant_data = {
            "id": variant.id,
            "sku": variant.sku,
            "name": variant.name,
            "variant_code": variant.variant_code,
            "description": variant.description,
            "is_active": variant.is_active,
        }
        
        # Add parent product info
        if variant.parent:
            variant_data["parent"] = {
                "id": variant.parent.id,
                "name": variant.parent.name,
                "sku": variant.parent.sku,
            }
            
        # Add attributes if available
        if hasattr(variant, "attributes") and variant.attributes.exists():
            variant_data["attributes"] = [
                {"name": attr.name, "value": attr.value}
                for attr in variant.attributes.all()
            ]
            
        # Add images if available
        if hasattr(variant, "images") and variant.images.exists():
            variant_data["images"] = [
                {
                    "id": img.id,
                    "url": img.image_url,
                    "thumbnail_url": getattr(img, "thumbnail_url", img.image_url),
                    "is_primary": getattr(img, "is_primary", False),
                    "is_front": getattr(img, "is_front", False),
                    "image_type": getattr(img, "image_type", None),
                }
                for img in variant.images.all()
            ]
            
        # Add tag inheritance info if available
        if hasattr(variant, "inherits_tags"):
            variant_data["inherits_tags"] = variant.inherits_tags()
            
        return Response(variant_data) 