"""Tests for the sync loaders module."""

import pytest
from unittest.mock import MagicMock, patch
from django.db import models
from django.core.exceptions import ValidationError as DjangoValidationError

from pyerp.sync.loaders.base import BaseLoader, LoadResult
from pyerp.sync.loaders.django_model import DjangoModelLoader


@pytest.mark.unit
class TestLoadResult:
    """Tests for the LoadResult class."""





















    def test_init(self):
        """Test initialization of LoadResult."""
        result = LoadResult()
        assert result.created == 0
        assert result.updated == 0
        assert result.skipped == 0
        assert result.errors == 0
        assert result.error_details == []




    def test_add_error(self):
        """Test adding an error to LoadResult."""
        result = LoadResult()
        record = {"id": 1, "name": "Test"}
        error = ValueError("Test error")
        context = {"update_existing": True}
        
        result.add_error(record, error, context)
        
        assert result.errors == 1
        assert len(result.error_details) == 1
        assert result.error_details[0]["record"] == record
        assert result.error_details[0]["error"] == str(error)
        assert result.error_details[0]["context"] == context




    def test_to_dict(self):
        """Test converting LoadResult to dictionary."""
        result = LoadResult()
        result.created = 5
        result.updated = 3
        result.skipped = 2
        result.errors = 1
        result.error_details = [{"record": {}, "error": "Error", "context": {}}]
        
        result_dict = result.to_dict()
        
        assert result_dict["created"] == 5
        assert result_dict["updated"] == 3
        assert result_dict["skipped"] == 2
        assert result_dict["errors"] == 1
        assert len(result_dict["error_details"]) == 1


# Create a mock model for testing
class MockModel(models.Model):
    """Mock model for testing."""
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    
    class Meta:
        """Meta class to prevent creating actual table."""
        app_label = 'testapp'
        managed = False


