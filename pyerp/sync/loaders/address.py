"""Load address data into the Address model."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from pyerp.business_modules.sales.models import Address, Customer
from .base import BaseLoader


logger = logging.getLogger(__name__)


class AddressLoader(BaseLoader):
    """Loads transformed address data into the Address model."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.
        
        Returns:
            List of required field names
        """
        return []  # No required config for basic address loading

    def prepare_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare an address record for loading.
        
        Args:
            record: Transformed address record
            
        Returns:
            Tuple of (lookup criteria, prepared record)
        """
        # Extract lookup fields
        lookup = {}
        if "legacy_id" in record:
            lookup["legacy_id"] = record["legacy_id"]

        # Remove any None values from lookup
        lookup = {k: v for k, v in lookup.items() if v is not None}

        # Prepare record for create/update
        prepared = record.copy()

        # Remove any fields that shouldn't be passed to create/update
        for field in ["created_at", "modified_at"]:
            prepared.pop(field, None)

        return lookup, prepared

    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True
    ) -> Optional[Address]:
        """Load a single address record.
        
        Args:
            lookup_criteria: Fields to use for finding existing record
            record: Prepared record data
            update_existing: Whether to update existing records
            
        Returns:
            Created or updated Address instance, or None if skipped
            
        Raises:
            Exception: If create/update fails
        """
        try:
            with transaction.atomic():
                # Try to find existing record
                existing = None
                if lookup_criteria:
                    try:
                        existing = Address.objects.get(**lookup_criteria)
                    except Address.DoesNotExist:
                        pass
                    except Address.MultipleObjectsReturned:
                        # Log warning and use first match
                        logger.warning(
                            "Multiple addresses found for criteria",
                            extra={
                                "lookup": lookup_criteria,
                                "record": record
                            }
                        )
                        existing = Address.objects.filter(
                            **lookup_criteria
                        ).first()

                if existing and not update_existing:
                    return None

                # Get or create customer if customer_number is provided
                customer = None
                customer_number = record.pop("customer_number", None)
                if customer_number:
                    try:
                        customer = Customer.objects.get(
                            customer_number=customer_number
                        )
                        record["customer"] = customer
                    except Customer.DoesNotExist:
                        logger.error(
                            "Customer not found for address",
                            extra={
                                "customer_number": customer_number,
                                "record": record
                            }
                        )
                        raise ValueError(
                            f"Customer not found: {customer_number}"
                        )

                if existing:
                    # Update existing record
                    for key, value in record.items():
                        setattr(existing, key, value)
                    existing.save()
                    return existing
                else:
                    # Create new record
                    return Address.objects.create(**record)

        except Exception as e:
            logger.error(
                "Failed to load address record",
                extra={
                    "lookup": lookup_criteria,
                    "record": record,
                    "error": str(e)
                }
            )
            raise 