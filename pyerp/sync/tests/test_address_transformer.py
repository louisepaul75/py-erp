"""Tests for the address transformer module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from django.utils import timezone
from pyerp.sync.transformers.address import AddressTransformer


@pytest.mark.unit
class TestAddressTransformer:
    """Tests for the AddressTransformer class."""

    def test_init_with_default_mappings(self):
        """Test initialization with default field mappings."""
        transformer = AddressTransformer({})
        
        # Verify default mappings are present
        assert "salutation" in transformer.field_mappings
        assert "first_name" in transformer.field_mappings
        assert "last_name" in transformer.field_mappings
        assert "company_name" in transformer.field_mappings
        assert "street" in transformer.field_mappings
        assert "country" in transformer.field_mappings
        assert "postal_code" in transformer.field_mappings
        assert "city" in transformer.field_mappings
        assert "phone" in transformer.field_mappings
        assert "fax" in transformer.field_mappings
        assert "email" in transformer.field_mappings
        assert "contact_person" in transformer.field_mappings
        assert "formal_salutation" in transformer.field_mappings
        assert "legacy_id" in transformer.field_mappings
        
        # Verify specific mappings
        assert transformer.field_mappings["salutation"] == "Anrede"
        assert transformer.field_mappings["first_name"] == "Vorname"
        assert transformer.field_mappings["last_name"] == "Name1"
        assert transformer.field_mappings["legacy_id"] == "__KEY"

    def test_init_with_custom_mappings(self):
        """Test initialization with custom field mappings."""
        custom_mappings = {
            "first_name": "custom_first_name_field",
            "last_name": "custom_last_name_field"
        }
        
        transformer = AddressTransformer({"field_mappings": custom_mappings})
        
        # Verify custom mappings overrode defaults
        assert transformer.field_mappings["first_name"] == "custom_first_name_field"
        assert transformer.field_mappings["last_name"] == "custom_last_name_field"
        
        # Verify other defaults are still present
        assert transformer.field_mappings["salutation"] == "Anrede"
        assert transformer.field_mappings["company_name"] == "Name2"

    @patch("pyerp.sync.transformers.address.apps")
    def test_transform_customer_model_not_found(self, mock_apps):
        """Test transform behavior when Customer model is not found."""
        # Setup mock to raise LookupError
        mock_apps.get_model.side_effect = LookupError("Customer model not found")
        
        transformer = AddressTransformer({})
        source_data = [{"AdrNr": "12345", "Name1": "Test Customer"}]
        
        result = transformer.transform(source_data)
        
        # Should return empty list when Customer model not found
        assert result == []
        mock_apps.get_model.assert_called_once_with("sales", "Customer")

    @patch("pyerp.sync.transformers.address.apps")
    def test_transform_error_fetching_customers(self, mock_apps):
        """Test transform behavior when error occurs fetching customers."""
        # Setup mock Customer model
        mock_customer = MagicMock()
        mock_customer.objects.values_list.side_effect = Exception("DB error")
        mock_apps.get_model.return_value = mock_customer
        
        transformer = AddressTransformer({})
        source_data = [{"AdrNr": "12345", "Name1": "Test Customer"}]
        
        # Should handle the exception and continue processing
        transformer.transform(source_data)
        
        mock_apps.get_model.assert_called_once_with("sales", "Customer")
        mock_customer.objects.values_list.assert_called_once_with("legacy_address_number", flat=True)

    @patch("pyerp.sync.transformers.address.apps")
    def test_transform_successful_processing(self, mock_apps):
        """Test successful transformation of address data."""
        # Setup mock Customer model
        mock_customer = MagicMock()
        mock_customer.objects.values_list.return_value = ["12345"]
        
        mock_customer_instance = MagicMock()
        mock_customer_instance.id = 1
        mock_customer_instance.customer_number = "C12345"
        
        mock_customer.objects.get.return_value = mock_customer_instance
        mock_apps.get_model.return_value = mock_customer
        
        transformer = AddressTransformer({})
        
        source_data = [{
            "AdrNr": "12345",
            "Anrede": "Hr.",
            "Vorname": "John",
            "Name1": "Doe",
            "Name2": "ACME Corp",
            "Strasse": "123 Main St",
            "Land": "DE",
            "PLZ": "12345",
            "Ort": "Berlin",
            "Telefon": "1234567890",
            "Fax": "0987654321",
            "e_Mail": "john.doe@example.com",
            "Ansprechp": "Jane Smith",
            "Briefanrede": "Sehr geehrter Herr Doe",
            "__KEY": "address_12345",
            "__TIMESTAMP": "2025-03-06T04:13:17.687Z"
        }]
        
        result = transformer.transform(source_data)
        
        # Verify the transformation result
        assert len(result) == 1
        transformed = result[0]
        
        assert transformed["salutation"] == "Hr."
        assert transformed["first_name"] == "John"
        assert transformed["last_name"] == "Doe"
        assert transformed["company_name"] == "ACME Corp"
        assert transformed["street"] == "123 Main St"
        assert transformed["country"] == "DE"
        assert transformed["postal_code"] == "12345"
        assert transformed["city"] == "Berlin"
        assert transformed["phone"] == "1234567890"
        assert transformed["fax"] == "0987654321"
        assert transformed["email"] == "john.doe@example.com"
        assert transformed["contact_person"] == "Jane Smith"
        assert transformed["formal_salutation"] == "Sehr geehrter Herr Doe"
        assert transformed["legacy_id"] == "address_12345"
        assert transformed["address_number"] == "12345"
        assert transformed["customer"] == mock_customer_instance
        assert transformed["is_synchronized"] is True
        
        # Verify legacy_modified was parsed
        assert isinstance(transformed["legacy_modified"], datetime)
        assert transformed["legacy_modified"].year == 2025
        assert transformed["legacy_modified"].month == 3
        assert transformed["legacy_modified"].day == 6

    @patch("pyerp.sync.transformers.address.apps")
    def test_transform_customer_not_found(self, mock_apps):
        """Test behavior when customer is not found for address."""
        # Setup mock Customer model
        mock_customer = MagicMock()
        mock_customer.objects.values_list.return_value = ["12345"]
        mock_customer.DoesNotExist = Exception
        mock_customer.objects.get.side_effect = mock_customer.DoesNotExist("Customer not found")
        mock_apps.get_model.return_value = mock_customer
        
        transformer = AddressTransformer({})
        source_data = [{
            "AdrNr": "12345",
            "Name1": "Test Customer"
        }]
        
        result = transformer.transform(source_data)
        
        # Should not include addresses without customers
        assert len(result) == 0

    def test_parse_legacy_timestamp_valid(self):
        """Test parsing of valid legacy timestamp."""
        transformer = AddressTransformer({})
        timestamp = "2025-03-06T04:13:17.687Z"
        
        result = transformer._parse_legacy_timestamp(timestamp)
        
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 3
        assert result.day == 6
        assert result.hour == 4
        assert result.minute == 13
        assert result.second == 17
        assert result.tzinfo is not None  # Should have timezone info

    def test_parse_legacy_timestamp_invalid(self):
        """Test parsing of invalid legacy timestamp."""
        transformer = AddressTransformer({})
        
        # Test with invalid format
        result1 = transformer._parse_legacy_timestamp("invalid-timestamp")
        assert isinstance(result1, datetime)
        
        # Test with empty string
        result2 = transformer._parse_legacy_timestamp("")
        assert isinstance(result2, datetime)
        
        # Test with None
        result3 = transformer._parse_legacy_timestamp(None)
        assert isinstance(result3, datetime)

    def test_clean_country_code_valid(self):
        """Test cleaning of valid country codes."""
        transformer = AddressTransformer({})
        
        # Test valid 2-letter code
        assert transformer._clean_country_code("DE") == "DE"
        assert transformer._clean_country_code("de") == "DE"
        assert transformer._clean_country_code(" FR ") == "FR"
        
        # Test common variations
        assert transformer._clean_country_code("DEU") == "DE"
        assert transformer._clean_country_code("GER") == "DE"
        assert transformer._clean_country_code("DEUTSCHLAND") == "DE"
        assert transformer._clean_country_code("GERMANY") == "DE"
        assert transformer._clean_country_code("AUT") == "AT"
        assert transformer._clean_country_code("AUSTRIA") == "AT"
        assert transformer._clean_country_code("ÖSTERREICH") == "AT"
        assert transformer._clean_country_code("CHE") == "CH"
        assert transformer._clean_country_code("SWITZERLAND") == "CH"
        assert transformer._clean_country_code("SCHWEIZ") == "CH"

    def test_clean_country_code_invalid(self):
        """Test cleaning of invalid country codes."""
        transformer = AddressTransformer({})
        
        # Test empty values
        assert transformer._clean_country_code("") == ""
        assert transformer._clean_country_code(None) == ""
        
        # Test invalid values
        assert transformer._clean_country_code("INVALID") == ""
        assert transformer._clean_country_code("X") == ""
        assert transformer._clean_country_code("123") == ""

    def test_clean_email_valid(self):
        """Test cleaning of valid email addresses."""
        transformer = AddressTransformer({})
        
        # Test valid emails
        assert transformer._clean_email("test@example.com") == "test@example.com"
        assert transformer._clean_email(" user@domain.com ") == "user@domain.com"
        assert transformer._clean_email("TEST@EXAMPLE.COM") == "test@example.com"
        
    def test_clean_email_invalid(self):
        """Test cleaning of invalid email addresses."""
        transformer = AddressTransformer({})
        
        # Test empty values
        assert transformer._clean_email("") == ""
        assert transformer._clean_email(None) == ""
        
        # Test invalid formats - these should all return empty string
        assert transformer._clean_email("not-an-email") == ""
        assert transformer._clean_email("missing@domain") == ""  # No dot after @
        assert transformer._clean_email("no-at-sign.com") == ""
        assert transformer._clean_email("multiple@@at.com") == "" 