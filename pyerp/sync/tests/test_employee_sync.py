"""Tests for employee synchronization tasks."""

import pytest
from unittest import mock
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget, SyncLog
from pyerp.sync.tasks import (
    sync_employees, 
    scheduled_employee_sync,
    nightly_full_employee_sync,
)
from pyerp.sync.transformers.employee import EmployeeTransformer


@pytest.mark.unit
class TestEmployeeSync(TestCase):
    """Tests for the employee sync tasks."""

    def setUp(self):
        """Set up test data with mocks."""
        # Mock source and target
        self.source = mock.MagicMock(spec=SyncSource)
        self.source.name = "legacy_erp"
        self.source.description = "Legacy 4D ERP System"
        self.source.config = {
            "extractor_class": "pyerp.sync.extractors.legacy_api.LegacyAPIExtractor",
            "config": {
                "environment": "test",
                "table_name": "Pers",
                "key_field": "__KEY"
            },
        }

        self.target = mock.MagicMock(spec=SyncTarget)
        self.target.name = "django_models"
        self.target.description = "Django ORM Models"
        self.target.config = {
            "loader_class": "pyerp.sync.loaders.django_model.DjangoModelLoader",
            "config": {
                "app_label": "business",
                "model_name": "Employee",
            }
        }

        # Mock employee mapping
        self.mapping = mock.MagicMock(spec=SyncMapping)
        self.mapping.id = 1
        self.mapping.source = self.source
        self.mapping.target = self.target
        self.mapping.entity_type = "employee"
        self.mapping.mapping_config = {
            "transformer_class": "pyerp.sync.transformers.employee.EmployeeTransformer",
            "field_mappings": {
                "Pers_Nr": "employee_number",
                "Name": "last_name",
                "Vorname": "first_name",
                "eMail": "email",
                "__KEY": "legacy_id",
            }
        }
        self.mapping.active = True

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    @mock.patch("pyerp.sync.tasks.SyncSource.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncTarget.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.get_or_create")
    def test_sync_employees(self, mock_get_mapping, mock_get_target, 
                            mock_get_source, mock_factory):
        """Test the sync_employees task."""
        # Set up mock get_or_create returns
        mock_get_source.return_value = (self.source, False)
        mock_get_target.return_value = (self.target, False)
        mock_get_mapping.return_value = (self.mapping, False)

        # Set up mock pipeline
        mock_pipeline = mock.MagicMock()
        mock_factory().create_pipeline.return_value = mock_pipeline

        # Set up mock sync log
        mock_log = mock.MagicMock(spec=SyncLog)
        mock_log.id = 123
        mock_log.records_processed = 10
        mock_log.records_succeeded = 9
        mock_log.records_failed = 1
        mock_pipeline.run.return_value = mock_log

        # Run the task with default parameters
        result = sync_employees()

        # Check that get_or_create was called correctly
        mock_get_source.assert_called_once()
        mock_get_target.assert_called_once()
        mock_get_mapping.assert_called_once()

        # Check that pipeline was created and run correctly
        mock_factory().create_pipeline.assert_called_once_with(self.mapping)
        mock_pipeline.run.assert_called_once_with(
            incremental=True,  # Default is incremental=True
            query_params={},
            batch_size=100
        )

        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mapping_id"], self.mapping.id)
        self.assertEqual(result["sync_log_id"], mock_log.id)
        self.assertEqual(result["records_processed"], 10)
        self.assertEqual(result["records_succeeded"], 9)
        self.assertEqual(result["records_failed"], 1)

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    @mock.patch("pyerp.sync.tasks.SyncSource.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncTarget.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.get_or_create")
    def test_sync_employees_full_sync(self, mock_get_mapping, mock_get_target, 
                                     mock_get_source, mock_factory):
        """Test the sync_employees task with full_sync=True."""
        # Set up mock get_or_create returns
        mock_get_source.return_value = (self.source, False)
        mock_get_target.return_value = (self.target, False)
        mock_get_mapping.return_value = (self.mapping, False)

        # Set up mock pipeline
        mock_pipeline = mock.MagicMock()
        mock_factory().create_pipeline.return_value = mock_pipeline

        # Set up mock sync log
        mock_log = mock.MagicMock(spec=SyncLog)
        mock_log.id = 124
        mock_log.records_processed = 100
        mock_log.records_succeeded = 95
        mock_log.records_failed = 5
        mock_pipeline.run.return_value = mock_log

        # Run the task with full_sync=True
        result = sync_employees(full_sync=True)

        # Check that pipeline was run with incremental=False
        mock_pipeline.run.assert_called_once_with(
            incremental=False,
            query_params={},
            batch_size=100
        )

        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_processed"], 100)
        self.assertEqual(result["records_succeeded"], 95)
        self.assertEqual(result["records_failed"], 5)

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    @mock.patch("pyerp.sync.tasks.SyncSource.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncTarget.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.get_or_create")
    def test_sync_employees_with_filters(self, mock_get_mapping, mock_get_target, 
                                         mock_get_source, mock_factory):
        """Test the sync_employees task with filters."""
        # Set up mock get_or_create returns
        mock_get_source.return_value = (self.source, False)
        mock_get_target.return_value = (self.target, False)
        mock_get_mapping.return_value = (self.mapping, False)

        # Set up mock pipeline
        mock_pipeline = mock.MagicMock()
        mock_factory().create_pipeline.return_value = mock_pipeline

        # Set up mock sync log
        mock_log = mock.MagicMock(spec=SyncLog)
        mock_log.id = 125
        mock_log.records_processed = 5
        mock_log.records_succeeded = 5
        mock_log.records_failed = 0
        mock_pipeline.run.return_value = mock_log

        # Create test filters
        filters = {"department": "IT", "active": True}

        # Run the task with filters
        result = sync_employees(filters=filters)

        # Check that pipeline was run with correct query_params
        mock_pipeline.run.assert_called_once_with(
            incremental=True,
            query_params=filters,
            batch_size=100
        )

        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_processed"], 5)
        self.assertEqual(result["records_succeeded"], 5)
        self.assertEqual(result["records_failed"], 0)

    @mock.patch("pyerp.sync.tasks.PipelineFactory")
    @mock.patch("pyerp.sync.tasks.SyncSource.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncTarget.objects.get_or_create")
    @mock.patch("pyerp.sync.tasks.SyncMapping.objects.get_or_create")
    def test_sync_employees_error_handling(self, mock_get_mapping, mock_get_target, 
                                          mock_get_source, mock_factory):
        """Test the sync_employees task error handling."""
        # Set up mock get_or_create returns
        mock_get_source.return_value = (self.source, False)
        mock_get_target.return_value = (self.target, False)
        mock_get_mapping.return_value = (self.mapping, False)

        # Set up mock pipeline to raise an exception
        mock_pipeline = mock.MagicMock()
        mock_factory().create_pipeline.return_value = mock_pipeline
        mock_pipeline.run.side_effect = Exception("Test exception")

        # Run the task
        result = sync_employees()

        # Check result contains error
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Test exception")

    @mock.patch("pyerp.sync.tasks.sync_employees")
    def test_scheduled_employee_sync(self, mock_sync_employees):
        """Test the scheduled_employee_sync task."""
        # Set up mock return value
        mock_sync_employees.return_value = {
            "status": "success",
            "records_processed": 10
        }

        # Run the task
        result = scheduled_employee_sync()

        # Check that sync_employees was called with full_sync=False
        mock_sync_employees.assert_called_once_with(full_sync=False)

        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_processed"], 10)

    @mock.patch("pyerp.sync.tasks.sync_employees")
    def test_nightly_full_employee_sync(self, mock_sync_employees):
        """Test the nightly_full_employee_sync task."""
        # Set up mock return value
        mock_sync_employees.return_value = {
            "status": "success",
            "records_processed": 100
        }

        # Run the task
        result = nightly_full_employee_sync()

        # Check that sync_employees was called with full_sync=True
        mock_sync_employees.assert_called_once_with(full_sync=True)

        # Check result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["records_processed"], 100)


