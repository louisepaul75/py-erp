"""
Transformers for mapping BuchhaltungsButler data to pyERP models.
"""

from pyerp.sync.transformers.base import BaseTransformer
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)

class BuchhaltungsButlerCreditorTransformer(BaseTransformer):
    """
    Transforms BuchhaltungsButler creditor data into the format
    expected by the pyERP Supplier model loader.
    
    Maps:
    - postingaccount_number -> creditor_id
    - name -> name
    - email -> email
    - contact_person_name -> contact_person
    - street, zip, city, country, additional_addressline -> address
    """

    def transform(self, data: dict):
        """
        Transforms a single creditor dictionary.

        Args:
            data: A dictionary representing a creditor from the API.

        Returns:
            dict: A dictionary formatted for the Supplier loader, or None if 
                  mapping fails.
        """
        if not isinstance(data, dict):
            logger.warning("Transformer received non-dict data: %s", type(data))
            return None

        # Filter by type: Only process creditors (redundant but safe)
        account_type = data.get('type')
        if account_type != 'creditor':
            logger.debug(
                "Skipping record ID %s (type: '%s') - Not a creditor.",
                data.get('postingaccount_number'), 
                account_type
            )
            return None

        posting_account_number = data.get('postingaccount_number')
        name = data.get('name')
        
        # Minimal validation: require postingaccount_number and name
        if not posting_account_number or not name:
            logger.warning(
                "Skipping creditor due to missing postingaccount_number or name: %s", data
            )
            return None

        # Construct address string
        address_parts = [
            data.get('contact_person_name', ''),
            data.get('additional_addressline', ''),
            data.get('street', ''),
            f"{data.get('zip', '')} {data.get('city', '')}".strip(),
            data.get('country', '')
        ]
        # Filter out empty parts and join with newline
        address = "\n".join(part for part in address_parts if part and part.strip())
        
        transformed_data = {
            # Ensure creditor_id is a string
            'creditor_id': str(posting_account_number),  
            'name': name.strip() if name else None,
            'email': data.get('email', '').strip() or None,
            'contact_person': data.get('contact_person_name', '').strip() or None,
            'address': address or None, # Use the constructed address
            'iban': data.get('iban', '').strip() or None,
            'bic': data.get('bic', '').strip() or None,
            'accounting_id': data.get('customer_number'), # Map customer_number
            'tax_id': data.get('sales_tax_id_eu', '').strip() or None, # Map EU VAT ID
            # Add other default/optional fields for Supplier model if needed
        }
        
        # Remove keys with None values if desired, though Django handles them
        # transformed_data = {k: v for k, v in transformed_data.items() if v is not None}
        
        return transformed_data 