from django.test import TestCase

from pyerp.sync.extractors.base import BaseExtractor
from pyerp.sync.transformers.base import BaseTransformer, ValidationError
from pyerp.sync.loaders.base import BaseLoader, LoadResult


class TestBaseExtractor(TestCase):
    """Tests for the BaseExtractor class."""

    def test_validate_config_with_missing_fields(self):
        """Test that _validate_config raises ValueError for missing fields."""
        # Create a subclass that requires fields
        class TestExtractor(BaseExtractor):
            def get_required_config_fields(self):
                return ["api_key", "url"]
                
            def connect(self):
                pass
                
            def extract(self, query_params=None):
                return []
        
        # Test with missing fields
        with self.assertRaises(ValueError) as context:
            TestExtractor(config={"api_key": "test"})
            
        # Check error message
        self.assertIn("Missing required configuration fields", str(context.exception))
        self.assertIn("url", str(context.exception))

    def test_validate_config_with_all_fields(self):
        """Test that _validate_config passes with all required fields."""
        # Create a subclass that requires fields
        class TestExtractor(BaseExtractor):
            def get_required_config_fields(self):
                return ["api_key", "url"]
                
            def connect(self):
                pass
                
            def extract(self, query_params=None):
                return []
        
        # Test with all fields
        config = {"api_key": "test", "url": "http://example.com"}
        extractor = TestExtractor(config=config)
        
        # Check that config was set
        self.assertEqual(extractor.config["api_key"], "test")
        self.assertEqual(extractor.config["url"], "http://example.com")

    def test_context_manager(self):
        """Test that extractor can be used as a context manager."""
        # Create a subclass with mock methods
        class TestExtractor(BaseExtractor):
            def get_required_config_fields(self):
                return []
                
            def connect(self):
                self.connect_called = True
                
            def extract(self, query_params=None):
                return []
                
            def close(self):
                self.close_called = True
        
        # Create instance
        extractor = TestExtractor(config={})
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


class TestBaseTransformer(TestCase):
    """Tests for the BaseTransformer class."""

    def test_apply_field_mappings(self):
        """Test that apply_field_mappings correctly maps fields."""
        # Create a transformer with field mappings
        transformer = BaseTransformer({
            "field_mappings": {
                "source_id": "id",
                "source_name": "name",
                "source_price": "price"
            }
        })
        
        # Create a source record
        source_record = {
            "source_id": 123,
            "source_name": "Test Product",
            "source_price": 99.99,
            "unmapped_field": "value"
        }
        
        # Apply field mappings
        result = transformer.apply_field_mappings(source_record)
        
        # Check result
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "Test Product")
        self.assertEqual(result["price"], 99.99)
        self.assertNotIn("unmapped_field", result)
        self.assertNotIn("source_id", result)

    def test_apply_custom_transformers(self):
        """Test that apply_custom_transformers applies custom transformers."""
        # Create a transformer
        transformer = BaseTransformer({})
        
        # Register custom transformers
        transformer.register_custom_transformer(
            "price", lambda x: float(x) * 1.2
        )
        transformer.register_custom_transformer(
            "name", lambda x: x.upper()
        )
        
        # Create a record
        record = {
            "id": 123,
            "name": "Test Product",
            "price": "99.99"
        }
        
        # Apply custom transformers
        result = transformer.apply_custom_transformers(record, {})
        
        # Check result
        self.assertEqual(result["id"], 123)
        self.assertEqual(result["name"], "TEST PRODUCT")
        self.assertEqual(result["price"], 119.988)

    def test_validate_record(self):
        """Test that validate_record applies validation rules."""
        # Create a transformer with validation rules
        transformer = BaseTransformer({
            "validation_rules": [
                {
                    "field": "price",
                    "rule": "min_value",
                    "value": 0,
                    "message": "Price must be positive"
                },
                {
                    "field": "name",
                    "rule": "required",
                    "message": "Name is required"
                }
            ]
        })
        
        # Create a valid record
        valid_record = {
            "id": 123,
            "name": "Test Product",
            "price": 99.99
        }
        
        # Validate valid record
        errors = transformer.validate_record(valid_record)
        self.assertEqual(len(errors), 0)
        
        # Create an invalid record
        invalid_record = {
            "id": 123,
            "price": -10
        }
        
        # Validate invalid record
        errors = transformer.validate_record(invalid_record)
        
        # Check errors
        self.assertEqual(len(errors), 2)
        
        # Check price error
        price_error = next(e for e in errors if e.field == "price")
        self.assertEqual(price_error.message, "Price must be positive")
        
        # Check name error
        name_error = next(e for e in errors if e.field == "name")
        self.assertEqual(name_error.message, "Name is required")

    def test_validation_error(self):
        """Test the ValidationError class."""
        # Create a validation error
        error = ValidationError(
            field="price",
            message="Price must be positive",
            error_type="error",
            context={"value": -10}
        )
        
        # Check attributes
        self.assertEqual(error.field, "price")
        self.assertEqual(error.message, "Price must be positive")
        self.assertEqual(error.error_type, "error")
        self.assertEqual(error.context, {"value": -10})


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
        # Create a subclass that requires fields
        class TestLoader(BaseLoader):
            def get_required_config_fields(self):
                return ["model_class", "key_field"]
                
            def prepare_record(self, record):
                return {}, {}
                
            def load_record(
                self, lookup_criteria, record, update_existing=True
            ):
                return None
        
        # Test with missing fields
        with self.assertRaises(ValueError) as context:
            TestLoader(config={"model_class": "app.models.TestModel"})
            
        # Check error message
        error_msg = str(context.exception)
        self.assertIn("Missing required configuration fields", error_msg)
        self.assertIn("key_field", error_msg)

    def test_load(self):
        """Test the load method."""
        # Create a subclass with mock methods
        class TestLoader(BaseLoader):
            def get_required_config_fields(self):
                return []
                
            def prepare_record(self, record):
                return {"id": record["id"]}, record
                
            def load_record(
                self, lookup_criteria, record, update_existing=True
            ):
                if lookup_criteria["id"] == 1:
                    # Existing record
                    return "updated"
                elif lookup_criteria["id"] == 2:
                    # New record
                    return "created"
                elif lookup_criteria["id"] == 3:
                    # Error
                    raise ValueError("Test error")
                else:
                    # Skip
                    return None
        
        # Create loader
        loader = TestLoader(config={})
        
        # Create test records
        records = [
            {"id": 1, "name": "Existing"},
            {"id": 2, "name": "New"},
            {"id": 3, "name": "Error"},
            {"id": 4, "name": "Skip"}
        ]
        
        # Load records
        result = loader.load(records)
        
        # Check result
        self.assertEqual(result.created, 1)
        self.assertEqual(result.updated, 1)
        self.assertEqual(result.skipped, 1)
        self.assertEqual(result.errors, 1)
        self.assertEqual(len(result.error_details), 1)
        self.assertEqual(result.error_details[0]["record"]["id"], 3) 