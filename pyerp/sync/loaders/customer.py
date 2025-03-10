"""Load customer data into the Customer model."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from pyerp.business_modules.sales.models import Customer
from .base import BaseLoader


logger = logging.getLogger(__name__)


class CustomerLoader(BaseLoader):
    """Loads transformed customer data into the Customer model."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.
        
        Returns:
            List of required field names
        """
        return []  # No required config for basic customer loading

    def prepare_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare a customer record for loading.
        
        Args:
            record: Transformed customer record
            
        Returns:
            Tuple of (lookup criteria, prepared record)
        """
        # Extract lookup fields
        lookup = {}
        if "legacy_id" in record:
            lookup["legacy_id"] = record["legacy_id"]
        if "customer_number" in record:
            lookup["customer_number"] = record["customer_number"]

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
    ) -> Optional[Customer]:
        """Load a single customer record.
        
        Args:
            lookup_criteria: Fields to use for finding existing record
            record: Prepared record data
            update_existing: Whether to update existing records
            
        Returns:
            Created or updated Customer instance, or None if skipped
            
        Raises:
            Exception: If create/update fails
        """
        try:
            with transaction.atomic():
                # Try to find existing record
                existing = None
                if lookup_criteria:
                    try:
                        existing = Customer.objects.get(**lookup_criteria)
                    except Customer.DoesNotExist:
                        pass
                    except Customer.MultipleObjectsReturned:
                        # Log warning and use first match
                        logger.warning(
                            "Multiple customers found for criteria",
                            extra={
                                "lookup": lookup_criteria,
                                "record": record
                            }
                        )
                        existing = Customer.objects.filter(
                            **lookup_criteria
                        ).first()

                if existing and not update_existing:
                    return None

                if existing:
                    # Update existing record
                    for key, value in record.items():
                        setattr(existing, key, value)
                    existing.save()
                    return existing
                else:
                    # Create new record
                    return Customer.objects.create(**record)

        except Exception as e:
            logger.error(
                "Failed to load customer record",
                extra={
                    "lookup": lookup_criteria,
                    "record": record,
                    "error": str(e)
                }
            )
            raise 