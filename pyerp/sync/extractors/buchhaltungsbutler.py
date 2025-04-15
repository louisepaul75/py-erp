"""
Extractors for fetching data from BuchhaltungsButler API.
"""

from pyerp.external_api.buchhaltungsbutler import BuchhaltungsButlerClient, BuchhaltungsButlerError
from pyerp.sync.extractors.base import BaseExtractor
from pyerp.utils.logging import get_logger
from typing import List, Optional, Dict, Any

logger = get_logger(__name__)

class BuchhaltungsButlerCreditorExtractor(BaseExtractor):
    """
    Extracts creditors from the BuchhaltungsButler API.
    Implements the abstract methods from BaseExtractor.
    """

    def __init__(self, config: dict):
        """
        Initializes the extractor with necessary configuration.

        Args:
            config: Configuration dictionary (can include API details 
                    if not global).
        """
        super().__init__(config)
        # Assumes client uses Django settings
        self.client = BuchhaltungsButlerClient()  
        # Configurable page size
        self.page_size = self.config.get('page_size', 500)  

    def get_required_config_fields(self) -> List[str]:
        """Returns a list of required configuration fields."""
        # API keys are handled globally by BuchhaltungsButlerClient via settings
        return [] # No specific config keys required here besides optional page_size

    def connect(self) -> None:
        """Establish connection to the data source (not needed for this client)."""
        # The BuchhaltungsButlerClient handles connection/auth per-request.
        logger.debug("Connect method called, but no explicit connection needed.")
        pass

    def extract(self, query_params: Optional[Dict[str, Any]] = None, fail_on_filter_error: bool = False) -> List[Dict[str, Any]]:
        """
        Fetches all creditors from the API using the client's pagination helper.

        Args:
            query_params: Optional parameters (not used by this extractor).
            fail_on_filter_error: Whether to fail if filter query fails (not used).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a 
                                  creditor.
        """
        # Log if query_params are provided but unused
        if query_params:
            logger.warning("query_params provided but not used by BuchhaltungsButlerCreditorExtractor: %s", query_params)
        if fail_on_filter_error:
            logger.warning("fail_on_filter_error=True provided but not used by BuchhaltungsButlerCreditorExtractor.")
            
        try:
            logger.info(
                "Starting extraction of BuchhaltungsButler creditors..."
            )
            # Use the client method to fetch all creditors with pagination handled
            all_creditors = self.client.get_all_creditors(
                limit=self.page_size
            )
            logger.info(
                "Successfully fetched %d creditors.", len(all_creditors)
            )
            
            # Return the list directly, not yield
            return all_creditors

        except BuchhaltungsButlerError as e: # Catch specific API errors
            logger.error(
                "BuchhaltungsButler API error during creditor extraction: %s",
                e,
                exc_info=True
            )
            raise # Re-raise API errors
        except Exception as e: # Catch other potential errors
            logger.error(
                "Unexpected error during BuchhaltungsButler creditor extraction: %s",
                e,
                exc_info=True
            )
            # Decide on error handling: re-raise, return empty list, or custom exception?
            # Re-raising allows Celery retry mechanisms to work.
            raise

class BuchhaltungsButlerReceiptExtractor(BaseExtractor):
    """
    Extracts 'inbound' receipts from the BuchhaltungsButler API to update
    SalesRecord payment status.
    Implements the abstract methods from BaseExtractor.
    """

    def __init__(self, config: dict):
        """
        Initializes the extractor with necessary configuration.

        Args:
            config: Configuration dictionary.
        """
        super().__init__(config)
        self.client = BuchhaltungsButlerClient()
        self.page_size = self.config.get('page_size', 500)
        # Direction is fixed for this use case, but could be configurable
        self.list_direction = "inbound"

    def get_required_config_fields(self) -> List[str]:
        """Returns a list of required configuration fields."""
        # API keys are handled globally by the client
        return []

    def connect(self) -> None:
        """Establish connection to the data source (not needed)."""
        logger.debug("Connect method called, but no explicit connection needed.")
        pass

    def extract(self, query_params: Optional[Dict[str, Any]] = None, fail_on_filter_error: bool = False) -> List[Dict[str, Any]]:
        """
        Fetches all 'inbound' receipts using the client's pagination helper.

        Args:
            query_params: Optional parameters (not used by this extractor).
            fail_on_filter_error: Whether to fail if filter query fails (not used).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an
                                  inbound receipt.
        """
        if query_params:
            logger.warning("query_params provided but not used by BuchhaltungsButlerReceiptExtractor: %s", query_params)
        if fail_on_filter_error:
            logger.warning("fail_on_filter_error=True provided but not used by BuchhaltungsButlerReceiptExtractor.")

        try:
            logger.info(
                "Starting extraction of BuchhaltungsButler \'%s\' receipts...",
                self.list_direction
            )
            # Use the client method to fetch all receipts with pagination handled
            all_receipts = self.client.get_all_receipts(
                list_direction=self.list_direction,
                limit=self.page_size
            )
            logger.info(
                "Successfully fetched %d \'%s\' receipts.",
                len(all_receipts), self.list_direction
            )

            return all_receipts

        except BuchhaltungsButlerError as e:
            logger.error(
                "BuchhaltungsButler API error during receipt extraction (%s): %s",
                self.list_direction, e, exc_info=True
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error during BuchhaltungsButler receipt extraction (%s): %s",
                self.list_direction, e, exc_info=True
            )
            raise 