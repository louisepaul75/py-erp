from django.http import JsonResponse
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from django.db import models

from .models import BoxType, StorageLocation, Box, ProductStorage, BoxStorage, BoxSlot
from .services import InventoryService

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
        return Response({"detail": "Failed to fetch box types"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def boxes_list(request):
    """API endpoint to list all boxes."""
    try:
        # Get page number and size from query parameters
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        # Calculate offset and limit
        offset = (page - 1) * page_size
        limit = page_size

        # Get total count
        total_count = Box.objects.count()

        # Get paginated boxes with related data
        boxes = (
            Box.objects.select_related("box_type")
            .prefetch_related("slots")
            .all()[offset : offset + limit]
        )

        data = []
        for box in boxes:
            try:
                # Get the first slot with a storage location through box storage
                storage_location = None
                for slot in box.slots.all():
                    box_storage = slot.box_storage_items.select_related(
                        "product_storage__storage_location"
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

        return Response(
            {
                "results": data,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
            }
        )
    except Exception as e:
        logger.error(f"Error fetching boxes: {e}")
        return Response({"detail": "Failed to fetch boxes"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_locations_list(request):
    """API endpoint to list all storage locations."""
    try:
        # Get all storage locations with product counts
        locations = StorageLocation.objects.annotate(
            product_count=models.Count("stored_products", distinct=True)
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
                "location_code": f"{location.country}-{location.city_building}-{location.unit}-{location.compartment}-{location.shelf}".strip(
                    "-"
                ),
            }
            for location in locations
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching storage locations: {e}")
        return Response({"detail": "Failed to fetch storage locations"}, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def products_by_location(request, location_id=None):
    """API endpoint to list products by storage location."""
    try:
        if not location_id:
            return Response({"detail": "Storage location ID is required"}, status=400)

        # Get products in the storage location
        product_storage_items = ProductStorage.objects.filter(
            storage_location_id=location_id
        ).select_related("product", "storage_location")

        # Get box storage items for these products
        box_storage_items = BoxStorage.objects.filter(
            product_storage__in=product_storage_items
        ).select_related("box_slot", "box_slot__box")

        # Group products by box and slot
        result = {}
        for box_item in box_storage_items:
            box = box_item.box_slot.box
            box_code = box.code
            slot_code = box_item.box_slot.slot_code
            product = box_item.product_storage.product

            if box_code not in result:
                result[box_code] = {"box_id": box.id, "box_code": box_code, "slots": {}}

            if slot_code not in result[box_code]["slots"]:
                result[box_code]["slots"][slot_code] = {
                    "slot_id": box_item.box_slot.id,
                    "slot_code": slot_code,
                    "products": [],
                }

            result[box_code]["slots"][slot_code]["products"].append(
                {
                    "id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                    "quantity": box_item.quantity,
                    "reservation_status": box_item.product_storage.reservation_status,
                    "batch_number": box_item.batch_number,
                    "date_stored": box_item.date_stored,
                }
            )

        # Convert to list format for easier consumption in frontend
        formatted_result = []
        for box_code, box_data in result.items():
            box_item = {"box_id": box_data["box_id"], "box_code": box_code, "slots": []}

            for slot_code, slot_data in box_data["slots"].items():
                box_item["slots"].append(
                    {
                        "slot_id": slot_data["slot_id"],
                        "slot_code": slot_code,
                        "products": slot_data["products"],
                    }
                )

            formatted_result.append(box_item)

        return Response(formatted_result)
    except Exception as e:
        logger.error(f"Error fetching products by location: {e}")
        return Response(
            {"detail": f"Failed to fetch products by location: {str(e)}"}, status=500
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def locations_by_product(request, product_id=None):
    """API endpoint to list storage locations for a specific product."""
    try:
        if not product_id:
            return Response({"detail": "Product ID is required"}, status=400)

        # Get storage locations for the product
        product_storage_items = ProductStorage.objects.filter(
            product_id=product_id
        ).select_related("product", "storage_location")

        # Format the response
        result = []
        for item in product_storage_items:
            if item.storage_location:
                location = item.storage_location
                result.append(
                    {
                        "id": location.id,
                        "name": location.name,
                        "location_code": f"{location.country}-{location.city_building}-{location.unit}-{location.compartment}-{location.shelf}".strip(
                            "-"
                        ),
                        "quantity": item.quantity,
                        "reservation_status": item.reservation_status,
                        "country": location.country,
                        "city_building": location.city_building,
                        "unit": location.unit,
                        "compartment": location.compartment,
                        "shelf": location.shelf,
                    }
                )

        return Response(result)
    except Exception as e:
        logger.error(f"Error fetching locations by product: {e}")
        return Response(
            {"detail": f"Failed to fetch locations by product: {str(e)}"}, status=500
        )


# New endpoints for inventory operations

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_box(request):
    """API endpoint to move a box to a different storage location."""
    try:
        box_id = request.data.get("box_id")
        target_location_id = request.data.get("target_location_id")

        if not box_id or not target_location_id:
            return Response(
                {"detail": "Box ID and target location ID are required"},
                status=400,
            )

        try:
            box = Box.objects.get(id=box_id)
            target_location = StorageLocation.objects.get(id=target_location_id)
        except (Box.DoesNotExist, StorageLocation.DoesNotExist):
            return Response(
                {"detail": "Box or target location not found"},
                status=404,
            )

        try:
            updated_box = InventoryService.move_box(
                box=box,
                target_storage_location=target_location,
                user=request.user,
            )
            
            return Response({
                "id": updated_box.id,
                "code": updated_box.code,
                "status": updated_box.status,
                "storage_location": {
                    "id": updated_box.storage_location.id,
                    "name": updated_box.storage_location.name,
                    "location_code": updated_box.storage_location.location_code,
                } if updated_box.storage_location else None,
                "message": f"Box successfully moved to {updated_box.storage_location}",
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error moving box: {e}")
        return Response({"detail": "Failed to move box"}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_to_box(request):
    """API endpoint to add a product to a box slot."""
    try:
        product_id = request.data.get("product_id")
        box_slot_id = request.data.get("box_slot_id")
        quantity = request.data.get("quantity")
        batch_number = request.data.get("batch_number")
        expiry_date = request.data.get("expiry_date")

        if not product_id or not box_slot_id or not quantity:
            return Response(
                {"detail": "Product ID, box slot ID, and quantity are required"},
                status=400,
            )

        try:
            from pyerp.business_modules.products.models import VariantProduct
            product = VariantProduct.objects.get(id=product_id)
            box_slot = BoxSlot.objects.get(id=box_slot_id)
            quantity = int(quantity)
        except (VariantProduct.DoesNotExist, BoxSlot.DoesNotExist, ValueError):
            return Response(
                {"detail": "Product, box slot not found, or invalid quantity"},
                status=404,
            )

        try:
            box_storage = InventoryService.add_product_to_box_slot(
                product=product,
                box_slot=box_slot,
                quantity=quantity,
                batch_number=batch_number,
                expiry_date=expiry_date,
                user=request.user,
            )
            
            return Response({
                "id": box_storage.id,
                "product": {
                    "id": product.id,
                    "name": str(product),
                },
                "box_slot": {
                    "id": box_slot.id,
                    "code": box_slot.slot_code,
                    "box_code": box_slot.box.code,
                },
                "quantity": box_storage.quantity,
                "message": f"Added {quantity} of product {product} to box slot {box_slot}",
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error adding product to box: {e}")
        return Response({"detail": "Failed to add product to box"}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_product_between_boxes(request):
    """API endpoint to move products between box slots."""
    try:
        source_box_storage_id = request.data.get("source_box_storage_id")
        target_box_slot_id = request.data.get("target_box_slot_id")
        quantity = request.data.get("quantity")

        if not source_box_storage_id or not target_box_slot_id or not quantity:
            return Response(
                {"detail": "Source box storage ID, target box slot ID, and quantity are required"},
                status=400,
            )

        try:
            source_box_storage = BoxStorage.objects.get(id=source_box_storage_id)
            target_box_slot = BoxSlot.objects.get(id=target_box_slot_id)
            quantity = int(quantity)
        except (BoxStorage.DoesNotExist, BoxSlot.DoesNotExist, ValueError):
            return Response(
                {"detail": "Source box storage or target box slot not found, or invalid quantity"},
                status=404,
            )

        try:
            source_updated, target_updated = InventoryService.move_product_between_box_slots(
                source_box_storage=source_box_storage,
                target_box_slot=target_box_slot,
                quantity=quantity,
                user=request.user,
            )
            
            product = target_updated.product_storage.product
            
            return Response({
                "product": {
                    "id": product.id,
                    "name": str(product),
                },
                "source_box_slot": {
                    "id": source_box_storage.box_slot.id,
                    "code": source_box_storage.box_slot.slot_code,
                    "box_code": source_box_storage.box_slot.box.code,
                    "remaining_quantity": source_updated.quantity if source_updated else 0,
                },
                "target_box_slot": {
                    "id": target_box_slot.id,
                    "code": target_box_slot.slot_code,
                    "box_code": target_box_slot.box.code,
                    "quantity": target_updated.quantity,
                },
                "quantity_moved": quantity,
                "message": f"Moved {quantity} units of product {product} between box slots",
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error moving product between boxes: {e}")
        return Response({"detail": "Failed to move product between boxes"}, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_product_from_box(request):
    """API endpoint to remove a product from a box slot."""
    try:
        box_storage_id = request.data.get("box_storage_id")
        quantity = request.data.get("quantity")
        reason = request.data.get("reason")

        if not box_storage_id or not quantity:
            return Response(
                {"detail": "Box storage ID and quantity are required"},
                status=400,
            )

        try:
            box_storage = BoxStorage.objects.get(id=box_storage_id)
            quantity = int(quantity)
        except (BoxStorage.DoesNotExist, ValueError):
            return Response(
                {"detail": "Box storage not found or invalid quantity"},
                status=404,
            )

        try:
            updated_box_storage = InventoryService.remove_product_from_box_slot(
                box_storage=box_storage,
                quantity=quantity,
                reason=reason,
                user=request.user,
            )
            
            product = box_storage.product_storage.product
            box_slot = box_storage.box_slot
            
            return Response({
                "product": {
                    "id": product.id,
                    "name": str(product),
                },
                "box_slot": {
                    "id": box_slot.id,
                    "code": box_slot.slot_code,
                    "box_code": box_slot.box.code,
                },
                "quantity_removed": quantity,
                "remaining_quantity": updated_box_storage.quantity if updated_box_storage else 0,
                "message": f"Removed {quantity} units of product {product} from box slot {box_slot}",
            })
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error removing product from box: {e}")
        return Response({"detail": "Failed to remove product from box"}, status=500)


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
    path(
        "products/<int:product_id>/locations/",
        locations_by_product,
        name="locations_by_product",
    ),
    path("api/move-box/", move_box, name="move_box"),
    path("api/add-product-to-box/", add_product_to_box, name="add_product_to_box"),
    path("api/move-product-between-boxes/", move_product_between_boxes, name="move_product_between_boxes"),
    path("api/remove-product-from-box/", remove_product_from_box, name="remove_product_from_box"),
]