@pytest.mark.unit
class TestEmployeeTransformer(TestCase):
    """Tests for the EmployeeTransformer."""

    def setUp(self):
        """Set up test data."""
        # Properly initialize transformer with config dict
        self.transformer = EmployeeTransformer(
            config={
                "field_mappings": {
                    "Pers_Nr": "employee_number",
                    "Name": "last_name",
                    "Vorname": "first_name",
                    "eMail": "email",
                    "AD_Name": "ad_username",
                    "Straße": "street",
                    "PLZ": "postal_code",
                    "Ort": "city",
                    "Telefon": "phone",
                    "Telefon2": "mobile_phone",
                    "GebDatum": "birth_date",
                    "Eintrittsdatum": "hire_date",
                    "Austrittsdatum": "termination_date",
                    "ausgeschieden": "is_terminated",
                    "anwesend": "is_present",
                    "Geh_code": "salary_code",
                    "Monatsgehalt": "monthly_salary",
                    "Jahres_Gehalt": "annual_salary",
                    "Arb_Std_Wo": "weekly_hours",
                    "Arb_Std_Tag": "daily_hours",
                    "Jahrs_Urlaub": "annual_vacation_days",
                    "__KEY": "legacy_id",
                }
            }
        )

    def test_transform_basic_fields(self):
        """Test transforming basic employee fields."""
        source_data = [{
            "Pers_Nr": "E123",
            "Name": "Doe",
            "Vorname": "John",
            "eMail": "john.doe@example.com",
            "AD_Name": "johndoe",
            "__KEY": "1001",
        }]
        
        transformed = self.transformer.transform(source_data)
        
        self.assertEqual(len(transformed), 1)
        self.assertEqual(transformed[0]["employee_number"], "E123")
        self.assertEqual(transformed[0]["last_name"], "Doe")
        self.assertEqual(transformed[0]["first_name"], "John")
        self.assertEqual(transformed[0]["email"], "john.doe@example.com")
        self.assertEqual(transformed[0]["ad_username"], "johndoe")
        self.assertEqual(transformed[0]["legacy_id"], "1001")

    def test_transform_date_fields(self):
        """Test transforming date fields."""
        source_data = [{
            "Pers_Nr": "E123",
            "Name": "Doe",
            "GebDatum": "15!04!1985",
            "Eintrittsdatum": "01!06!2020",
            "Austrittsdatum": "0!0!0",  # Empty date
            "__KEY": "1001",
        }]
        
        transformed = self.transformer.transform(source_data)
        
        self.assertEqual(transformed[0]["birth_date"], "1985-04-15")
        self.assertEqual(transformed[0]["hire_date"], "2020-06-01")
        self.assertIsNone(transformed[0]["termination_date"])

    def test_transform_salary_data(self):
        """Test transforming salary data."""
        source_data = [{
            "Pers_Nr": "E123",
            "Name": "Doe",
            "Jahres_Gehalt": "60000",
            "Monatsgehalt": "5000",
            "Arb_Std_Wo": "40",
            "Arb_Std_Tag": "8",
            "__KEY": "1001",
        }]
        
        transformed = self.transformer.transform(source_data)
        
        self.assertEqual(transformed[0]["annual_salary"], 60000.00)
        self.assertEqual(transformed[0]["monthly_salary"], 5000.00)
        self.assertEqual(transformed[0]["weekly_hours"], 40.00)
        self.assertEqual(transformed[0]["daily_hours"], 8.00)

    def test_transform_boolean_fields(self):
        """Test transforming boolean fields."""
        source_data = [{
            "Pers_Nr": "E123",
            "Name": "Doe",
            "ausgeschieden": "0",
            "anwesend": "1",
            "__KEY": "1001",
        }]
        
        transformed = self.transformer.transform(source_data)
        
        self.assertFalse(transformed[0]["is_terminated"])
        self.assertTrue(transformed[0]["is_present"])

    def test_validation(self):
        """Test validation of transformed employee records."""
        # Valid record
        valid_record = {
            "employee_number": "E123",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
        
        errors = self.transformer.validate(valid_record)
        self.assertEqual(len(errors), 0)
        
        # Invalid record - missing required field
        invalid_record = {
            "last_name": "Doe",
            "email": "john.doe@example.com",
        }
        
        errors = self.transformer.validate(invalid_record)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].field, "employee_number")
        
        # Invalid email format
        invalid_email_record = {
            "employee_number": "E123",
            "last_name": "Doe",
            "email": "not-an-email",
        }
        
        errors = self.transformer.validate(invalid_email_record)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].field, "email")
        self.assertEqual(errors[0].error_type, "warning")

    def test_transform_error_handling(self):
        """Test error handling during transformation."""
        # Create a record that will cause an exception
        source_data = [
            {
                "Pers_Nr": "E123",
                # Will cause exception in _process_salary_data due to invalid value
                "Jahres_Gehalt": "not-a-number",
                "__KEY": "1001",
            }
        ]
        
        # Mock the _process_salary_data method to raise an exception
        with mock.patch.object(
            EmployeeTransformer, 
            '_process_salary_data', 
            side_effect=ValueError("Invalid salary data")
        ):
            transformed = self.transformer.transform(source_data)
            
            self.assertEqual(len(transformed), 1)
            self.assertTrue(transformed[0]["_has_errors"])
            self.assertEqual(transformed[0]["employee_number"], "E123")
            self.assertIn("Invalid salary data", transformed[0]["_error"]) 