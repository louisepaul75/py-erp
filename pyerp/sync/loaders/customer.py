"""Load customer data into the Customer model."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import Q
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
        if "customer_number" in record:
            lookup["customer_number"] = record["customer_number"]
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
                # Try to find existing record by customer number first
                existing = None
                if "customer_number" in lookup_criteria:
                    try:
                        existing = Customer.objects.get(
                            customer_number=lookup_criteria["customer_number"]
                        )
                    except Customer.DoesNotExist:
                        pass

                # If not found by customer number, try legacy_id
                if not existing and "legacy_id" in lookup_criteria:
                    try:
                        existing = Customer.objects.get(
                            legacy_id=lookup_criteria["legacy_id"]
                        )
                    except Customer.DoesNotExist:
                        pass

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

    def load(
        self,
        records: List[Dict[str, Any]],
        update_existing: bool = True
    ) -> Dict[str, Any]:
        """Load records using bulk operations.
        
        Args:
            records: List of records to load
            update_existing: Whether to update existing records
            
        Returns:
            Dict with operation statistics
        """
        if not records:
            return {
                'created': 0, 'updated': 0, 'skipped': 0,
                'errors': 0, 'error_details': []
            }

        try:
            with transaction.atomic():
                # Prepare all records
                prepared_records = []
                lookup_values = {'customer_numbers': [], 'legacy_ids': []}
                
                for record in records:
                    lookup, prepared = self.prepare_record(record)
                    prepared_records.append((lookup, prepared))
                    if 'customer_number' in lookup:
                        lookup_values['customer_numbers'].append(
                            lookup['customer_number']
                        )
                    if 'legacy_id' in lookup:
                        lookup_values['legacy_ids'].append(lookup['legacy_id'])

                # Bulk fetch existing records
                existing_records = {}
                has_lookups = (lookup_values['customer_numbers'] or 
                             lookup_values['legacy_ids'])
                if has_lookups:
                    query = Q()
                    if lookup_values['customer_numbers']:
                        query |= Q(
                            customer_number__in=(
                                lookup_values['customer_numbers']
                            )
                        )
                    if lookup_values['legacy_ids']:
                        query |= Q(
                            legacy_id__in=lookup_values['legacy_ids']
                        )
                    
                    for existing in Customer.objects.filter(query):
                        if existing.customer_number:
                            existing_records[
                                ('customer_number', existing.customer_number)
                            ] = existing
                        if existing.legacy_id:
                            existing_records[
                                ('legacy_id', existing.legacy_id)
                            ] = existing

                # Separate records for create and update
                to_create = []
                to_update = []
                skipped = 0
                errors = []

                for lookup, record in prepared_records:
                    try:
                        existing = None
                        # Try to find by customer number first
                        if 'customer_number' in lookup:
                            existing = existing_records.get(
                                ('customer_number', lookup['customer_number'])
                            )
                        # Then try by legacy_id
                        if not existing and 'legacy_id' in lookup:
                            existing = existing_records.get(
                                ('legacy_id', lookup['legacy_id'])
                            )

                        if existing and not update_existing:
                            skipped += 1
                            continue

                        if existing:
                            # Update existing record
                            for key, value in record.items():
                                setattr(existing, key, value)
                            to_update.append(existing)
                        else:
                            # Create new record
                            to_create.append(Customer(**record))

                    except Exception as e:
                        errors.append({
                            'record': record,
                            'error': str(e),
                            'context': {'lookup': lookup}
                        })

                # Perform bulk operations
                created = len(Customer.objects.bulk_create(
                    to_create,
                    ignore_conflicts=True  # Skip records that would cause conflicts
                ))
                
                # Bulk update in chunks to avoid memory issues
                chunk_size = 1000
                updated = 0
                for i in range(0, len(to_update), chunk_size):
                    chunk = to_update[i:i + chunk_size]
                    update_fields = [
                        f.name for f in Customer._meta.fields 
                        if f.name not in ['id', 'created_at', 'modified_at']
                    ]
                    Customer.objects.bulk_update(chunk, fields=update_fields)
                    updated += len(chunk)

                result = {
                    'created': created,
                    'updated': updated,
                    'skipped': skipped,
                    'errors': len(errors),
                    'error_details': errors
                }

                # Log the operation summary
                logger.info(
                    "Bulk load completed",
                    extra={
                        'created': created,
                        'updated': updated,
                        'skipped': skipped,
                        'errors': len(errors)
                    }
                )

                return result

        except Exception as e:
            logger.error(
                "Failed to load customer records in bulk",
                extra={'error': str(e)}
            )
            raise 