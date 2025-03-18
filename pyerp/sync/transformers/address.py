"""Transform address data from legacy format to new model format."""

from datetime import datetime
from typing import Any, Dict, List, Set
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.apps import apps
from .base import BaseTransformer
from pyerp.utils.logging import get_logger


# Get logger for data sync operations
logger = get_logger(__name__)


class AddressTransformer(BaseTransformer):
    """Transforms address data from legacy Adressen format to Address model."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with default field mappings for addresses."""
        default_mappings = {
            "salutation": "Anrede",
            "first_name": "Vorname",
            "last_name": "Name1",
            "company_name": "Name2",
            "street": "Strasse",
            "country": "Land",
            "postal_code": "PLZ",
            "city": "Ort",
            "phone": "Telefon",
            "fax": "Fax",
            "email": "e_Mail",
            "contact_person": "Ansprechp",
            "formal_salutation": "Briefanrede",
            "legacy_id": "__KEY",
        }

        # Merge default mappings with any provided in config
        if "field_mappings" in config:
            default_mappings.update(config["field_mappings"])
        config["field_mappings"] = default_mappings

        super().__init__(config)

    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform address records from legacy format.

        Args:
            source_data: List of address records from legacy system

        Returns:
            List of transformed address records
        """
        transformed_records = []

        # Get the Customer model
        try:
            Customer = apps.get_model("sales", "Customer")
        except LookupError:
            logger.error("Could not find Customer model in sales app")
            Customer = None
            return transformed_records

        # Get all existing address numbers for prefiltering
        existing_address_numbers: Set[str] = set()
        if Customer:
            try:
                # Fetch all legacy address numbers from the database
                existing_address_numbers = set(
                    Customer.objects.values_list("legacy_address_number", flat=True)
                )
                logger.info(
                    f"Found {len(existing_address_numbers)} existing "
                    f"customers for prefiltering"
                )
            except Exception as e:
                logger.error(f"Error fetching address numbers: {e}")

        # Prepare records with address numbers for prefiltering
        records_with_address_numbers = []
        for source_record in source_data:
            # Extract address number from the record
            address_number = source_record.get("AdrNr", "")

            # Add address_number to the record for prefiltering
            source_record["_address_number"] = address_number
            records_with_address_numbers.append(source_record)

        # Prefilter records based on existing address numbers
        valid_records, invalid_records = self.prefilter_records(
            records_with_address_numbers,
            existing_keys=existing_address_numbers,
            key_field="_address_number",
        )

        if invalid_records:
            logger.info(
                f"Skipping {len(invalid_records)} addresses with "
                f"non-existent address numbers"
            )
            for record in invalid_records:
                logger.warning(
                    f"Address not found for number: "
                    f"{record.get('_address_number', 'unknown')}"
                )

        # Process only records with valid address numbers
        for source_record in valid_records:
            try:
                # Apply basic field mappings
                record = self.apply_field_mappings(source_record)

                # Add address_number field
                record["address_number"] = source_record.get("AdrNr", "")

                # Look up customer by address_number
                customer_found = False
                if Customer and "address_number" in record:
                    try:
                        # Match on legacy_address_number
                        lookup_value = record["address_number"]
                        logger.info(
                            "Looking up customer with " "legacy_address_number: %s",
                            lookup_value,
                        )
                        customer = Customer.objects.get(
                            legacy_address_number=lookup_value
                        )
                        # Set customer foreign key relationship
                        record["customer"] = customer
                        customer_found = True
                        logger.info(
                            "Found customer: %s (customer_number: %s) "
                            "for address: %s",
                            customer.id,
                            customer.customer_number,
                            lookup_value,
                        )
                    except Customer.DoesNotExist:
                        logger.error(
                            "No customer found with legacy_address_number: %s",
                            lookup_value,
                        )
                    except Exception as e:
                        extra = {
                            "address_number": record["address_number"],
                            "error_type": type(e).__name__,
                        }
                        logger.error(
                            "Error looking up customer: %s", str(e), extra=extra
                        )

                # Skip records without a valid customer
                if not customer_found:
                    continue

                # Clean up country code
                if "country" in record:
                    record["country"] = self._clean_country_code(record["country"])

                # Clean up email
                if "email" in record:
                    record["email"] = self._clean_email(record["email"])

                # Set synchronization fields
                record["is_synchronized"] = True
                record["legacy_modified"] = self._parse_legacy_timestamp(
                    source_record.get("__TIMESTAMP")
                )

                # Apply any custom transformations
                record = self.apply_custom_transformers(record, source_record)

                transformed_records.append(record)

            except Exception as e:
                logger.error(
                    f"Failed to transform address record: {e}",
                    extra={"record": source_record},
                )
                continue

        return transformed_records

    def _parse_legacy_timestamp(self, timestamp_str: str) -> datetime:
        """Parse legacy system timestamp into datetime object.

        Args:
            timestamp_str: Timestamp string from legacy system

        Returns:
            Parsed datetime or current time if parsing fails
        """
        if not timestamp_str:
            return timezone.now()

        try:
            # Legacy timestamps are in format: "2025-03-06T04:13:17.687Z"
            dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            # Use UTC timezone
            return dt.replace(tzinfo=ZoneInfo("UTC"))
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse legacy timestamp: {timestamp_str}")
            return timezone.now()

    def _clean_country_code(self, country: str) -> str:
        """Clean and validate country code.

        Args:
            country: Raw country code from legacy system

        Returns:
            Cleaned 2-letter country code or empty string
        """
        if not country:
            return ""

        # Convert to uppercase and strip whitespace
        code = country.strip().upper()

        # Validate it's a 2-letter code
        if len(code) == 2 and code.isalpha():
            return code

        # Map common variations
        country_map = {
            "DEU": "DE",
            "GER": "DE",
            "DEUTSCHLAND": "DE",
            "GERMANY": "DE",
            "AUT": "AT",
            "AUSTRIA": "AT",
            "ÖSTERREICH": "AT",
            "CHE": "CH",
            "SWITZERLAND": "CH",
            "SCHWEIZ": "CH",
        }
        return country_map.get(code, "")

    def _clean_email(self, email: str) -> str:
        """Clean and validate email address.

        Args:
            email: Raw email from legacy system

        Returns:
            Cleaned email address or empty string
        """
        if not email:
            return ""

        # Strip whitespace and convert to lowercase
        email = email.strip().lower()

        # Basic validation - must contain @ and at least one dot after @
        if "@" in email and "." in email.split("@")[1]:
            return email

        return ""