@pytest.mark.unit
@patch('pyerp.sync.loaders.django_model.apps.get_model')
class TestDjangoModelLoader:
    """Tests for the DjangoModelLoader."""

    def test_get_required_config_fields(self, mock_get_model):
        """Test required config fields method."""
        mock_get_model.return_value = MockModel
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        required_fields = loader.get_required_config_fields()
        
        assert "app_name" in required_fields
        assert "model_name" in required_fields
        assert "unique_field" in required_fields

    def test_get_model_class(self, mock_get_model):
        """Test getting model class from configuration."""
        # Setup the mock
        mock_get_model.return_value = MockModel
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        model_class = loader._get_model_class()
        
        # Verify the mock was called correctly
        mock_get_model.assert_called_once_with("testapp", "MockModel")
        assert model_class == MockModel

    def test_get_model_class_error(self, mock_get_model):
        """Test error handling when getting model class."""
        # Setup the mock to raise an exception
        mock_get_model.side_effect = LookupError("Model not found")
        
        with pytest.raises(ValueError) as exc_info:
            loader = DjangoModelLoader({
                "app_name": "testapp",
                "model_name": "NonExistentModel",
                "unique_field": "code"
            })
        
        assert "Failed to get model" in str(exc_info.value)

    def test_prepare_record(self, mock_get_model):
        """Test preparing a record for loading."""
        # Setup mock
        mock_model = MagicMock()
        mock_model.__name__ = 'MockModel'
        field_mock = MagicMock()
        field_mock.name = "code"
        field_mock.primary_key = False
        field_mock.auto_created = False
        
        name_field = MagicMock()
        name_field.name = "name"
        name_field.primary_key = False
        name_field.auto_created = False
        
        id_field = MagicMock()
        id_field.name = "id"
        id_field.primary_key = True
        id_field.auto_created = True
        
        mock_model._meta.get_fields.return_value = [field_mock, name_field, id_field]
        mock_get_model.return_value = mock_model
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        record = {
            "code": "TEST001",
            "name": "Test Product",
            "id": 1,
            "non_existent_field": "value"
        }
        
        lookup_criteria, prepared_record = loader.prepare_record(record)
        
        assert lookup_criteria == {"code": "TEST001"}
        assert "code" in prepared_record
        assert "name" in prepared_record
        assert "id" not in prepared_record  # Should be removed as it's a PK
        assert "non_existent_field" not in prepared_record  # Should be removed as it doesn't exist

    def test_prepare_record_missing_unique_field(self, mock_get_model):
        """Test error when unique field is missing."""
        mock_get_model.return_value = MockModel
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        record = {
            "name": "Test Product without code"
        }
        
        with pytest.raises(ValueError) as exc_info:
            loader.prepare_record(record)
        
        assert "Record missing unique field: code" in str(exc_info.value)

    @patch('django.db.transaction.atomic')
    def test_load_record_create(self, mock_atomic, mock_get_model):
        """Test creating a new record."""
        # Setup mocks
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None
        
        # Create a proper mock with a name attribute to avoid __name__ attribute error
        mock_model = MagicMock()
        mock_model.__name__ = 'MockModel'
        
        mock_model_instance = MagicMock()
        mock_model_instance._state = MagicMock()
        mock_model_instance._state.adding = True  # Indicates a new record
        
        # Set up the model to return itself on constructor call
        mock_model.return_value = mock_model_instance
        mock_model.objects.filter.return_value.first.return_value = None  # No existing record
        
        mock_get_model.return_value = mock_model
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        lookup_criteria = {"code": "TEST001"}
        record = {"code": "TEST001", "name": "Test Product"}
        
        result = loader.load_record(lookup_criteria, record)
        
        # Verify mock calls
        mock_model.objects.filter.assert_called_once_with(**lookup_criteria)
        assert result is mock_model_instance
        mock_model_instance.full_clean.assert_called_once()
        mock_model_instance.save.assert_called_once()

    @patch('django.db.transaction.atomic')
    def test_load_record_update(self, mock_atomic, mock_get_model):
        """Test updating an existing record."""
        # Setup mocks
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None
        
        mock_model_instance = MagicMock()
        mock_model_instance._state = MagicMock()
        mock_model_instance._state.adding = False  # Indicates an existing record
        
        mock_model = MagicMock()
        mock_model.__name__ = 'MockModel'  # Add name attribute to avoid __name__ error
        mock_model.objects.filter.return_value.first.return_value = mock_model_instance  # Existing record
        
        mock_get_model.return_value = mock_model
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        lookup_criteria = {"code": "TEST001"}
        record = {"code": "TEST001", "name": "Updated Product"}
        
        result = loader.load_record(lookup_criteria, record)
        
        # Verify mock calls
        mock_model.objects.filter.assert_called_once_with(**lookup_criteria)
        assert result is mock_model_instance
        mock_model_instance.full_clean.assert_called_once()
        mock_model_instance.save.assert_called_once()
        
        # Verify attributes were set
        assert mock_model_instance.code == "TEST001"
        assert mock_model_instance.name == "Updated Product"

    @patch('django.db.transaction.atomic')
    def test_load_record_skip_existing(self, mock_atomic, mock_get_model):
        """Test skipping an existing record when update_existing is False."""
        # Setup mocks
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None
        
        mock_model_instance = MagicMock()
        
        mock_model = MagicMock()
        mock_model.__name__ = 'MockModel'  # Add name attribute to avoid __name__ error
        mock_model.objects.filter.return_value.first.return_value = mock_model_instance  # Existing record
        
        mock_get_model.return_value = mock_model
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        lookup_criteria = {"code": "TEST001"}
        record = {"code": "TEST001", "name": "Should Not Update"}
        
        result = loader.load_record(lookup_criteria, record, update_existing=False)
        
        # Verify record was skipped
        assert result is None
        mock_model_instance.save.assert_not_called()

    @patch('django.db.transaction.atomic')
    def test_load_record_validation_error(self, mock_atomic, mock_get_model):
        """Test handling validation errors."""
        # Setup mocks
        mock_atomic.return_value.__enter__.return_value = None
        mock_atomic.return_value.__exit__.return_value = None
        
        mock_model_instance = MagicMock()
        
        # Create a real Django ValidationError
        validation_error = DjangoValidationError("Validation failed")
        mock_model_instance.full_clean.side_effect = validation_error
        
        mock_model = MagicMock()
        mock_model.__name__ = 'MockModel'  # Add name attribute to avoid __name__ error
        mock_model.objects.filter.return_value.first.return_value = None  # No existing record
        mock_model.return_value = mock_model_instance
        
        mock_get_model.return_value = mock_model
        
        loader = DjangoModelLoader({
            "app_name": "testapp",
            "model_name": "MockModel",
            "unique_field": "code"
        })
        
        lookup_criteria = {"code": "TEST001"}
        record = {"code": "TEST001", "name": "Test Product"}
        
        with pytest.raises(ValueError) as exc_info:
            loader.load_record(lookup_criteria, record)
        
        assert "Validation failed" in str(exc_info.value)
        mock_model_instance.save.assert_not_called() 