"""
Extractors for fetching data from BuchhaltungsButler API.
"""

from pyerp.external_api.buchhaltungsbutler import BuchhaltungsButlerClient
from pyerp.sync.extractors.base import BaseExtractor
from pyerp.utils.logging import get_logger
from typing import List, Optional, Dict, Any

logger = get_logger(__name__)

class BuchhaltungsButlerPostingAccountExtractor(BaseExtractor):
    """
    Extracts posting accounts from the BuchhaltungsButler API.
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
        Fetches all posting accounts from the API using the client's pagination helper.

        Args:
            query_params: Optional parameters (not used by this extractor).
            fail_on_filter_error: Whether to fail if filter query fails (not used).

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a 
                                  posting account.
        """
        # Log if query_params are provided but unused
        if query_params:
            logger.warning("query_params provided but not used by BuchhaltungsButlerPostingAccountExtractor: %s", query_params)
        if fail_on_filter_error:
            logger.warning("fail_on_filter_error=True provided but not used by BuchhaltungsButlerPostingAccountExtractor.")
            
        try:
            logger.info(
                "Starting extraction of BuchhaltungsButler posting accounts..."
            )
            # Use the client method to fetch all accounts with pagination handled
            all_accounts = self.client.get_all_posting_accounts(
                limit=self.page_size
            )
            logger.info(
                "Successfully fetched %d posting accounts.", len(all_accounts)
            )
            
            # Return the list directly, not yield
            return all_accounts

        except Exception as e:
            logger.error(
                "Error during BuchhaltungsButler posting account extraction: %s",
                e,
                exc_info=True
            )
            # Decide on error handling: re-raise, return empty list, or custom exception?
            # Re-raising allows Celery retry mechanisms to work.
            raise 