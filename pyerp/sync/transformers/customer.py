"""Transform customer data from legacy format to new model format."""

import logging
from datetime import datetime
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

from django.utils import timezone
from .base import BaseTransformer


logger = logging.getLogger(__name__)


class CustomerTransformer(BaseTransformer):
    """Transforms customer data from legacy Kunden format to Customer model."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with default field mappings for customers."""
        default_mappings = {
            "customer_number": "KundenNr",
            "legacy_address_number": "AdrNr",
            "customer_group": "Kundengr",
            "delivery_block": "Liefersperre",
            "price_group": "Preisgru",
            "vat_id": "USt_IdNr",
            "payment_method": "Zahlungsart",
            "shipping_method": "Versandart",
            "credit_limit": "Kreditlimit",
            "discount_percentage": "Rabatt",
            "payment_terms_discount_days": "SkontoTage",
            "payment_terms_net_days": "NettoTage",
            "legacy_id": "__KEY",
        }

        # Merge default mappings with any provided in config
        if "field_mappings" in config:
            default_mappings.update(config["field_mappings"])
        config["field_mappings"] = default_mappings

        super().__init__(config)

    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform customer records from legacy format.

        Args:
            source_data: List of customer records from legacy system

        Returns:
            List of transformed customer records
        """
        transformed_records = []

        for source_record in source_data:
            try:
                # Apply basic field mappings
                record = self.apply_field_mappings(source_record)

                # Convert boolean fields
                record["delivery_block"] = bool(record.get("delivery_block"))

                # Convert numeric fields
                if "credit_limit" in record:
                    try:
                        record["credit_limit"] = float(record["credit_limit"])
                    except (ValueError, TypeError):
                        record["credit_limit"] = None

                if "discount_percentage" in record:
                    try:
                        record["discount_percentage"] = float(
                            record["discount_percentage"]
                        )
                    except (ValueError, TypeError):
                        record["discount_percentage"] = None

                # Convert integer fields
                for field in ["payment_terms_discount_days", "payment_terms_net_days"]:
                    if field in record:
                        try:
                            record[field] = int(record[field])
                        except (ValueError, TypeError):
                            record[field] = None

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
                    f"Failed to transform customer record: {e}",
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
            # Use Europe/Berlin timezone (German time)
            german_tz = ZoneInfo("Europe/Berlin")
            return dt.replace(tzinfo=german_tz)
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Failed to parse legacy timestamp: {timestamp_str} - {str(e)}"
            )
            # Return current time in German timezone
            return timezone.now().astimezone(ZoneInfo("Europe/Berlin"))
