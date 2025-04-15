"""
Loaders for the Sales business module.
"""
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation

from django.utils.dateparse import parse_date
from django.db import transaction

from pyerp.business_modules.sales.models import SalesRecord
from pyerp.sync.loaders.base import BaseLoader
from pyerp.sync.exceptions import LoadError, ConfigurationError

logger = logging.getLogger(__name__)

class SalesRecordStatusLoader(BaseLoader):
    """
    Loads payment status updates from external receipts (e.g., BuchhaltungsButler)
    into the SalesRecord model.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.model = SalesRecord
        # Configuration for mapping API fields to model fields (optional)
        self.field_mapping = self.config.get('field_mapping', {})
        self.invoice_number_field = self.field_mapping.get('invoice_number', 'invoicenumber') # API field
        self.amount_field = self.field_mapping.get('amount', 'amount') # API field
        self.amount_paid_field = self.field_mapping.get('amount_paid', 'amount_paid') # API field
        self.payment_date_field = self.field_mapping.get('payment_date', 'payment_date') # API field

        # Model fields to update
        self.model_invoice_field = "record_number"
        self.model_status_field = "payment_status"
        self.model_payment_date_field = "payment_date"

        # Status values in the SalesRecord model
        self.status_paid = "PAID"
        self.status_pending = "PENDING"
        # Potentially map other statuses if needed, e.g., partially paid
        # self.status_partial = "PARTIAL" # If you add this to SalesRecord choices

    def get_required_config_fields(self) -> List[str]:
        """Returns a list of required configuration fields."""
        # No specific config required beyond optional field_mapping
        return []

    def validate_data(self, data: List[Dict[str, Any]]) -> None:
        """Performs basic validation on the incoming list of receipt dicts."""
        if not isinstance(data, list):
            raise TypeError("Input data must be a list of dictionaries.")
        
        required_keys = [self.invoice_number_field, self.amount_field, self.amount_paid_field]
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                 raise TypeError(f"Item at index {i} must be a dictionary.")
            for key in required_keys:
                 if key not in item:
                      raise ValueError(f"Missing required key '{key}' in item at index {i}: {item}")


    def load(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Loads the extracted receipt data into the SalesRecord model, updating
        payment status and date.

        Args:
            data: A list of dictionaries, where each dictionary represents a
                  receipt from the API. Expected keys: 'invoicenumber', 'amount',
                  'amount_paid', 'payment_date'.

        Returns:
            Dict[str, int]: A dictionary containing counts of processed,
                            updated, skipped, and failed records.
        """
        self.validate_data(data)
        logger.info(f"Starting load process for {len(data)} receipts into {self.model.__name__}.")

        processed_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        
        records_to_update = []
        record_update_map = {} # Store updates keyed by pk for bulk_update

        # Fetch relevant SalesRecords in bulk to minimize DB queries
        invoice_numbers = [item.get(self.invoice_number_field) for item in data if item.get(self.invoice_number_field)]
        logger.debug(f"Looking for SalesRecords with record_numbers: {invoice_numbers[:10]}...") # Log first 10
        
        # Only look for INVOICE type records
        existing_records = self.model.objects.filter(
            record_number__in=invoice_numbers,
            record_type='INVOICE' # Ensure we only match invoices
        ).in_bulk(field_name='record_number') # Use in_bulk for efficient lookup by invoice number

        logger.info(f"Found {len(existing_records)} existing INVOICE SalesRecords matching the received receipt numbers.")

        for item in data:
            processed_count += 1
            invoice_number = item.get(self.invoice_number_field)

            if not invoice_number:
                 logger.warning(f"Skipping item due to missing invoice number: {item}")
                 skipped_count += 1
                 continue

            # Check if we found a matching SalesRecord (Invoice)
            sales_record = existing_records.get(invoice_number)

            if not sales_record:
                 logger.debug(f"Skipping receipt - No matching INVOICE SalesRecord found for record_number '{invoice_number}'.")
                 skipped_count += 1
                 continue

            try:
                 # Extract and convert amounts safely
                 try:
                      # API amounts might be negative for credit notes, handle appropriately
                      # For standard invoices, we expect positive values typically
                      amount_str = item.get(self.amount_field, '0')
                      amount = abs(Decimal(amount_str)) # Use absolute value for comparison? Or check record_type? Assuming positive amount needed.
                 except (InvalidOperation, TypeError, ValueError) as e:
                      logger.warning(f"Invalid amount '{amount_str}' for invoice {invoice_number}. Skipping update. Error: {e}")
                      skipped_count += 1
                      continue

                 try:
                      amount_paid_str = item.get(self.amount_paid_field, '0')
                      amount_paid = abs(Decimal(amount_paid_str)) # Use absolute value
                 except (InvalidOperation, TypeError, ValueError) as e:
                      logger.warning(f"Invalid amount_paid '{amount_paid_str}' for invoice {invoice_number}. Skipping update. Error: {e}")
                      skipped_count += 1
                      continue

                 # Determine new status
                 new_status = self.status_pending
                 new_payment_date = sales_record.payment_date # Keep existing unless fully paid

                 # Use a small tolerance for floating point comparisons
                 tolerance = Decimal('0.01') 
                 if amount_paid >= (amount - tolerance):
                      new_status = self.status_paid
                      # Update payment date only if newly marked as paid
                      api_payment_date_str = item.get(self.payment_date_field)
                      if api_payment_date_str:
                           parsed_date = parse_date(api_payment_date_str)
                           if parsed_date:
                                new_payment_date = parsed_date
                           else:
                                logger.warning(f"Could not parse payment_date '{api_payment_date_str}' for invoice {invoice_number}.")
                 # Optional: Handle partially paid status if added to the model
                 # elif amount_paid > tolerance:
                 #     new_status = self.status_partial # Requires PARTIAL in choices

                 # Check if update is needed
                 status_changed = sales_record.payment_status != new_status
                 date_changed = sales_record.payment_date != new_payment_date and new_payment_date is not None
                 
                 if status_changed or date_changed:
                      logger.debug(f"Updating SalesRecord {sales_record.pk} (Invoice: {invoice_number}): Status '{sales_record.payment_status}' -> '{new_status}', Payment Date '{sales_record.payment_date}' -> '{new_payment_date}'")
                      sales_record.payment_status = new_status
                      sales_record.payment_date = new_payment_date
                      # Add to list for bulk update
                      # Avoid adding the same record multiple times if it appears >1 in source data
                      if sales_record.pk not in record_update_map:
                           records_to_update.append(sales_record)
                           record_update_map[sales_record.pk] = sales_record # Track updates
                      else:
                           # If record already marked for update, ensure we keep the latest parsed status/date?
                           # Current logic takes the status from the *first* occurrence in the data.
                           # If multiple receipts could apply to one invoice, this logic might need refinement.
                           logger.debug(f"Record {sales_record.pk} already queued for update.")
                           # Update the instance in the list/map if necessary based on latest data?
                           # For now, we just update the first time we see it.
                           pass 
                 else:
                      logger.debug(f"Skipping SalesRecord {sales_record.pk} (Invoice: {invoice_number}): No change in status or payment date.")
                      skipped_count += 1

            except Exception as e:
                 logger.error(f"Failed to process update for SalesRecord with record_number '{invoice_number}'. Error: {e}", exc_info=True)
                 failed_count += 1


        # Perform bulk update outside the loop
        if records_to_update:
            try:
                 with transaction.atomic():
                      updated_rows = self.model.objects.bulk_update(
                           records_to_update,
                           [self.model_status_field, self.model_payment_date_field]
                      )
                      updated_count = len(records_to_update) # bulk_update returns None in some Django<4 versions
                      logger.info(f"Successfully bulk updated {updated_count} {self.model.__name__} records.")
            except Exception as e:
                 failed_count += len(records_to_update) # Assume all failed in bulk
                 updated_count = 0 # Reset updated count as the transaction failed
                 logger.error(f"Bulk update failed for {self.model.__name__}: {e}", exc_info=True)
                 # Optionally re-raise or handle specific DB errors
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