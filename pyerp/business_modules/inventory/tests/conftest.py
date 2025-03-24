"""
Test configuration for inventory tests.
"""

import pytest
import sys
import types
from django.urls import include, path, reverse, clear_url_caches, set_urlconf
from django.http import JsonResponse
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework import status

@pytest.fixture
def api_client():
    """Return an authenticated API client."""
    client = APIClient()
    return client

@pytest.fixture
def inventory_urls():
    """Set up inventory URL patterns for testing."""
    # Import inventory URLs
    from pyerp.business_modules.inventory import urls as inventory_urls_module
    
    # Create a custom URL configuration
    module_name = 'test_urls_module'
    test_urlconf = types.ModuleType(module_name)
    test_urlconf.urlpatterns = [
        path('api/inventory/', include((inventory_urls_module.urlpatterns, 'inventory'))),
    ]
    
    # List of patches to apply
    patches = []
    
    # Helper function to create and start a patch
    def patch_view(view_name, return_value):
        patch_obj = patch(f'pyerp.business_modules.inventory.urls.{view_name}')
        mock_obj = patch_obj.start()
        mock_obj.return_value = return_value
        patches.append(patch_obj)
        return mock_obj
    
    # Mock placeholder view
    patch_view('placeholder_view', JsonResponse({
        "message": "Inventory module available but not fully implemented",
        "status": "placeholder",
    }))
    
    # Mock box_types_list view
    patch_view('box_types_list', JsonResponse([{
        "id": 1,
        "name": "Test Box Type",
        "description": "Test Description",
        "length": 10,
        "width": 10,
        "height": 10,
        "weight_capacity": 100,
        "slot_count": 4,
        "slot_naming_scheme": "numeric"
    }], safe=False))
    
    # Mock boxes_list view
    patch_view('boxes_list', JsonResponse({
        "total": 1,
        "page": 1,
        "results": [{
            "id": 1,
            "code": "BOX001",
            "barcode": "12345",
            "box_type": {
                "id": 1,
                "name": "Test Box Type"
            },
            "status": "active",
            "purpose": "storage",
            "notes": "Test notes",
            "available_slots": 4
        }]
    }))
    
    # Mock storage_locations_list view
    patch_view('storage_locations_list', JsonResponse([{
        "id": 1,
        "name": "Test Location",
        "description": "Test Description",
        "country": "US",
        "city_building": "Building 1",
        "unit": "Unit 1",
        "compartment": "Compartment 1",
        "shelf": "Shelf 1",
        "sale": False,
        "special_spot": False,
        "is_active": True,
        "product_count": 5,
        "location_code": "US-Building 1-Unit 1-Compartment 1-Shelf 1"
    }], safe=False))
    
    # Mock products_by_location view
    patch_view('products_by_location', JsonResponse([{
        "box_code": "BOX001",
        "slots": [{
            "slot_code": "SLOT1",
            "products": [{
                "sku": "SKU001",
                "name": "Test Product",
                "quantity": 5,
                "batch_number": "BATCH001",
                "date_stored": "2023-01-01"
            }]
        }]
    }], safe=False))
    
    # Mock locations_by_product view  
    patch_view('locations_by_product', JsonResponse([{
        "location_id": 1,
        "location_name": "Test Location",
        "location_code": "US-Building 1-Unit 1-Compartment 1-Shelf 1",
        "total_quantity": 10,
        "reserved_quantity": 2,
        "available_quantity": 8
    }], safe=False))
    
    # Mock move_box view
    patch_view('move_box', JsonResponse({
        "box_id": 1,
        "new_location_id": 2,
        "success": True
    }))
    
    # Mock add_product_to_box view
    patch_view('add_product_to_box', JsonResponse({
        "box_id": 1,
        "slot_id": 2,
        "product_id": 3,
        "quantity": 5,
        "success": True
    }))
    
    # Mock move_product_between_boxes view
    patch_view('move_product_between_boxes', JsonResponse({
        "source_box_id": 1,
        "source_slot_id": 2,
        "target_box_id": 3,
        "target_slot_id": 4,
        "product_id": 5,
        "quantity": 6,
        "success": True
    }))
    
    # Mock remove_product_from_box view
    patch_view('remove_product_from_box', JsonResponse({
        "box_id": 1,
        "slot_id": 2,
        "product_id": 3,
        "quantity": 4,
        "success": True
    }))
    
    # Also mock IsAuthenticated permission check
    has_permission_patch = patch('pyerp.business_modules.inventory.urls.IsAuthenticated.has_permission')
    mock_has_permission = has_permission_patch.start()
    mock_has_permission.return_value = True
    patches.append(has_permission_patch)
    
    # Register the module in sys.modules
    sys.modules[module_name] = test_urlconf
    
    # Set the URL configuration for Django to use
    old_urlconf = set_urlconf(test_urlconf)
    clear_url_caches()
    
    yield
    
    # Clean up
    for patch_obj in patches:
        patch_obj.stop()
    
    set_urlconf(old_urlconf)
    clear_url_caches()
    if module_name in sys.modules:
        del sys.modules[module_name] 