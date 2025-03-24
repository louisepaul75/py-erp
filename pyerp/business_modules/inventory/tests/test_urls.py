"""
Tests for the inventory module URL configuration.
"""

import pytest
from unittest.mock import patch, MagicMock

from pyerp.business_modules.inventory.urls import urlpatterns


class TestInventoryURLs:
    """Test class for inventory URL patterns."""

    def test_urlpatterns_exist(self):
        """Test that urlpatterns are defined and not empty."""
        assert urlpatterns
        assert len(urlpatterns) > 0

    def test_app_name(self):
        """Test that app_name is defined correctly."""
        from pyerp.business_modules.inventory.urls import app_name
        assert app_name == "inventory"

    def test_url_names(self):
        """Test that all expected URL names exist in the urlpatterns."""
        url_names = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'name'):
                url_names.append(pattern.name)
        
        expected_names = [
            'status',
            'placeholder',
            'box_types_list',
            'boxes_list',
            'storage_locations_list',
            'products_by_location',
            'locations_by_product',
            'move_box',
            'add_product_to_box',
            'move_product_between_boxes',
            'remove_product_from_box'
        ]
        
        for name in expected_names:
            assert name in url_names, f"URL name '{name}' not found in urlpatterns"


@pytest.mark.django_db
class TestInventoryViewFunctions:
    """Test class for inventory view functions."""

    def test_placeholder_view_registered(self):
        """Test that the placeholder view is registered with the correct URL pattern."""
        # Find placeholder view in urlpatterns
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'placeholder':
                found = True
                break
        assert found, "Could not find 'placeholder' URL pattern"
        
    def test_box_types_list_registered(self):
        """Test that the box_types_list view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'box_types_list':
                found = True
                break
        assert found, "Could not find 'box_types_list' URL pattern"
        
    def test_boxes_list_registered(self):
        """Test that the boxes_list view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'boxes_list':
                found = True
                break
        assert found, "Could not find 'boxes_list' URL pattern"
        
    def test_storage_locations_list_registered(self):
        """Test that the storage_locations_list view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'storage_locations_list':
                found = True
                break
        assert found, "Could not find 'storage_locations_list' URL pattern"
        
    def test_products_by_location_registered(self):
        """Test that the products_by_location view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'products_by_location':
                found = True
                break
        assert found, "Could not find 'products_by_location' URL pattern"
        
    def test_locations_by_product_registered(self):
        """Test that the locations_by_product view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'locations_by_product':
                found = True
                break
        assert found, "Could not find 'locations_by_product' URL pattern"
        
    def test_move_box_registered(self):
        """Test that the move_box view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'move_box':
                found = True
                break
        assert found, "Could not find 'move_box' URL pattern"
        
    def test_add_product_to_box_registered(self):
        """Test that the add_product_to_box view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'add_product_to_box':
                found = True
                break
        assert found, "Could not find 'add_product_to_box' URL pattern"
        
    def test_move_product_between_boxes_registered(self):
        """Test that the move_product_between_boxes view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'move_product_between_boxes':
                found = True
                break
        assert found, "Could not find 'move_product_between_boxes' URL pattern"
        
    def test_remove_product_from_box_registered(self):
        """Test that the remove_product_from_box view is registered with the correct URL pattern."""
        found = False
        for pattern in urlpatterns:
            if hasattr(pattern, 'name') and pattern.name == 'remove_product_from_box':
                found = True
                break
        assert found, "Could not find 'remove_product_from_box' URL pattern" 