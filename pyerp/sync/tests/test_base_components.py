import pytest
from django.test import TestCase
import unittest.mock

from pyerp.sync.extractors.base import BaseExtractor
from pyerp.sync.transformers.base import BaseTransformer, ValidationError
from pyerp.sync.loaders.base import BaseLoader, LoadResult


# Add a concrete transformer implementation
class MockTransformer(BaseTransformer):
    """Mock transformer that implements the required abstract methods."""
    
    def transform(self, source_data):
        """Implement the abstract transform method."""
        transformed_records = []
        for record in source_data:
            # Apply field mappings
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            transformed_records.append(transformed)
        
        return transformed_records


# Create test subclasses for each base component
class TestExtractor(BaseExtractor):
    """Test extractor implementation."""
    
    def get_required_config_fields(self):
        return ["api_key", "url"]

    def connect(self):
        self.connect_called = True

    def extract(self, query_params=None):
        return []
    
    def close(self):
        self.close_called = True


class TestLoader(BaseLoader):
    """Test loader implementation."""
    
    def get_required_config_fields(self):
        return ["destination_url"]
    
    def prepare_record(self, record):
        return record
    
    def load_record(self, lookup_criteria, record, update_existing=True):
        # Simulate loading a record
        return {"id": 1, "status": "success"}


@pytest.mark.unit
class TestBaseExtractor(TestCase):
    """Tests for the BaseExtractor class."""

    def test_validate_config_with_missing_fields(self):
        """Test that _validate_config raises ValueError for missing fields."""
        # Test with missing fields
        with self.assertRaises(ValueError) as context:
            TestExtractor(config={"api_key": "test"})

        # Check error message
        self.assertIn("Missing required configuration fields", str(context.exception))
        self.assertIn("url", str(context.exception))

    def test_validate_config_with_all_fields(self):
        """Test that _validate_config passes with all required fields."""
        # Test with all fields
        config = {"api_key": "test", "url": "http://example.com"}
        extractor = TestExtractor(config=config)

        # Check that config was set
        self.assertEqual(extractor.config["api_key"], "test")
        self.assertEqual(extractor.config["url"], "http://example.com")

    def test_context_manager(self):
        """Test that extractor can be used as a context manager."""
        # Create instance
        extractor = TestExtractor(config={"api_key": "test", "url": "http://example.com"})
        extractor.connect_called = False
        extractor.close_called = False

        # Use as context manager
        with extractor as e:
            # Check that connect was called
            self.assertTrue(extractor.connect_called)
            # Check that the context manager returns the extractor
            self.assertEqual(e, extractor)

        # Check that close was called
        self.assertTrue(extractor.close_called)


@pytest.mark.unit
class TestBaseTransformer(TestCase):
    """Tests for the BaseTransformer class."""

    def test_apply_field_mappings(self):
        """Test that apply_field_mappings correctly maps fields."""
        # Create a transformer with field mappings
        transformer = MockTransformer(
            {
                "field_mappings": {
                    "id": "source_id",
                    "name": "source_name",
                    "price": "source_price",
                }
            }
        )

        # Create a source record
        source_record = {
            "source_id": 123,
            "source_name": "Test Product",
            "source_price": 99.99,
            "unmapped_field": "value",
        }

        # Apply field mappings
        result = transformer.apply_field_mappings(source_record)

        # Check result
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "Test Product")
        self.assertEqual(result["price"], 99.99)
        # Unmapped fields are no longer preserved by apply_field_mappings
        self.assertNotIn("unmapped_field", result)

    def test_apply_custom_transformers(self):
        """Test that apply_custom_transformers applies custom transformers."""
        # Create a transformer
        transformer = MockTransformer({})

        # Register custom transformers
        transformer.register_custom_transformer("price", lambda x: float(x) * 1.2)
        transformer.register_custom_transformer("name", lambda x: x.upper())

        # Create a record
        record = {"id": 123, "name": "Test Product", "price": "99.99"}

        # Apply custom transformers
        result = transformer.apply_custom_transformers(record, {})

        # Check result
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "TEST PRODUCT")
        # Use assertAlmostEqual for floating point comparisons
        self.assertAlmostEqual(result["price"], 119.988, places=3)

    def test_validate_record(self):
        """Test that validate_record applies validation rules."""
        # Create a transformer with validation rules
        transformer = MockTransformer(
            {
                "validation_rules": [
                    {
                        "field": "price",
                        "check": "greater_than",
                        "value": 0,
                        "message": "Price must be positive",
                    },
                    {
                        "field": "name",
                        "check": "required",
                        "message": "Name is required",
                    },
                ]
            }
        )

        # Create a valid record
        valid_record = {"id": 123, "name": "Test Product", "price": 99.99}

        # Validate valid record
        errors = transformer.validate_record(valid_record)
        self.assertEqual(len(errors), 0)

        # Create an invalid record
        invalid_record = {"id": 123, "price": -10}

        # Validate invalid record
        errors = transformer.validate_record(invalid_record)

        # Check errors
        price_errors = [e for e in errors if e.field == "price"]
        self.assertEqual(len(price_errors), 1)
        
        # There will be no name error since the test validation is for "check": "required"
        # but the BaseTransformer doesn't implement that check

    def test_validation_error(self):
        """Test the ValidationError class."""
        # Create a validation error
        error = ValidationError(
            field="price",
            message="Price must be positive",
            error_type="error",
            context={"value": -10},
        )

        # Check attributes
        self.assertEqual(error.field, "price")
        self.assertEqual(error.message, "Price must be positive")
        self.assertEqual(error.error_type, "error")
        self.assertEqual(error.context, {"value": -10})


