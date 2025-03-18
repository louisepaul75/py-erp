"""
Global search API views.

This module provides API views for performing searches across multiple models in the system.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models import Q

from pyerp.business_modules.sales.models import Customer, SalesRecord
from pyerp.business_modules.products.models import ParentProduct, VariantProduct
from pyerp.business_modules.inventory.models import BoxSlot, StorageLocation


class GlobalSearchViewSet(viewsets.ViewSet):
    """
    API viewset for global search functionality.
    Allows searching across multiple models in the system.
    """

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
        )[
            :10
        ]  # Limit to 10 results

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
        records = SalesRecord.objects.filter(record_number__icontains=query)[
            :10
        ]  # Limit to 10 results

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
        """Search parent products by sku and name."""
        products = ParentProduct.objects.filter(
            Q(sku__icontains=query) | Q(name__icontains=query)
        )[
            :10
        ]  # Limit to 10 results

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "type": "parent_product",
            }
            for product in products
        ]

    def _search_variant_products(self, query):
        """Search variant products by sku, name, and legacy_sku."""
        products = VariantProduct.objects.filter(
            Q(sku__icontains=query)
            | Q(name__icontains=query)
            | Q(legacy_sku__icontains=query)
        )[
            :10
        ]  # Limit to 10 results

        return [
            {
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "legacy_sku": product.legacy_sku,
                "type": "variant_product",
            }
            for product in products
        ]

    def _search_box_slots(self, query):
        """Search box slots by barcode."""
        box_slots = BoxSlot.objects.filter(barcode__icontains=query)[
            :10
        ]  # Limit to 10 results

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
        locations = StorageLocation.objects.filter(legacy_id__icontains=query)[
            :10
        ]  # Limit to 10 results

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
