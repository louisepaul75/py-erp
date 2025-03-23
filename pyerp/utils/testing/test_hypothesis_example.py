"""
Example tests demonstrating the use of Hypothesis for property-based testing.

This module shows how to implement Hypothesis in pytest to test properties
and invariants of functions rather than just specific examples.
"""

import pytest
from hypothesis import given, strategies as st, settings, example
from decimal import Decimal
from .hypothesis_examples import (
    product_strategy,
    customer_strategy,
    product_code_strategy,
    amount_strategy,
    date_strategy,
    assert_valid_product,
    assert_valid_customer,
)


# Example 1: Testing a simple function
def calculate_discount(price, quantity):
    """Calculate discount based on quantity purchased."""
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    
    discount_rate = Decimal('0.0')
    if quantity >= 10:
        discount_rate = Decimal('0.05')
    if quantity >= 50:
        discount_rate = Decimal('0.1')
    if quantity >= 100:
        discount_rate = Decimal('0.15')
    
    # Convert to Decimal if it's not already
    if not isinstance(price, Decimal):
        price = Decimal(str(price))
    
    return price * quantity * discount_rate


@given(
    price=st.decimals(min_value=0.01, max_value=1000, places=2),
    quantity=st.integers(min_value=0, max_value=1000)
)
def test_calculate_discount_properties(price, quantity):
    """Test general properties of the discount calculation function."""
    discount = calculate_discount(price, quantity)
    
    # Property 1: Discount is never negative
    assert discount >= 0
    
    # Property 2: Discount is always less than or equal to the total price
    assert discount <= price * quantity
    
    # Property 3: Higher quantities should never result in lower absolute discounts
    if quantity > 0:
        discount_for_one_less = calculate_discount(price, quantity - 1)
        # The discount per item might increase with quantity thresholds
        if quantity - 1 > 0:  # Avoid division by zero
            assert discount / quantity >= discount_for_one_less / (quantity - 1)


@given(
    price=st.decimals(min_value=0.01, max_value=1000, places=2)
)
@example(price=Decimal('10.0'))  # Explicitly test specific examples alongside properties
def test_discount_thresholds(price):
    """Test that discount thresholds behave as expected."""
    # No discount for 9 items
    assert calculate_discount(price, 9) == 0
    
    # 5% discount for 10 items
    assert calculate_discount(price, 10) == price * 10 * Decimal('0.05')
    
    # 10% discount for 50 items
    assert calculate_discount(price, 50) == price * 50 * Decimal('0.1')
    
    # 15% discount for 100 items
    assert calculate_discount(price, 100) == price * 100 * Decimal('0.15')


# Example 2: Testing with complex business objects
def process_order(order):
    """Process an order and calculate totals."""
    if 'items' not in order:
        raise ValueError("Order must have line items")
    
    total = Decimal('0')
    for item in order['items']:
        # Ensure we have Decimal calculations
        quantity = item['quantity']
        price = item['price'] if isinstance(item['price'], Decimal) else Decimal(str(item['price']))
        item_total = quantity * price
        total += item_total
    
    # Apply any order-level discounts based on total
    if total >= 1000:
        total *= Decimal('0.95')  # 5% discount
    
    # Update order total and return
    order['calculated_total'] = total
    return order


# Create a simple order strategy manually for the test
def simple_order_strategy():
    """Create a simple order strategy for testing."""
    return st.fixed_dictionaries({
        'order_number': st.from_regex(r"ORD-\d{6}", fullmatch=True),
        'customer_id': st.integers(min_value=1, max_value=10000),
        'date': date_strategy(),
        'total': amount_strategy(min_value=10, max_value=10000),
        'status': st.sampled_from(['Pending', 'Processing', 'Shipped', 'Delivered']),
        'items': st.lists(
            st.fixed_dictionaries({
                'product_code': product_code_strategy(),
                'quantity': st.integers(min_value=1, max_value=100),
                'price': amount_strategy(),
            }),
            min_size=1,
            max_size=10
        ),
    })


@given(order=simple_order_strategy())
def test_process_order_properties(order):
    """Test properties of the order processing function."""
    processed_order = process_order(order)
    
    # Skip orders with zero total
    expected_total = sum(item['quantity'] * item['price'] for item in order['items'])
    if expected_total == 0:
        pytest.skip("Skipping orders with zero total")
    
    # Property 1: Calculated total is always positive
    assert processed_order['calculated_total'] > 0
    
    # Property 2: If order total exceeds 1000, discount is applied
    if expected_total >= 1000:
        assert pytest.approx(float(processed_order['calculated_total'])) == float(expected_total) * 0.95
    else:
        assert pytest.approx(float(processed_order['calculated_total'])) == float(expected_total)


# Example 3: Using Hypothesis as a data generator
@given(product=product_strategy())
@settings(max_examples=100)  # Increase the number of examples for better coverage
def test_product_validation(product):
    """Ensure that products generated by our strategies are valid."""
    # This would normally call your validation function
    assert_valid_product(product)
    
    # Example validation logic
    assert len(product['name']) >= 5, "Product name is too short"
    assert product['price'] >= 0, "Price cannot be negative"
    assert product['stock'] >= 0, "Stock cannot be negative"


@given(customer=customer_strategy())
def test_customer_validation(customer):
    """Ensure that customers generated by our strategies are valid."""
    assert_valid_customer(customer)


# Example 4: Testing failure conditions
@given(
    price=st.decimals(min_value=0.01, max_value=1000, places=2),
    quantity=st.integers(max_value=-1)  # Always negative
)
def test_calculate_discount_with_negative_quantity(price, quantity):
    """Test that negative quantities raise appropriate errors."""
    with pytest.raises(ValueError) as excinfo:
        calculate_discount(price, quantity)
    
    assert "Quantity cannot be negative" in str(excinfo.value) 