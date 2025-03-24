"""
Hypothesis integration examples for property-based testing in pyERP.

This module provides example strategies and test patterns using Hypothesis
to improve test coverage and catch edge cases through property-based testing.
"""

from hypothesis import given, strategies as st
from hypothesis.extra.django import from_model, TestCase as HypothesisTestCase
import re
from typing import List, Dict, Any, Optional, Union

# Basic strategies for different data types
def text_strategy(min_size: int = 0, max_size: int = 100) -> st.SearchStrategy[str]:
    """Generate text strings with configurable length."""
    return st.text(min_size=min_size, max_size=max_size)

def email_strategy() -> st.SearchStrategy[str]:
    """Generate valid email addresses."""
    return st.emails()

def amount_strategy(min_value: float = 0, max_value: float = 1000) -> st.SearchStrategy[float]:
    """Generate decimal amounts with 2 decimal places."""
    return st.decimals(min_value=min_value, max_value=max_value, places=2)

def date_strategy() -> st.SearchStrategy[str]:
    """Generate date strings in ISO format."""
    return st.dates().map(lambda d: d.isoformat())

def product_code_strategy() -> st.SearchStrategy[str]:
    """Generate product codes in the format ABC-123-XYZ."""
    return st.from_regex(r"[A-Z]{3}-\d{3}-[A-Z]{3}", fullmatch=True)

# Composite strategies for business objects
def product_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    """Generate valid product dictionaries."""
    return st.fixed_dictionaries({
        'code': product_code_strategy(),
        'name': st.text(min_size=5, max_size=50),
        'price': amount_strategy(),
        'stock': st.integers(min_value=0, max_value=1000),
        'category': st.sampled_from(['Electronics', 'Clothing', 'Food', 'Books']),
        'active': st.booleans(),
    })

def customer_strategy() -> st.SearchStrategy[Dict[str, Any]]:
    """Generate valid customer dictionaries."""
    return st.fixed_dictionaries({
        'name': st.text(min_size=2, max_size=50),
        'email': email_strategy(),
        'phone': st.from_regex(r"\+\d{1,3}\d{10}", fullmatch=True),
        'address': st.text(min_size=10, max_size=100),
        'active': st.booleans(),
    })

def order_strategy(include_items: bool = True) -> st.SearchStrategy[Dict[str, Any]]:
    """Generate valid order dictionaries, optionally with line items."""
    order = st.fixed_dictionaries({
        'order_number': st.from_regex(r"ORD-\d{6}", fullmatch=True),
        'customer_id': st.integers(min_value=1, max_value=10000),
        'date': date_strategy(),
        'total': amount_strategy(min_value=10, max_value=10000),
        'status': st.sampled_from(['Pending', 'Processing', 'Shipped', 'Delivered']),
    })
    
    if include_items:
        return order.flatmap(lambda o: st.fixed_dictionaries({
            **o,
            'items': st.lists(
                st.fixed_dictionaries({
                    'product_code': product_code_strategy(),
                    'quantity': st.integers(min_value=1, max_value=100),
                    'price': amount_strategy(),
                }),
                min_size=1,
                max_size=10
            ),
        }))
    
    return order

# Common property test helper functions
def assert_valid_product(product: Dict[str, Any]) -> None:
    """Assert that a product dictionary has valid properties."""
    assert re.match(r"[A-Z]{3}-\d{3}-[A-Z]{3}", product['code'])
    assert 5 <= len(product['name']) <= 50
    assert 0 <= product['price'] <= 1000
    assert 0 <= product['stock'] <= 1000
    assert product['category'] in ['Electronics', 'Clothing', 'Food', 'Books']
    assert isinstance(product['active'], bool)

def assert_valid_customer(customer: Dict[str, Any]) -> None:
    """Assert that a customer dictionary has valid properties."""
    assert 2 <= len(customer['name']) <= 50
    assert re.match(r"[^@]+@[^@]+\.[^@]+", customer['email'])
    assert re.match(r"\+\d{1,3}\d{10}", customer['phone'])
    assert 10 <= len(customer['address']) <= 100
    assert isinstance(customer['active'], bool)

# Django model strategy helpers
def django_model_strategy(model_class, **field_strategies):
    """
    Create a strategy for generating Django model instances.
    
    Args:
        model_class: The Django model class
        field_strategies: Field-specific strategies to override defaults
        
    Returns:
        A strategy that generates instances of the model
    """
    return from_model(model_class, **field_strategies) 