from django.http import JsonResponse
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from django.db import models

from .models import BoxType, StorageLocation, Box, BoxSlot, ProductStorage, BoxStorage

app_name = "inventory"
logger = logging.getLogger(__name__)


# Simple view that returns a placeholder response
@api_view(["GET"])
def placeholder_view(request):
    """A placeholder view that returns a simple JSON response."""
    return JsonResponse(
        {
            "message": "Inventory module available but not fully implemented",
            "status": "placeholder",
        },
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def box_types_list(request):
    """API endpoint to list all box types."""
    try:
        box_types = BoxType.objects.all()
        data = [
            {
                "id": box_type.id,
                "name": box_type.name,
                "description": box_type.description,
                "length": box_type.length,
                "width": box_type.width,
                "height": box_type.height,
                "weight_capacity": box_type.weight_capacity,
                "slot_count": box_type.slot_count,
                "slot_naming_scheme": box_type.slot_naming_scheme,
            }
            for box_type in box_types
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching box types: {e}")
        return Response(
            {"detail": "Failed to fetch box types"},
            status=500
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def boxes_list(request):
    """API endpoint to list all boxes."""
    try:
        # Get page number and size from query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        # Calculate offset and limit
        offset = (page - 1) * page_size
        limit = page_size

        # Get total count
        total_count = Box.objects.count()

        # Get paginated boxes with related data
        boxes = Box.objects.select_related('box_type').prefetch_related('slots').all()[offset:offset + limit]

        data = []
        for box in boxes:
            try:
                # Get the first slot with a storage location through box storage
                storage_location = None
                for slot in box.slots.all():
                    box_storage = slot.box_storage_items.select_related(
                        'product_storage__storage_location'
                    ).first()
                    if box_storage and box_storage.product_storage.storage_location:
                        storage_location = {
                            "id": box_storage.product_storage.storage_location.id,
                            "name": box_storage.product_storage.storage_location.name,
                        }
                        break

                box_data = {
                    "id": box.id,
                    "code": box.code,
                    "barcode": box.barcode,
                    "box_type": {
                        "id": box.box_type.id,
                        "name": box.box_type.name,
                    },
                    "storage_location": storage_location,
                    "status": box.status,
                    "purpose": box.purpose,
                    "notes": box.notes,
                    "available_slots": box.available_slots,
                }
                data.append(box_data)
            except Exception as box_error:
                logger.error(f"Error processing box {box.id}: {box_error}")
                continue
        
        return Response({
            'results': data,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
    except Exception as e:
        logger.error(f"Error fetching boxes: {e}")
        return Response(
            {"detail": "Failed to fetch boxes"},
            status=500
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_locations_list(request):
    """API endpoint to list all storage locations."""
    try:
        # Get all storage locations with product counts
        locations = StorageLocation.objects.annotate(
            product_count=models.Count(
                'stored_products',
                distinct=True
            )
        )
        
        data = [
            {
                "id": location.id,
                "name": location.name,
                "description": location.description,
                "country": location.country,
                "city_building": location.city_building,
                "unit": location.unit,
                "compartment": location.compartment,
                "shelf": location.shelf,
                "sale": location.sale,
                "special_spot": location.special_spot,
                "is_active": location.is_active,
                "product_count": location.product_count,
                "location_code": f"{location.country}-{location.city_building}-{location.unit}-{location.compartment}-{location.shelf}".strip("-")
            }
            for location in locations
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching storage locations: {e}")
        return Response(
            {"detail": "Failed to fetch storage locations"},
            status=500
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def products_by_location(request, location_id=None):
    """API endpoint to list products by storage location."""
    try:
        if not location_id:
            return Response(
                {"detail": "Storage location ID is required"},
                status=400
            )
        
        # Get products in the storage location
        product_storage_items = ProductStorage.objects.filter(
            storage_location_id=location_id
        ).select_related(
            'product',
            'storage_location'
        )
        
        # Get box storage items for these products
        box_storage_items = BoxStorage.objects.filter(
            product_storage__in=product_storage_items
        ).select_related(
            'box_slot',
            'box_slot__box'
        )
        
        # Group products by box and slot
        result = {}
        for box_item in box_storage_items:
            box = box_item.box_slot.box
            box_code = box.code
            slot_code = box_item.box_slot.slot_code
            product = box_item.product_storage.product
            
            if box_code not in result:
                result[box_code] = {
                    "box_id": box.id,
                    "box_code": box_code,
                    "slots": {}
                }
            
            if slot_code not in result[box_code]["slots"]:
                result[box_code]["slots"][slot_code] = {
                    "slot_id": box_item.box_slot.id,
                    "slot_code": slot_code,
                    "products": []
                }
            
            result[box_code]["slots"][slot_code]["products"].append({
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "quantity": box_item.quantity,
                "reservation_status": box_item.product_storage.reservation_status,
                "batch_number": box_item.batch_number,
                "date_stored": box_item.date_stored
            })
        
        # Convert to list format for easier consumption in frontend
        formatted_result = []
        for box_code, box_data in result.items():
            box_item = {
                "box_id": box_data["box_id"],
                "box_code": box_code,
                "slots": []
            }
            
            for slot_code, slot_data in box_data["slots"].items():
                box_item["slots"].append({
                    "slot_id": slot_data["slot_id"],
                    "slot_code": slot_code,
                    "products": slot_data["products"]
                })
            
            formatted_result.append(box_item)
        
        return Response(formatted_result)
    except Exception as e:
        logger.error(f"Error fetching products by location: {e}")
        return Response(
            {"detail": f"Failed to fetch products by location: {str(e)}"},
            status=500
        )


# URL patterns for the inventory app
urlpatterns = [
    path("status/", placeholder_view, name="status"),
    path("placeholder/", placeholder_view, name="placeholder"),
    path("box-types/", box_types_list, name="box_types_list"),
    path("boxes/", boxes_list, name="boxes_list"),
    path(
        "storage-locations/",
        storage_locations_list,
        name="storage_locations_list",
    ),
    path(
        "storage-locations/<int:location_id>/products/",
        products_by_location,
        name="products_by_location",
    ),
]
