"""
Global search API views.

This module provides API views for performing searches across multiple models
in the system.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Q, Prefetch

from pyerp.business_modules.sales.models import Customer, SalesRecord
from pyerp.business_modules.products.models import (
    ParentProduct, VariantProduct, ProductImage
)
from pyerp.business_modules.inventory.models import BoxSlot, StorageLocation


class GlobalSearchViewSet(viewsets.ViewSet):
    """
    API viewset for global search functionality.
    Allows searching across multiple models in the system.
    """

    def _get_primary_image_url(self, product_instance):
        """Helper: Get primary thumbnail URL for a product (Parent/Variant)."""
        primary_image = None
        # Check type and access images appropriately
        images_relation = None
        if isinstance(product_instance, ParentProduct):
            # Parent: Try finding image via prefetched variants or query fallback
            # Note: Query fallback might be inefficient.
            if hasattr(product_instance, 'prefetched_variants_with_images'):
                # Use prefetched data if available
                for variant in product_instance.prefetched_variants_with_images:
                    if hasattr(variant, 'images_prefetched'):
                        images_relation = variant.images_prefetched
                        if images_relation:
                            break  # Stop at the first variant with images
            else:  # Fallback to querying (less efficient)
                first_variant = product_instance.variants.prefetch_related(
                    'images'
                ).first()
                if first_variant:
                    images_relation = first_variant.images.all()
        elif isinstance(product_instance, VariantProduct):
            # Variant: Use prefetched images or query fallback
            if hasattr(product_instance, 'images_prefetched'):
                images_relation = product_instance.images_prefetched
            else:  # Fallback to querying
                images_relation = product_instance.images.all()

        if images_relation:
            # Prioritize: Produktfoto+Front > Produktfoto > Front > Primary > Any
            candidates = list(images_relation)  # Evaluate queryset
            primary_image = next((
                img for img in candidates
                if img.image_type == "Produktfoto" and img.is_front
            ), None)
            if not primary_image:
                primary_image = next((
                    img for img in candidates if img.image_type == "Produktfoto"
                ), None)
            if not primary_image:
                primary_image = next((
                    img for img in candidates if img.is_front
                ), None)
            if not primary_image:
                primary_image = next((
                    img for img in candidates if img.is_primary
                ), None)
            if not primary_image and candidates:
                primary_image = candidates[0]

        # Return thumbnail URL > full URL > None
        if primary_image:
            return primary_image.thumbnail_url or primary_image.image_url
        return None

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Perform a global search across multiple models.
        """
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Perform search on each model
        results = {
            "customers": self._search_customers(query),
            "sales_records": self._search_sales_records(query),
            "parent_products": self._search_parent_products(query),
            "variant_products": self._search_variant_products(query),
            "box_slots": self._search_box_slots(query),
            "storage_locations": self._search_storage_locations(query),
        }

        # Add counts for each result type
        counts = {key: len(value) for key, value in results.items()}
        total_count = sum(counts.values())

        response_data = {
            "query": query,
            "total_count": total_count,
            "counts": counts,
            "results": results,
        }

        return Response(response_data)

    def _search_customers(self, query):
        """Search customers by customer_number and name."""
        customers = Customer.objects.filter(
            Q(customer_number__icontains=query) | Q(name__icontains=query)
        )[:10]  # Limit results

        return [
            {
                "id": customer.id,
                "customer_number": customer.customer_number,
                "name": customer.name,
                "type": "customer",
            }
            for customer in customers
        ]

    def _search_sales_records(self, query):
        """Search sales records by record_number."""
        records = SalesRecord.objects.filter(
            record_number__icontains=query
        )[:10]  # Limit results

        return [
            {
                "id": record.id,
                "record_number": record.record_number,
                "record_type": record.record_type,
                "record_date": record.record_date,
                "customer": record.customer.name if record.customer else None,
                "type": "sales_record",
            }
            for record in records
        ]

    def _search_parent_products(self, query):
        """Search parent products by sku and name, include primary image."""
        # Prefetch variants and their images for efficiency
        prefetch_images = Prefetch(
            'variants__images',
            queryset=ProductImage.objects.order_by(
                '-is_primary', '-is_front', 'priority'
            ),
            to_attr='images_prefetched'
        )
        prefetch_variants_with_images = Prefetch(
            'variants',
            queryset=VariantProduct.objects.prefetch_related(
                prefetch_images
            ).order_by('id')[:1],  # Only need first variant for image
            to_attr='prefetched_variants_with_images'
        )

        products = ParentProduct.objects.filter(
            Q(sku__icontains=query) | Q(name__icontains=query)
        ).prefetch_related(prefetch_variants_with_images)[:10]  # Limit results

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "type": "parent_product",
                # "primary_image_thumbnail_url": self._get_primary_image_url(
                #     product
                # ),
            }
            for product in products
        ]

    def _search_variant_products(self, query):
        """Search variant products by sku, name, legacy_sku; include image."""
        # Prefetch images for variants
        prefetch_images = Prefetch(
            'images',
            queryset=ProductImage.objects.order_by(
                '-is_primary', '-is_front', 'priority'
            ),
            to_attr='images_prefetched'
        )
        products = VariantProduct.objects.filter(
            Q(sku__icontains=query)
            | Q(name__icontains=query)
            | Q(legacy_sku__icontains=query)
        ).prefetch_related(prefetch_images)[:10]  # Limit results

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "legacy_sku": product.legacy_sku,
                "type": "variant_product",
                "retail_price": product.retail_price,
                "wholesale_price": product.wholesale_price,
                "variant_code": product.variant_code,
                # "primary_image_thumbnail_url": self._get_primary_image_url(
                #     product
                # ),
            }
            for product in products
        ]

    def _search_box_slots(self, query):
        """Search box slots by barcode."""
        box_slots = BoxSlot.objects.filter(barcode__icontains=query)[:10]

        return [
            {
                "id": box_slot.id,
                "barcode": box_slot.barcode,
                "box_code": box_slot.box.code if box_slot.box else None,
                "slot_code": box_slot.slot_code,
                "type": "box_slot",
            }
            for box_slot in box_slots
        ]

    def _search_storage_locations(self, query):
        """Search storage locations by legacy_id."""
        locations = StorageLocation.objects.filter(
            Q(legacy_id__icontains=query)
            | Q(name__icontains=query)
        )[:10]

        return [
            {
                "id": location.id,
                "legacy_id": location.legacy_id,
                "name": location.name,
                "location_code": location.location_code,
                "type": "storage_location",
            }
            for location in locations
        ]
