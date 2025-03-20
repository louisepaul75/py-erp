"""Tests for the sync transformers module."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List, Set

from pyerp.sync.transformers.base import BaseTransformer, ValidationError


class TestValidationError:
    """Tests for the ValidationError class."""

    def test_init_with_defaults(self):
        """Test initialization with default values."""
        error = ValidationError(field="name", message="Invalid name")
        
        assert error.field == "name"
        assert error.message == "Invalid name"
        assert error.error_type == "error"
        assert error.context == {}

    def test_init_with_custom_values(self):
        """Test initialization with custom values."""
        context = {"max_length": 50, "actual_length": 60}
        error = ValidationError(
            field="description",
            message="Description too long",
            error_type="warning",
            context=context
        )
        
        assert error.field == "description"
        assert error.message == "Description too long"
        assert error.error_type == "warning"
        assert error.context == context


class SimpleTransformer(BaseTransformer):
    """Simple transformer implementation for testing."""
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform source data to target format."""
        return super().transform(source_data)


class TestBaseTransformer:
    """Tests for the BaseTransformer class."""

    def test_init_with_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = {}
        transformer = SimpleTransformer(config)
        
        assert transformer.config == config
        assert transformer.field_mappings == {}
        assert transformer.custom_transformers == {}
        assert transformer.validation_rules == []

    def test_init_with_full_config(self):
        """Test initialization with full configuration."""
        field_mappings = {
            "target_field1": "source_field1",
            "target_field2": "source_field2"
        }
        validation_rules = [
            {
                "field": "target_field1",
                "validator": lambda x: isinstance(x, str),
                "error_message": "Must be a string"
            }
        ]
        config = {
            "field_mappings": field_mappings,
            "validation_rules": validation_rules,
            "extra_setting": "value"
        }
        
        transformer = SimpleTransformer(config)
        
        assert transformer.config == config
        assert transformer.field_mappings == field_mappings
        assert transformer.validation_rules == validation_rules

    def test_validate_config_valid(self):
        """Test configuration validation with valid config."""
        config = {
            "field_mappings": {"target": "source"},
            "validation_rules": []
        }
        
        # This should not raise an exception
        transformer = SimpleTransformer(config)
        assert transformer.field_mappings == {"target": "source"}

    def test_validate_config_invalid_mappings(self):
        """Test configuration validation with invalid field mappings."""
        config = {
            "field_mappings": "not a dict",
            "validation_rules": []
        }
        
        with pytest.raises(ValueError) as exc_info:
            SimpleTransformer(config)
        
        assert "field_mappings must be a dictionary" in str(exc_info.value)

    def test_validate_config_invalid_rules(self):
        """Test configuration validation with invalid validation rules."""
        config = {
            "field_mappings": {},
            "validation_rules": "not a list"
        }
        
        with pytest.raises(ValueError) as exc_info:
            SimpleTransformer(config)
        
        assert "validation_rules must be a list" in str(exc_info.value)

    def test_register_custom_transformer(self):
        """Test registering a custom transformer function."""
        transformer = SimpleTransformer({})
        
        # Register a simple custom transformer
        def custom_func(value, _):
            return value.upper() if isinstance(value, str) else value
        
        transformer.register_custom_transformer("name", custom_func)
        
        assert "name" in transformer.custom_transformers
        assert transformer.custom_transformers["name"] == custom_func

    def test_apply_field_mappings(self):
        """Test applying field mappings to a source record."""
        field_mappings = {
            "target_name": "name",
            "target_price": "price",
            "target_code": "product_code"
        }
        transformer = SimpleTransformer({"field_mappings": field_mappings})
        
        source_record = {
            "name": "Test Product",
            "price": 10.99,
            "product_code": "TP001",
            "other_field": "Other value"  # This should not be mapped
        }
        
        result = transformer.apply_field_mappings(source_record)
        
        assert result == {
            "target_name": "Test Product",
            "target_price": 10.99,
            "target_code": "TP001"
        }
        
        # Test with a source field that doesn't exist
        source_record_missing = {
            "name": "Test Product",
            "other_field": "Other value"
        }
        
        result_missing = transformer.apply_field_mappings(source_record_missing)
        
        assert result_missing == {
            "target_name": "Test Product"
        }

    def test_apply_custom_transformers(self):
        """Test applying custom transformers to a record."""
        transformer = SimpleTransformer({})
        
        # Register custom transformers
        def uppercase_name(value, source_record=None):
            return value.upper() if isinstance(value, str) else value
        
        def double_price(value, source_record=None):
            return value * 2 if isinstance(value, (int, float)) else value
        
        transformer.register_custom_transformer("name", uppercase_name)
        transformer.register_custom_transformer("price", double_price)
        
        record = {
            "name": "Test Product",
            "price": 10.99,
            "code": "TP001"
        }
        source_record = {}  # Not used in our test transformers
        
        result = transformer.apply_custom_transformers(record, source_record)
        
        assert result["name"] == "TEST PRODUCT"
        assert result["price"] == 21.98
        assert result["code"] == "TP001"  # Unchanged, no transformer

    @patch('pyerp.sync.transformers.base.logger')
    def test_apply_custom_transformers_error(self, mock_logger):
        """Test handling errors in custom transformers."""
        transformer = SimpleTransformer({})
        
        # Register custom transformer that raises exception
        def failing_transformer(value, source_record=None):
            raise ValueError("Test error")
            
        transformer.register_custom_transformer("name", failing_transformer)
        
        record = {"name": "Test Product"}
        source_record = {}
        
        # This should not raise an exception
        result = transformer.apply_custom_transformers(record, source_record)
        
        # The value should remain unchanged
        assert result["name"] == "Test Product"
        
        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error applying custom transformer" in mock_logger.error.call_args[0][0]

    def test_validate_record(self):
        """Test record validation."""
        validation_rules = [
            {
                "field": "name",
                "validator": lambda x: isinstance(x, str) and len(x) <= 10,
                "error_message": "Name must be a string <= 10 characters"
            },
            {
                "field": "price",
                "validator": lambda x: isinstance(x, (int, float)) and x > 0,
                "error_message": "Price must be a positive number"
            }
        ]
        
        transformer = SimpleTransformer({"validation_rules": validation_rules})
        
        # Test valid record
        valid_record = {"name": "Test", "price": 10.99}
        valid_errors = transformer.validate_record(valid_record)
        assert len(valid_errors) == 0
        
        # Test invalid name
        invalid_name = {"name": "Test Product with Long Name", "price": 10.99}
        name_errors = transformer.validate_record(invalid_name)
        assert len(name_errors) == 1
        assert name_errors[0].field == "name"
        assert "Name must be a string <= 10 characters" in name_errors[0].message
        
        # Test invalid price
        invalid_price = {"name": "Test", "price": -5}
        price_errors = transformer.validate_record(invalid_price)
        assert len(price_errors) == 1
        assert price_errors[0].field == "price"
        assert "Price must be a positive number" in price_errors[0].message
        
        # Test multiple errors
        invalid_record = {"name": "Test Product with Long Name", "price": -5}
        all_errors = transformer.validate_record(invalid_record)
        assert len(all_errors) == 2

    def test_prefilter_records(self):
        """Test prefiltering records based on existing keys."""
        field_mappings = {"target_sku": "sku"}
        transformer = SimpleTransformer({"field_mappings": field_mappings})
        
        source_data = [
            {"sku": "TP001", "name": "Existing Product 1"},
            {"sku": "TP002", "name": "Existing Product 2"},
            {"sku": "TP003", "name": "New Product 1"},
            {"sku": "TP004", "name": "New Product 2"},
            {"name": "No SKU Product"}  # No SKU field
        ]
        
        existing_keys = {"TP001", "TP002"}
        
        new_records, existing_records = transformer.prefilter_records(
            source_data, existing_keys, "target_sku"
        )
        
        assert len(new_records) == 3
        assert len(existing_records) == 2
        
        # Verify new records
        new_skus = {r.get("sku") for r in new_records}
        assert new_skus == {"TP003", "TP004", None}
        
        # Verify existing records
        existing_skus = {r.get("sku") for r in existing_records}
        assert existing_skus == {"TP001", "TP002"}

    def test_prefilter_records_normalization(self):
        """Test key normalization in prefiltering."""
        field_mappings = {"target_sku": "sku"}
        transformer = SimpleTransformer({"field_mappings": field_mappings})
        
        source_data = [
            {"sku": "tp001", "name": "Lowercase SKU"},  # Lowercase
            {"sku": "TP002 ", "name": "Extra Whitespace"},  # Extra whitespace
            {"sku": "TP003", "name": "Normal SKU"}
        ]
        
        # Existing keys with different case and whitespace
        existing_keys = {"TP001", " tp002"}
        
        new_records, existing_records = transformer.prefilter_records(
            source_data, existing_keys, "target_sku"
        )
        
        assert len(new_records) == 1
        assert len(existing_records) == 2
        
        # Verify normalization worked
        new_skus = {r.get("sku") for r in new_records}
        assert new_skus == {"TP003"}
        
        existing_skus = {r.get("sku") for r in existing_records}
        assert existing_skus == {"tp001", "TP002 "}

    def test_prefilter_records_missing_key_field(self):
        """Test prefiltering with missing key field."""
        transformer = SimpleTransformer({})
        
        source_data = [
            {"id": 1, "name": "Product 1"},
            {"id": 2, "name": "Product 2"}
        ]
        
        existing_keys = {1, 2}
        
        # No key_field provided
        new_records, existing_records = transformer.prefilter_records(
            source_data, existing_keys
        )
        
        # All records should be treated as new
        assert len(new_records) == 2
        assert len(existing_records) == 0

    def test_transform(self):
        """Test the transform method."""
        transformer = SimpleTransformer({
            "field_mappings": {
                "legacy_id": "id",
                "product_name": "name",
                "price": "price",
            }
        })
        
        # Register a custom transformer
        def uppercase_name(value, source_record=None):
            return value.upper() if isinstance(value, str) else value
        
        transformer.register_custom_transformer("product_name", uppercase_name)
        
        source_data = [
            {"name": "Product 1", "price": 10.99, "sku": "P1", "other_field": "value1"},
            {"name": "Product 2", "price": 20.99, "sku": "P2", "other_field": "value2"}
        ]
        
        result = transformer.transform(source_data)
        
        assert len(result) == 2
        
        # Verify first record
        assert result[0]["product_name"] == "PRODUCT 1"
        assert result[0]["product_price"] == 10.99
        assert result[0]["product_code"] == "P1"
        assert "other_field" not in result[0]
        
        # Verify second record
        assert result[1]["product_name"] == "PRODUCT 2"
        assert result[1]["product_price"] == 20.99
        assert result[1]["product_code"] == "P2"
        assert "other_field" not in result[1]

    def test_validate(self):
        """Test the validate method."""
        validation_rules = [
            {
                "field": "name",
                "validator": lambda x: isinstance(x, str) and len(x) <= 10,
                "error_message": "Name must be a string <= 10 characters"
            },
            {
                "field": "price",
                "validator": lambda x: isinstance(x, (int, float)) and x > 0,
                "error_message": "Price must be a positive number"
            }
        ]
        
        transformer = SimpleTransformer({"validation_rules": validation_rules})
        
        transformed_data = [
            {"name": "Valid", "price": 10.99},  # Valid
            {"name": "Too Long Name for Validation", "price": 20.99},  # Invalid name
            {"name": "Valid", "price": -5}  # Invalid price
        ]
        
        validation_results = transformer.validate(transformed_data)
        
        assert len(validation_results) == 2  # 2 records with errors
        
        # Verify first error result
        assert validation_results[0]["record"] == transformed_data[1]  # Second record
        assert len(validation_results[0]["errors"]) == 1
        assert validation_results[0]["errors"][0].field == "name"
        
        # Verify second error result
        assert validation_results[1]["record"] == transformed_data[2]  # Third record
        assert len(validation_results[1]["errors"]) == 1
        assert validation_results[1]["errors"][0].field == "price" 