"""
Tests for the BaseTransformer class.
"""
import pytest
from typing import Any, Dict, List

from pyerp.sync.transformers.base import BaseTransformer, ValidationError
from pyerp.sync.exceptions import TransformError


class MockTransformer(BaseTransformer):
    """Mock implementation of the abstract BaseTransformer for testing."""
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Implement the abstract method."""
        result = []
        for item in source_data:
            # Apply field mappings
            record = self.apply_field_mappings(item)
            
            # Apply custom transformers
            record = self.apply_custom_transformers(record, item)
            
            result.append(record)
        
        return result


@pytest.fixture
def basic_config():
    """Return a basic configuration for transformer testing."""
    return {
        "field_mappings": {
            "id": "legacy_id",
            "name": "product_name",
            "price": "product_price",
        },
        "validation_rules": [
            {
                "field": "price",
                "check": "greater_than",
                "value": 0,
                "message": "Price must be greater than zero"
            }
        ]
    }


class TestValidationError:
    """Tests for the ValidationError class."""
    
    def test_init_with_defaults(self):
        """Test ValidationError initialization with default values."""
        error = ValidationError("price", "Price must be positive")
        
        assert error.field == "price"
        assert error.message == "Price must be positive"
        assert error.error_type == "error"
        assert error.context == {}
    
    def test_init_with_custom_values(self):
        """Test ValidationError initialization with custom values."""
        context = {"original_value": -10}
        error = ValidationError("price", "Price must be positive", "warning", context)
        
        assert error.field == "price"
        assert error.message == "Price must be positive"
        assert error.error_type == "warning"
        assert error.context == context


class TestBaseTransformer:
    """Tests for the BaseTransformer class."""
    
    def test_init_with_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = {}
        transformer = MockTransformer(config)
        
        assert transformer.config == {}
        assert transformer.field_mappings == {}
        assert transformer.validation_rules == []
        assert transformer.custom_transformers == {}
    
    def test_init_with_full_config(self, basic_config):
        """Test initialization with full configuration."""
        transformer = MockTransformer(basic_config)
        
        assert transformer.config == basic_config
        assert transformer.field_mappings == basic_config["field_mappings"]
        assert transformer.validation_rules == basic_config["validation_rules"]
    
    def test_validate_config_valid(self, basic_config):
        """Test configuration validation with valid config."""
        transformer = MockTransformer(basic_config)
        # If invalid, an exception would be raised during initialization
        
        # Let's manually call it again to ensure it works
        transformer._validate_config()
        
        # No exception means test passes
    
    def test_validate_config_invalid_mappings(self):
        """Test configuration validation with invalid mappings."""
        config = {
            "field_mappings": "not a dictionary"
        }
        
        with pytest.raises(TransformError) as exc_info:
            MockTransformer(config)
        
        assert "field_mappings must be a dictionary" in str(exc_info.value)
    
    def test_validate_config_invalid_rules(self):
        """Test configuration validation with invalid rules."""
        config = {
            "validation_rules": "not a list"
        }
        
        with pytest.raises(TransformError) as exc_info:
            MockTransformer(config)
        
        assert "validation_rules must be a list" in str(exc_info.value)
    
    def test_register_custom_transformer(self, basic_config):
        """Test registering a custom transformer function."""
        transformer = MockTransformer(basic_config)
        
        def convert_to_float(value):
            return float(value)
        
        transformer.register_custom_transformer("price", convert_to_float)
        
        assert "price" in transformer.custom_transformers
        assert transformer.custom_transformers["price"] == convert_to_float
    
    def test_apply_field_mappings(self, basic_config):
        """Test applying field mappings to source data."""
        transformer = MockTransformer(basic_config)
        
        source_record = {
            "legacy_id": 123,
            "product_name": "Test Product",
            "product_price": "99.99",
            "other_field": "value"
        }
        
        result = transformer.apply_field_mappings(source_record)
        
        assert result["id"] == 123
        assert result["name"] == "Test Product"
        assert result["price"] == "99.99"
        assert "other_field" in result  # Unmapped fields should be preserved
        assert result["other_field"] == "value"
    
    def test_apply_custom_transformers(self, basic_config):
        """Test applying custom transformers to mapped data."""
        transformer = MockTransformer(basic_config)
        
        def convert_to_float(value):
            return float(value)
        
        transformer.register_custom_transformer("price", convert_to_float)
        
        record = {
            "id": 123,
            "name": "Test Product",
            "price": "99.99"
        }
        
        source_record = {
            "legacy_id": 123,
            "product_name": "Test Product",
            "product_price": "99.99"
        }
        
        result = transformer.apply_custom_transformers(record, source_record)
        
        assert result["price"] == 99.99  # Now a float
        assert result["id"] == 123  # Unchanged
        assert result["name"] == "Test Product"  # Unchanged
    
    def test_apply_custom_transformers_error(self, basic_config):
        """Test error handling in custom transformers."""
        transformer = MockTransformer(basic_config)
        
        def raise_error(value):
            raise ValueError("Test error")
        
        transformer.register_custom_transformer("price", raise_error)
        
        record = {"price": "99.99"}
        source_record = {"product_price": "99.99"}
        
        with pytest.raises(TransformError) as exc_info:
            transformer.apply_custom_transformers(record, source_record)
        
        assert "Error applying custom transformer for field 'price'" in str(exc_info.value)
    
    def test_validate_record(self, basic_config):
        """Test record validation with validation rules."""
        transformer = MockTransformer(basic_config)
        
        # Valid record
        valid_record = {"price": 10.0}
        valid_errors = transformer.validate_record(valid_record)
        assert len(valid_errors) == 0
        
        # Invalid record
        invalid_record = {"price": -5.0}
        invalid_errors = transformer.validate_record(invalid_record)
        assert len(invalid_errors) == 1
        assert invalid_errors[0].field == "price"
        assert "Price must be greater than zero" in invalid_errors[0].message
    
    def test_prefilter_records(self, basic_config):
        """Test prefiltering records based on key field."""
        transformer = MockTransformer(basic_config)
        
        source_data = [
            {"legacy_id": 1, "product_name": "Product 1"},
            {"legacy_id": 2, "product_name": "Product 2"},
            {"legacy_id": 3, "product_name": "Product 3"}
        ]
        
        existing_keys = {1, 3}  # Records with legacy_id 1 and 3 already exist
        
        to_update, to_create = transformer.prefilter_records(
            source_data,
            existing_keys=existing_keys,
            key_field="legacy_id"
        )
        
        assert len(to_update) == 2
        assert len(to_create) == 1
        assert to_create[0]["legacy_id"] == 2
        assert to_update[0]["legacy_id"] == 1
        assert to_update[1]["legacy_id"] == 3
    
    def test_prefilter_records_normalization(self, basic_config):
        """Test normalization of key values in prefiltering."""
        transformer = MockTransformer(basic_config)
        
        source_data = [
            {"legacy_id": "1", "product_name": "Product 1"},  # String key
            {"legacy_id": 2, "product_name": "Product 2"},   # Integer key
        ]
        
        existing_keys = {1}  # Integer format
        
        to_update, to_create = transformer.prefilter_records(
            source_data,
            existing_keys=existing_keys,
            key_field="legacy_id"
        )
        
        assert len(to_update) == 1
        assert len(to_create) == 1
        assert to_update[0]["legacy_id"] == "1"  # Original format preserved
        assert to_create[0]["legacy_id"] == 2
    
    def test_prefilter_records_missing_key_field(self, basic_config):
        """Test prefiltering when a record is missing the key field."""
        transformer = MockTransformer(basic_config)
        
        source_data = [
            {"legacy_id": 1, "product_name": "Product 1"},
            {"product_name": "Missing Key"},  # Missing legacy_id
            {"legacy_id": 3, "product_name": "Product 3"}
        ]
        
        existing_keys = {1}
        
        to_update, to_create = transformer.prefilter_records(
            source_data,
            existing_keys=existing_keys,
            key_field="legacy_id"
        )
        
        # Should skip the record with missing key field
        assert len(to_update) == 1
        assert len(to_create) == 1
        assert to_update[0]["legacy_id"] == 1
        assert to_create[0]["legacy_id"] == 3
    
    def test_transform(self, basic_config):
        """Test the transform method implementation."""
        transformer = MockTransformer(basic_config)
        
        source_data = [
            {
                "legacy_id": 1,
                "product_name": "Product 1",
                "product_price": "10.99"
            },
            {
                "legacy_id": 2,
                "product_name": "Product 2",
                "product_price": "20.99"
            }
        ]
        
        result = transformer.transform(source_data)
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Product 1"
        assert result[0]["price"] == "10.99"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Product 2"
        assert result[1]["price"] == "20.99"
    
    def test_validate(self, basic_config):
        """Test the validate method."""
        transformer = MockTransformer(basic_config)
        
        # Register a custom transformer to convert price to float
        def convert_to_float(value):
            return float(value)
        
        transformer.register_custom_transformer("price", convert_to_float)
        
        transformed_data = [
            {"id": 1, "name": "Product 1", "price": "10.99"},
            {"id": 2, "name": "Product 2", "price": "-5.99"}  # Invalid price
        ]
        
        # Transform first to apply custom transformers
        source_data = [
            {"legacy_id": 1, "product_name": "Product 1", "product_price": "10.99"},
            {"legacy_id": 2, "product_name": "Product 2", "product_price": "-5.99"}
        ]
        transformed_data = transformer.transform(source_data)
        
        # Then validate
        valid_records = transformer.validate(transformed_data)
        
        # Only one record should be valid
        assert len(valid_records) == 1
        assert valid_records[0]["id"] == 1
        assert valid_records[0]["price"] == 10.99 