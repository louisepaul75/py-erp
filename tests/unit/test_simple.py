"""
A simple test module with basic tests that should pass with minimal dependencies.
This is useful for verifying that the testing infrastructure is working properly.
"""
import pytest


def test_simple_addition():
    """Test a simple addition to verify pytest is working."""
    assert 1 + 1 == 2


def test_simple_string():
    """Test simple string operations."""
    assert "hello" + " world" == "hello world"


class TestSimpleClass:
    """A simple test class to verify class-based tests work."""
    
    def test_simple_subtraction(self):
        """Test a simple subtraction."""
        assert 5 - 3 == 2
    
    def test_simple_multiplication(self):
        """Test a simple multiplication."""
        assert 2 * 3 == 6 