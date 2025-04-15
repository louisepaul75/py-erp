"""
Loaders for the Sales business module.
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from django.utils.dateparse import parse_date
from django.db import transaction

from pyerp.business_modules.sales.models import SalesRecord
from pyerp.sync.loaders.base import BaseLoader
from pyerp.sync.exceptions import LoadError

logger = logging.getLogger(__name__)

TWO_PLACES = Decimal("0.01")

class SalesRecordStatusLoader(BaseLoader):
    """
    Loads payment status updates from external receipts (e.g., BuchhaltungsButler)
    into the SalesRecord model, matching based on filename and record_number.
    Updates payment status based on amount paid with tolerance.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = SalesRecord
        # Configuration for mapping API fields to model fields
        self.field_mapping = self.config.get('field_mapping', {})
        # Use invoicenumber from API to match record_number in DB
        self.api_match_field = self.field_mapping.get('api_match_field', 'invoicenumber')
        # API field for the amount paid
        self.api_amount_paid_field = self.field_mapping.get('api_amount_paid', 'amount_paid')
        # API field for the payment date
        self.api_payment_date_field = self.field_mapping.get('api_payment_date', 'payment_date')

        # Model fields to update
        self.model_match_field = "record_number"
        self.model_total_amount_field = "total_amount"
        self.model_status_field = "payment_status"
        self.model_payment_date_field = "payment_date"
        self.model_amount_paid_external_field = "amount_paid_external"

        # Status values in the SalesRecord model
        self.status_paid = "PAID"
        self.status_pending = "PENDING"
        self.status_overdue = "OVERDUE" # Assuming OVERDUE exists
        # Tolerance for payment amount matching (e.g., 2%)
        self.payment_tolerance_percent = Decimal(self.config.get('payment_tolerance_percent', '2.0'))

    def get_required_config_fields(self) -> List[str]:
        """Returns a list of required configuration fields."""
        # Optional config: field_mapping, payment_tolerance_percent
        return []

    def validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Performs basic validation on the incoming list of receipt dicts."""
        if not isinstance(data, list):
            raise TypeError("Input data must be a list of dictionaries.")

        # Required keys based on the fields we use
        required_keys = [
            self.api_match_field,
            self.api_amount_paid_field,
            # payment_date is optional for update, but good practice to require if available
            # self.api_payment_date_field
        ]
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise TypeError(f"Item at index {i} must be a dictionary.")
            for key in required_keys:
                # Check if the key exists, even if value is None/empty
                if key not in item:
                    raise ValueError(
                        f"Missing required key '{key}' in item at index {i}: "
                        f"{item}"
                    )

    def _clean_api_match_key(self, raw_key: Optional[str]) -> Optional[str]:
        """Clean the API matching key (e.g., invoice number)."""
        if not raw_key:
            return None
        
        # 1. Remove leading 'R' if present (case-insensitive)
        cleaned_key = re.sub(r'^[rR]', '', str(raw_key))
        
        # 2. Remove soft hyphens (\xad) and keep only alphanumeric and hyphens
        # This removes other potential special characters
        cleaned_key = cleaned_key.replace('\xad', '') 
        cleaned_key = re.sub(r'[^a-zA-Z0-9-]', '', cleaned_key)
        
        # 3. Optional: Add more cleaning steps if needed (e.g., strip whitespace)
        cleaned_key = cleaned_key.strip()

        return cleaned_key

    # Add placeholder implementations for abstract methods
    def prepare_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder: Prepare a single record (Not used by this loader)."""
        # This method is required by the base class but not used
        # as we operate in bulk via the load() method.
        raise NotImplementedError("prepare_record is not implemented for this loader")

    def load_record(self, record: Dict[str, Any]) -> Any:
        """Placeholder: Load a single prepared record (Not used by this loader)."""
        # This method is required by the base class but not used
        # as we operate in bulk via the load() method.
        raise NotImplementedError("load_record is not implemented for this loader")

    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Loads the extracted receipt data into the SalesRecord model, updating
        payment status, payment date, and external amount paid based on
        matching filename to record_number.

        Args:
            data: A list of dictionaries, where each dictionary represents a
                  receipt from the API. Expected keys depend on config but
                  defaults are 'filename', 'amount_paid', 'payment_date'.

        Returns:
            Dict[str, int]: A dictionary containing counts of processed,
                            updated, skipped, and failed records.
        """
        self.validate_data(data)
        logger.info(f"Starting load process for {len(data)} external receipts into {self.model.__name__}.")

        processed_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0

        records_to_update = []
        record_update_map = {} # Store updates keyed by pk for bulk_update

        # Extract potential matching keys (e.g., invoice numbers) from API data
        # and clean them immediately.
        potential_keys = set()
        api_item_map = {}
        for item in data:
            raw_key = item.get(self.api_match_field)
            cleaned_key = self._clean_api_match_key(raw_key)
            if cleaned_key:
                potential_keys.add(cleaned_key)
                # Store the original item keyed by the cleaned key
                # If duplicates exist, the last one wins (or handle differently if needed)
                api_item_map[cleaned_key] = item 

        if not potential_keys:
            logger.warning("No valid, cleaned matching keys found in the input data. Skipping load.")
            return {"processed": len(data), "updated": 0, "skipped": len(data), "failed": 0}

        logger.debug(f"Looking for SalesRecords with {self.model_match_field} matching cleaned keys: {list(potential_keys)[:10]}...")

        # Fetch matching records using the cleaned keys
        matching_records_qs = self.model.objects.filter(
            **{f"{self.model_match_field}__in": list(potential_keys)}
        )
        # Build a dictionary for efficient lookup using the model's record_number
        existing_records = {getattr(r, self.model_match_field): r for r in matching_records_qs}

        logger.info(f"Found {len(existing_records)} existing SalesRecords matching the cleaned API identifiers.")

        # Iterate through the cleaned keys and their corresponding original API items
        for cleaned_key, item in api_item_map.items():
            processed_count += 1
            # Check if we found a matching SalesRecord using the cleaned key
            sales_record = existing_records.get(cleaned_key)

            if not sales_record:
                raw_key = item.get(self.api_match_field)
                logger.debug(f"Skipping receipt - No matching SalesRecord found for cleaned key '{cleaned_key}' (raw: '{raw_key}').")
                skipped_count += 1
                continue

            # Avoid processing already paid records unless forcing update?
            # if sales_record.payment_status == self.status_paid:
            #     logger.debug(f"Skipping already paid SalesRecord {sales_record.pk} ({match_key_value}).")
            #     skipped_count += 1
            #     continue

            try:
                # Extract and convert amounts safely
                try:
                    api_amount_paid_str = item.get(self.api_amount_paid_field, '0')
                    # API amount paid might be 0 or negative, handle appropriately
                    api_amount_paid = Decimal(api_amount_paid_str)
                except (InvalidOperation, TypeError, ValueError) as e:
                    logger.warning(
                        f"Invalid amount_paid '{api_amount_paid_str}' for "
                        f"cleaned key {cleaned_key}. Skipping update. Error: {e}"
                    )
                    skipped_count += 1
                    continue

                # Get total amount from the sales record
                record_total_amount = getattr(sales_record, self.model_total_amount_field, Decimal('0'))
                if record_total_amount is None: # Handle potential None in DB
                    record_total_amount = Decimal('0')

                # Determine new status based on tolerance
                new_status = sales_record.payment_status # Default to existing status
                new_payment_date = sales_record.payment_date # Keep existing unless updated
                update_needed = False

                # Calculate tolerance amount
                # Handle potentially zero total amount
                if record_total_amount != Decimal('0'):
                    tolerance_amount = abs(record_total_amount * (self.payment_tolerance_percent / Decimal('100'))).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
                else:
                    # If total is zero, only mark paid if amount paid is also near zero
                    tolerance_amount = TWO_PLACES # Use a small fixed tolerance for zero amounts


                lower_bound = record_total_amount - tolerance_amount
                upper_bound = record_total_amount + tolerance_amount

                # Check if amount paid falls within the tolerance range of the total amount
                if lower_bound <= api_amount_paid <= upper_bound:
                    if sales_record.payment_status != self.status_paid:
                        new_status = self.status_paid
                        logger.debug(
                            f"Record {sales_record.pk} (Matched on '{cleaned_key}') meets PAID criteria. "
                            f"Amount paid: {api_amount_paid}, Total: {record_total_amount}, Tolerance: +/- {tolerance_amount}"
                        )
                        update_needed = True
                # Optional: Logic for PENDING/OVERDUE based on due date if not paid
                # elif new_status != self.status_paid and sales_record.due_date and sales_record.due_date < timezone.now().date():
                #      new_status = self.status_overdue
                # else: # Otherwise, assume pending if not paid
                #      new_status = self.status_pending

                # Always update external amount paid if changed or not set
                if getattr(sales_record, self.model_amount_paid_external_field) != api_amount_paid:
                     setattr(sales_record, self.model_amount_paid_external_field, api_amount_paid)
                     update_needed = True
                     logger.debug(f"Record {sales_record.pk} (Matched on '{cleaned_key}'): Updating external amount paid to {api_amount_paid}")


                # Update payment date if status is now PAID or if API provides a date
                api_payment_date_str = item.get(self.api_payment_date_field)
                parsed_api_date = None
                if api_payment_date_str:
                    parsed_api_date = parse_date(api_payment_date_str)
                    if not parsed_api_date:
                         logger.warning(
                             f"Could not parse payment_date '{api_payment_date_str}' for cleaned key {cleaned_key}."
                         )

                # Update model's payment date if status is PAID and we have a valid API date
                if new_status == self.status_paid and parsed_api_date:
                     if sales_record.payment_date != parsed_api_date:
                          new_payment_date = parsed_api_date
                          update_needed = True
                          logger.debug(
                              f"Record {sales_record.pk} (Matched on '{cleaned_key}'): Updating payment date to {new_payment_date}"
                          )

                # Set the new status if it changed
                if sales_record.payment_status != new_status:
                    sales_record.payment_status = new_status
                    # update_needed flag already set above if status changes to PAID

                # Add to bulk update list if any changes were made
                if update_needed:
                    if sales_record.pk not in record_update_map:
                        # Ensure payment date is set correctly on the instance before adding
                        sales_record.payment_date = new_payment_date
                        records_to_update.append(sales_record)
                        record_update_map[sales_record.pk] = sales_record
                        logger.info(
                            f"Queueing update for SalesRecord {sales_record.pk} (Matched on '{cleaned_key}'): "
                            f"Status='{sales_record.payment_status}', "
                            f"PaymentDate='{sales_record.payment_date}', "
                            f"AmountPaidExt='{getattr(sales_record, self.model_amount_paid_external_field)}'"
                        )
                    else:
                        # Handle potential duplicate updates if needed (e.g., merge logic)
                        logger.debug(f"Record {sales_record.pk} already queued for update.")
                else:
                    logger.debug(f"Skipping SalesRecord {sales_record.pk} (Matched on '{cleaned_key}'): No relevant change detected.")
                    skipped_count += 1


            except Exception as e:
                logger.error(f"Failed to process update for SalesRecord matched on cleaned key '{cleaned_key}'. Error: {e}", exc_info=True)
                failed_count += 1


        # Perform bulk update outside the loop
        if records_to_update:
            update_fields = [
                self.model_status_field,
                self.model_payment_date_field,
                self.model_amount_paid_external_field,
            ]
            try:
                with transaction.atomic():
                    # Note: Django < 4.0 bulk_update might return None
                    updated_pks = [r.pk for r in records_to_update]
                    self.model.objects.bulk_update(records_to_update, update_fields)
                    updated_count = len(updated_pks)
                    logger.info(f"Successfully bulk updated {updated_count} {self.model.__name__} records (PKs: {updated_pks[:10]}...).")
            except Exception as e:
                failed_count += len(records_to_update) # Assume all failed in bulk
                updated_count = 0 # Reset updated count as the transaction failed
                logger.error(f"Bulk update failed for {self.model.__name__}: {e}", exc_info=True)
                raise LoadError(f"Bulk update failed: {e}") from e
        else:
            logger.info("No SalesRecord records needed updating.")

        result = {
            "processed": processed_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "failed": failed_count,
        }
        logger.info(f"Load process finished. Results: {result}")
        return result 