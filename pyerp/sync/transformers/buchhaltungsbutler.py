"""
Transformers for mapping BuchhaltungsButler data to pyERP models.
"""

from pyerp.sync.transformers.base import BaseTransformer
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)

class BuchhaltungsButlerPostingAccountTransformer(BaseTransformer):
    """
    Transforms BuchhaltungsButler posting account data into the format
    expected by the pyERP Supplier model loader.
    
    Maps:
    - postingaccount_number -> creditor_id
    - name -> name
    """

    def transform(self, data: dict):
        """
        Transforms a single posting account dictionary.

        Args:
            data: A dictionary representing a posting account from the API.

        Returns:
            dict: A dictionary formatted for the Supplier loader, or None if 
                  mapping fails.
        """
        if not isinstance(data, dict):
            logger.warning("Transformer received non-dict data: %s", type(data))
            return None

        # Filter by type: Only process creditors
        account_type = data.get('type')
        if account_type != 'creditor':
            logger.debug(
                "Skipping posting account ID %s (type: '%s') - Not a creditor.",
                data.get('postingaccount_id'), # Use postingaccount_id if available for logging
                account_type
            )
            return None

        posting_account_number = data.get('postingaccount_number')
        name = data.get('name')
        
        # Minimal validation: require both fields
        if not posting_account_number or not name:
            logger.warning(
                "Skipping posting account due to missing number or name: %s", 
                data
            )
            return None
        
        transformed_data = {
            # Ensure creditor_id is a string
            'creditor_id': str(posting_account_number),  
            'name': name,
            # Add other default/optional fields for Supplier model if needed
            # e.g., 'synced_at': datetime.now(timezone.utc) could be added 
            # here or in loader
        }
        
        # logger.debug("Transformed %s -> %s", data, transformed_data)
        return transformed_data 