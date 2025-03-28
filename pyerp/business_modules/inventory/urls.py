from django.http import JsonResponse
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from django.db import models
from datetime import datetime

from .models import BoxType, StorageLocation, Box, ProductStorage, BoxStorage, BoxSlot
from .services import InventoryService
from pyerp.business_modules.sales.models import SalesRecord, SalesRecordItem

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
    """
    API endpoint to list all box types.
    
    Returns:
        200: List of box types
        500: Server error
    """
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
                "weight_capacity": box_type.weight_empty,
                "slot_count": box_type.slot_count,
                "slot_naming_scheme": box_type.slot_naming_scheme,
            }
            for box_type in box_types
        ]
        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching box types: {e}")
        return Response({
            "detail": "Failed to fetch box types"
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def boxes_list(request):
    """
    API endpoint to list all boxes with pagination.
    
    Query Parameters:
        page: Page number (default: 1)
        page_size: Number of items per page (default: 10)
        
    Returns:
        200: List of boxes with pagination info
        500: Server error
    """
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        # Calculate pagination
        offset = (page - 1) * page_size
        limit = page_size

        # Get total count using cached query
        total_count = Box.objects.count()
        logger.info(f"Total boxes count: {total_count}")

        try:
            # Optimize query with joins and annotations
            boxes = (
                Box.objects.select_related("box_type")
                .prefetch_related("slots")
                .all()[offset:offset + limit]
            )
            
            logger.info("Base query constructed successfully")
            logger.info(f"Fetched {len(boxes)} boxes for page {page}")

            data = []
            for box in boxes:
                box_data = {
                    "id": box.id,
                    "code": box.code,
                    "barcode": box.barcode,
                    "box_type": {
                        "id": box.box_type.id,
                        "name": box.box_type.name,
                    },
                    "status": box.status,
                    "purpose": box.purpose,
                    "notes": box.notes,
                    "available_slots": box.available_slots,
                }
                data.append(box_data)
                
            logger.info(f"Successfully processed {len(data)} boxes")

            return Response({
                "results": data,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
            })
            
        except Exception as e:
            logger.error(f"Database query error: {str(e)}", exc_info=True)
            return Response({
                "detail": "Failed to fetch boxes"
            }, status=500)
            
    except Exception as e:
        logger.error(f"Unexpected error in boxes_list: {str(e)}", exc_info=True)
        return Response({
            "detail": f"Failed to fetch boxes"
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_locations_list(request):
    """
    API endpoint to list all storage locations.
    
    Returns:
        200: List of storage locations
        500: Server error
    """
    try:
        locations = StorageLocation.objects.annotate(
            product_count=models.Count("stored_products", distinct=True)
        )

        data = []
        for location in locations:
            location_code = "-".join(filter(None, [
                location.country,
                location.city_building,
                location.unit,
                location.compartment,
                location.shelf
            ]))
            
            data.append({
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
                "location_code": location_code,
            })

        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching storage locations: {e}")
        return Response({
            "detail": "Failed to fetch storage locations"
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def products_by_location(request, location_id=None):
    """
    API endpoint to list products by storage location.
    
    Path Parameters:
        location_id: ID of the storage location
        
    Returns:
        200: List of products in the location
        400: Missing location ID
        500: Server error
    """
    try:
        if not location_id:
            return Response([], status=200)

        product_storage_items = ProductStorage.objects.filter(
            storage_location_id=location_id
        ).select_related("product", "storage_location")

        box_storage_items = BoxStorage.objects.filter(
            product_storage__in=product_storage_items
        ).select_related("box_slot", "box_slot__box")

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
                "product_id": product.id,
                "product_name": product.name,
                "quantity": box_item.quantity,
                "batch_number": box_item.batch_number,
                "expiry_date": box_item.expiry_date.isoformat() if box_item.expiry_date else None
            })

        # Convert the dictionary to a list for the response
        data = [
            {
                "box_id": box_data["box_id"],
                "box_code": box_data["box_code"],
                "slots": [
                    {
                        "slot_id": slot_data["slot_id"],
                        "slot_code": slot_code,
                        "products": slot_data["products"]
                    }
                    for slot_code, slot_data in box_data["slots"].items()
                ]
            }
            for box_code, box_data in result.items()
        ]

        return Response(data)
    except Exception as e:
        logger.error(f"Error fetching products by location: {e}")
        return Response({
            "detail": "Failed to fetch products by location"
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def locations_by_product(request, product_id=None):
    """
    API endpoint to list storage locations for a specific product.
    
    Path Parameters:
        product_id: ID of the product
        
    Returns:
        200: List of locations containing the product
        400: Missing product ID
        500: Server error
    """
    try:
        if not product_id:
            return Response({
                "status": "error",
                "message": "Product ID is required",
                "code": "MISSING_PARAMETERS"
            }, status=400)

        product_storage_items = ProductStorage.objects.filter(
            product_id=product_id
        ).select_related("product", "storage_location")

        result = []
        for item in product_storage_items:
            if item.storage_location:
                location = item.storage_location
                location_code = "-".join(filter(None, [
                    location.country,
                    location.city_building,
                    location.unit,
                    location.compartment,
                    location.shelf
                ]))
                
                result.append({
                    "id": location.id,
                    "name": location.name,
                    "location_code": location_code,
                    "quantity": item.quantity,
                    "reservation_status": item.reservation_status,
                    "country": location.country,
                    "city_building": location.city_building,
                    "unit": location.unit,
                    "compartment": location.compartment,
                    "shelf": location.shelf,
                })

        return Response({
            "status": "success",
            "message": "Locations retrieved successfully",
            "data": result
        })
    except Exception as e:
        logger.error(f"Error fetching locations by product: {e}")
        return Response({
            "detail": "Failed to fetch locations by product"
        }, status=500)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bin_locations_by_order(request, order_id=None):
    """
    API endpoint to list bin locations for a specific order.
    
    Path Parameters:
        order_id: ID of the sales record (order)
        
    Returns:
        200: List of bin locations associated with the order
        404: Order not found
        500: Server error
    """
    try:
        if not order_id:
            return Response([], status=200)

        # Try to get the sales record
        try:
            sales_record = SalesRecord.objects.get(id=order_id)
        except SalesRecord.DoesNotExist:
            return Response({
                "status": "error",
                "message": f"Order with ID {order_id} not found",
                "code": "ORDER_NOT_FOUND"
            }, status=404)
            
        # Get all items in this order
        record_items = SalesRecordItem.objects.filter(sales_record=sales_record)
        
        # Get all product IDs from the order items
        product_ids = [item.product_id for item in record_items if item.product_id]
        
        # Find storage locations for these products
        product_storage_items = ProductStorage.objects.filter(
            product_id__in=product_ids
        ).select_related("storage_location")
        
        # Extract unique locations
        bin_locations = []
        seen_locations = set()
        
        for item in product_storage_items:
            if item.storage_location and item.storage_location.id not in seen_locations:
                location = item.storage_location
                seen_locations.add(location.id)
                
                # Format location code based on available fields
                location_code = "-".join(filter(None, [
                    location.country,
                    location.city_building,
                    location.unit,
                    location.compartment,
                    location.shelf
                ]))
                
                bin_locations.append({
                    "id": str(location.id),  # Convert to string to match frontend expectation
                    "binCode": location.location_code or location_code,
                    "location": location.name
                })
                
        return Response(bin_locations)
    except Exception as e:
        logger.error(f"Error fetching bin locations for order {order_id}: {e}")
        return Response({
            "detail": f"Failed to fetch bin locations for order: {str(e)}"
        }, status=500)


# New endpoints for inventory operations

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_box(request):
    """
    API endpoint to move a box to a different storage location.

    Request body:
        box_id: ID of the box to move
        target_location_id: ID of the target storage location

    Returns:
        200: Box moved successfully
        400: Invalid request parameters
        404: Box or location not found
        500: Server error
    """
    try:
        box_id = request.data.get("box_id")
        target_location_id = request.data.get("target_location_id")

        if not box_id or not target_location_id:
            return Response({
                "detail": "Box ID and target location ID are required"
            }, status=400)

        try:
            box = Box.objects.get(id=box_id)
            target_location = StorageLocation.objects.get(id=target_location_id)
        except (Box.DoesNotExist, StorageLocation.DoesNotExist) as e:
            error_response = {
                "status": "error",
                "message": "Box or target location not found",
                "code": "NOT_FOUND",
                "details": str(e),
            }
            return Response(error_response, status=404)

        try:
            updated_box = InventoryService.move_box(
                box=box,
                target_storage_location=target_location,
                user=request.user,
            )
            
            success_response = {
                "status": "success",
                "message": "Box moved successfully",
                "data": {
                    "box_id": updated_box.id,
                    "current_location": {
                        "id": target_location.id,
                        "name": target_location.name,
                    },
                    "moved_at": datetime.now().isoformat(),
                    "moved_by": request.user.username,
                },
            }
            return Response(success_response)
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": "Failed to move box",
                "code": "MOVE_FAILED",
                "details": str(e),
            }
            return Response(error_response, status=500)
            
    except Exception as e:
        error_response = {
            "status": "error",
            "message": "Internal server error",
            "code": "SERVER_ERROR",
            "details": str(e),
        }
        return Response(error_response, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_product_to_box(request):
    """
    API endpoint to add a product to a box slot.
    
    Request body:
        product_id: ID of the product to add
        box_slot_id: ID of the target box slot
        quantity: Quantity to add
        batch_number: Optional batch number
        expiry_date: Optional expiry date
        
    Returns:
        200: Product added successfully
        400: Invalid request parameters
        404: Product or box slot not found
        500: Server error
    """
    try:
        product_id = request.data.get("product_id")
        box_slot_id = request.data.get("box_slot_id")
        quantity = request.data.get("quantity")
        batch_number = request.data.get("batch_number")
        expiry_date = request.data.get("expiry_date")

        if not product_id or not box_slot_id or not quantity:
            return Response({
                "detail": "Product ID, box slot ID, and quantity are required"
            }, status=400)

        try:
            from pyerp.business_modules.products.models import VariantProduct
            product = VariantProduct.objects.get(id=product_id)
            box_slot = BoxSlot.objects.get(id=box_slot_id)
            quantity = int(quantity)
        except (VariantProduct.DoesNotExist, BoxSlot.DoesNotExist, ValueError):
            return Response({
                "status": "error",
                "message": "Product, box slot not found, or invalid quantity",
                "code": "NOT_FOUND"
            }, status=404)

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
                "status": "success",
                "message": (
                    f"Added {quantity} of product {product} to box slot {box_slot}"
                ),
                "data": {
                    "box_storage_id": box_storage.id,
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
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "code": "OPERATION_FAILED"
            }, status=400)
    except Exception as e:
        logger.error(f"Error adding product to box: {e}")
        return Response({
            "status": "error",
            "message": "Failed to add product to box",
            "code": "SERVER_ERROR",
            "details": str(e)
        }, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def move_product_between_boxes(request):
    """
    API endpoint to move products between box slots.
    
    Request body:
        source_box_storage_id: ID of the source box storage
        target_box_slot_id: ID of the target box slot
        quantity: Quantity to move
        
    Returns:
        200: Product moved successfully
        400: Invalid request parameters
        404: Source or target not found
        500: Server error
    """
    try:
        source_box_storage_id = request.data.get("source_box_storage_id")
        target_box_slot_id = request.data.get("target_box_slot_id")
        quantity = request.data.get("quantity")

        if not source_box_storage_id or not target_box_slot_id or not quantity:
            return Response({
                "detail": "Source box storage ID, target box slot ID, and quantity are required"
            }, status=400)

        try:
            source_box_storage = BoxStorage.objects.get(
                id=source_box_storage_id
            )
            target_box_slot = BoxSlot.objects.get(id=target_box_slot_id)
            quantity = int(quantity)
        except (BoxStorage.DoesNotExist, BoxSlot.DoesNotExist, ValueError):
            return Response({
                "status": "error",
                "message": (
                    "Source box storage or target box slot not found, "
                    "or invalid quantity"
                ),
                "code": "NOT_FOUND"
            }, status=404)

        try:
            source_updated, target_updated = (
                InventoryService.move_product_between_box_slots(
                    source_box_storage=source_box_storage,
                    target_box_slot=target_box_slot,
                    quantity=quantity,
                    user=request.user,
                )
            )
            
            product = target_updated.product_storage.product
            
            return Response({
                "status": "success",
                "message": (
                    f"Moved {quantity} units of product {product} "
                    "between box slots"
                ),
                "data": {
                    "product": {
                        "id": product.id,
                        "name": str(product),
                    },
                    "source_box_slot": {
                        "id": source_box_storage.box_slot.id,
                        "code": source_box_storage.box_slot.slot_code,
                        "box_code": source_box_storage.box_slot.box.code,
                        "remaining_quantity": (
                            source_updated.quantity if source_updated else 0
                        ),
                    },
                    "target_box_slot": {
                        "id": target_box_slot.id,
                        "code": target_box_slot.slot_code,
                        "box_code": target_box_slot.box.code,
                        "quantity": target_updated.quantity,
                    },
                    "quantity_moved": quantity,
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "code": "OPERATION_FAILED"
            }, status=400)
    except Exception as e:
        logger.error(f"Error moving product between boxes: {e}")
        return Response({
            "status": "error",
            "message": "Failed to move product between boxes",
            "code": "SERVER_ERROR",
            "details": str(e)
        }, status=500)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def remove_product_from_box(request):
    """
    API endpoint to remove a product from a box slot.
    
    Request body:
        box_storage_id: ID of the box storage to remove from
        quantity: Quantity to remove
        reason: Optional reason for removal
        
    Returns:
        200: Product removed successfully
        400: Invalid request parameters
        404: Box storage not found
        500: Server error
    """
    try:
        box_storage_id = request.data.get("box_storage_id")
        quantity = request.data.get("quantity")
        reason = request.data.get("reason")

        if not box_storage_id or not quantity:
            return Response({
                "detail": "Box storage ID and quantity are required"
            }, status=400)

        try:
            box_storage = BoxStorage.objects.get(id=box_storage_id)
            quantity = int(quantity)
        except (BoxStorage.DoesNotExist, ValueError):
            return Response({
                "status": "error",
                "message": "Box storage not found or invalid quantity",
                "code": "NOT_FOUND"
            }, status=404)

        try:
            updated_box_storage = (
                InventoryService.remove_product_from_box_slot(
                    box_storage=box_storage,
                    quantity=quantity,
                    reason=reason,
                    user=request.user,
                )
            )
            
            product = box_storage.product_storage.product
            box_slot = box_storage.box_slot
            
            return Response({
                "status": "success",
                "message": (
                    f"Removed {quantity} units of product {product} "
                    f"from box slot {box_slot}"
                ),
                "data": {
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
                    "remaining_quantity": (
                        updated_box_storage.quantity 
                        if updated_box_storage else 0
                    ),
                }
            })
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e),
                "code": "OPERATION_FAILED"
            }, status=400)
    except Exception as e:
        logger.error(f"Error removing product from box: {e}")
        return Response({
            "status": "error",
            "message": "Failed to remove product from box",
            "code": "SERVER_ERROR",
            "details": str(e)
        }, status=500)


# URL patterns for the inventory app
urlpatterns = [
    path("status/", placeholder_view, name="status"),
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
    path(
        "bin-locations/by-order/<int:order_id>/",
        bin_locations_by_order,
        name="bin_locations_by_order",
    ),
    path("move-box/", move_box, name="move_box"),
    path(
        "add-product-to-box/",
        add_product_to_box,
        name="add_product_to_box"
    ),
    path(
        "move-product-between-boxes/",
        move_product_between_boxes,
        name="move_product_between_boxes"
    ),
    path(
        "remove-product-from-box/",
        remove_product_from_box,
        name="remove_product_from_box"
    ),
    path("placeholder/", placeholder_view, name="placeholder"),
]
