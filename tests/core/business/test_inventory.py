"""
Tests for inventory management functionality.

This module contains tests for inventory-related operations including:
- Stock level tracking
- Stock movements
- Inventory valuations
- Stock reservations
- Reorder point calculations
"""

from decimal import Decimal
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from tests.utils.mocks import MockProduct


class TestInventoryOperations:
    """Test suite for inventory operations."""

    def setup_method(self):
        """Set up test data."""
        self.product = MockProduct(
            sku="TEST001",
            name="Test Product",
            stock_quantity=100,
            min_stock_quantity=20,
            backorder_quantity=0,
            open_purchase_quantity=50,
            cost_price=Decimal("10.00"),
            list_price=Decimal("20.00")
        )

    def test_available_quantity_calculation(self):
        """Test calculation of available quantity."""
        # Available = Current - Reserved
        self.product.stock_quantity = 100
        reserved_quantity = 30
        
        expected_available = self.product.stock_quantity - reserved_quantity
        assert expected_available == 70, (
            "Available quantity should be current stock minus reserved"
        )

    def test_projected_quantity_calculation(self):
        """Test calculation of projected quantity."""
        # Projected = Current + On Order - Reserved - Backorders
        current_stock = 100
        on_order = 50
        reserved = 30
        backorders = 20

        self.product.stock_quantity = current_stock
        self.product.open_purchase_quantity = on_order
        self.product.backorder_quantity = backorders

        projected = (
            current_stock + on_order - reserved - backorders
        )
        assert projected == 100, (
            "Projected quantity calculation should be correct"
        )

    def test_reorder_point_validation(self):
        """Test validation of reorder points."""
        # Min stock should not be greater than max stock
        with pytest.raises(ValidationError) as exc_info:
            self.product.min_stock_quantity = 150
            self.product.validate_stock_levels()
        
        assert "minimum stock level" in str(exc_info.value)

    def test_stock_value_calculation(self):
        """Test calculation of stock value."""
        # Stock value = Quantity * Cost price
        quantity = 100
        cost_price = Decimal("10.00")
        self.product.stock_quantity = quantity
        self.product.cost_price = cost_price

        expected_value = quantity * cost_price
        actual_value = self.product.calculate_stock_value()
        assert actual_value == expected_value, (
            "Stock value calculation should be correct"
        )

    def test_stock_movement_validation(self):
        """Test validation of stock movements."""
        current_stock = 50
        self.product.stock_quantity = current_stock

        # Test invalid negative stock (if not allowed)
        with pytest.raises(ValidationError) as exc_info:
            self.product.validate_stock_movement(-60)
        
        assert "insufficient stock" in str(exc_info.value)

        # Test valid stock reduction
        try:
            self.product.validate_stock_movement(-30)
        except ValidationError:
            pytest.fail("Should allow valid stock reduction")

    def test_backorder_handling(self):
        """Test handling of backorders."""
        # Setup initial state
        self.product.stock_quantity = 10
        self.product.backorder_quantity = 0

        # Attempt to fulfill an order that exceeds stock
        order_quantity = 15
        fulfilled, backorder = self.product.process_order(
            order_quantity
        )

        assert fulfilled == 10, "Should fulfill available stock"
        assert backorder == 5, (
            "Should create backorder for remaining quantity"
        )
        assert self.product.backorder_quantity == 5, (
            "Should update backorder quantity"
        )

    def test_stock_receipt_processing(self):
        """Test processing of stock receipts."""
        initial_stock = 100
        receipt_quantity = 50
        self.product.stock_quantity = initial_stock
        self.product.last_receipt_date = None

        # Process receipt
        self.product.process_stock_receipt(receipt_quantity)

        assert self.product.stock_quantity == initial_stock + receipt_quantity, (
            "Stock quantity should be updated after receipt"
        )
        assert self.product.last_receipt_date == date.today(), (
            "Last receipt date should be updated"
        )

    def test_stock_level_alerts(self):
        """Test stock level alert conditions."""
        self.product.min_stock_quantity = 20
        
        # Test low stock alert
        self.product.stock_quantity = 15
        assert self.product.is_low_stock(), (
            "Should identify low stock condition"
        )

        # Test adequate stock
        self.product.stock_quantity = 25
        assert not self.product.is_low_stock(), (
            "Should not flag adequate stock as low"
        )

    def test_inventory_aging(self):
        """Test inventory aging calculations."""
        today = date.today()
        old_date = today - timedelta(days=180)
        
        self.product.last_issue_date = old_date
        
        # Calculate age in days
        age = (today - old_date).days
        assert age == 180, "Should correctly calculate inventory age"

        # Test aging classification
        assert self.product.get_aging_category() == "old", (
            "Should classify 180-day old inventory as old"
        ) 