from django.http import JsonResponse
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import BoxType, StorageLocation, Box

app_name = "inventory"


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
def box_types_list(request):
    """API endpoint to list all box types."""
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


@api_view(["GET"])
def storage_locations_list(request):
    """API endpoint to list all storage locations."""
    locations = StorageLocation.objects.all()
    data = [
        {
            "id": location.id,
            "name": location.name,
            "country": location.country,
            "city_building": location.city_building,
            "unit": location.unit,
            "compartment": location.compartment,
            "shelf": location.shelf,
            "location_code": location.location_code,
            "is_active": location.is_active,
        }
        for location in locations
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def boxes_list(request):
    """API endpoint to list all boxes."""
    boxes = Box.objects.all()
    data = [
        {
            "id": box.id,
            "code": box.code,
            "barcode": box.barcode,
            "box_type": {
                "id": box.box_type.id,
                "name": box.box_type.name,
            },
            "storage_location": {
                "id": box.storage_location.id,
                "name": box.storage_location.name,
            } if box.storage_location else None,
            "status": box.status,
            "purpose": box.purpose,
            "notes": box.notes,
            "available_slots": box.available_slots,
        }
        for box in boxes
    ]
    return Response(data)


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
]