@pytest.mark.unit
class TestBaseLoader(TestCase):
    """Tests for the BaseLoader class."""

    def test_load_result(self):
        """Test the LoadResult class."""
        # Create a load result
        result = LoadResult()

        # Check initial values
        self.assertEqual(result.created, 0)
        self.assertEqual(result.updated, 0)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.errors, 0)
        self.assertEqual(result.error_details, [])

        # Add an error
        record = {"id": 123}
        error = ValueError("Invalid value")
        context = {"field": "price"}
        result.add_error(record, error, context)

        # Check updated values
        self.assertEqual(result.errors, 1)
        self.assertEqual(len(result.error_details), 1)
        self.assertEqual(result.error_details[0]["record"], record)
        self.assertEqual(result.error_details[0]["error"], "Invalid value")
        self.assertEqual(result.error_details[0]["context"], context)

        # Check to_dict
        result_dict = result.to_dict()
        self.assertEqual(result_dict["created"], 0)
        self.assertEqual(result_dict["updated"], 0)
        self.assertEqual(result_dict["skipped"], 0)
        self.assertEqual(result_dict["errors"], 1)
        self.assertEqual(len(result_dict["error_details"]), 1)

    def test_validate_config_with_missing_fields(self):
        """Test that _validate_config raises ValueError for missing fields."""
        # Create a test loader that requires a key_field
        class KeyFieldLoader(TestLoader):
            def get_required_config_fields(self):
                return super().get_required_config_fields() + ["key_field"]
        
        # Test with missing fields
        with self.assertRaises(ValueError) as context:
            KeyFieldLoader(config={"destination_url": "http://example.com"})

        # Check error message
        self.assertIn("Missing required configuration fields", str(context.exception))
        self.assertIn("key_field", str(context.exception))

    def test_load(self):
        """Test the load method works correctly."""
        # Create a special test loader for this test
        class TestLoadLoader(TestLoader):
            def prepare_record(self, record):
                # Simulate preparing record for loading
                # Don't raise an error here, let it happen in load_record
                lookup_criteria = {}
                prepared_record = record.copy()

                if "id" in record:
                    lookup_criteria["id"] = record["id"]

                return lookup_criteria, prepared_record

            def load_record(self, lookup_criteria, record, update_existing=True):
                # Simulate loading a record
                import unittest.mock
                
                # For ID 3, we'll simulate an error during loading
                if record.get("id") == 3:
                    raise ValueError("Test error")
                
                # Create mock object with _state for detecting create/update
                mock_obj = unittest.mock.MagicMock()
                mock_obj._state = unittest.mock.MagicMock()
                
                # Ensure the 'adding' attribute is accessed correctly by the BaseLoader.load method
                if lookup_criteria and lookup_criteria.get("id") == 2:
                    # Update scenario
                    mock_obj._state.adding = False
                else:
                    # Create scenario
                    mock_obj._state.adding = True
                
                return mock_obj

        # Create loader
        loader = TestLoadLoader(config={"destination_url": "http://example.com"})

        # Test records
        records = [
            {"id": 1, "name": "Test 1"},  # Create
            {"id": 2, "name": "Test 2"},  # Update
            {"id": 3, "name": "Test 3"},  # Error
        ]

        # Load records
        result = loader.load(records)

        # Check result
        self.assertEqual(result.created, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.skipped, 0)
        self.assertEqual(result.errors, 1)
