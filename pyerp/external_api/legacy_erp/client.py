"""
Main API client for interacting with the legacy 4D-based ERP system.

This module provides the LegacyERPClient class which handles all interactions
with the legacy API, including data retrieval and updates.
"""

from typing import Optional, Dict, Any

import pandas as pd

from pyerp.external_api.legacy_erp.base import BaseAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError
from pyerp.external_api import connection_manager
from pyerp.utils.logging import get_logger

# Configure logging using the centralized logging system
logger = get_logger(__name__)


class LegacyERPClient(BaseAPIClient):
    """
    Client for directly interacting with the legacy 4D-based ERP system.

    This class provides methods for fetching data from and pushing data to
    the legacy system, handling authentication and error handling.
    """

    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new client instance.

        Args:
            environment: Which API environment to use ('live', 'test', etc.)
            timeout: Optional custom timeout for API requests (in seconds)
        """
        super().__init__(environment=environment, timeout=timeout)

    def check_connection(self) -> bool:
        """
        Check if the connection to the legacy ERP API is working.

        This method is used by the health check system to verify
        that the API is accessible and responding correctly.

        Returns:
            bool: True if connection is successful, False otherwise

        Raises:
            LegacyERPError: If an unexpected error occurs during validation
        """
        try:
            logger.info("Checking connection to legacy ERP API")

            # First check if the connection is enabled
            if not connection_manager.is_connection_enabled("legacy_erp"):
                logger.info("Legacy ERP API connection is disabled")
                return False

            return self.validate_session()
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            raise LegacyERPError(f"Failed to check connection: {e}")

    def fetch_table(
        self,
        table_name: str,
        top: Optional[int] = None,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system.

        Args:
            table_name: Name of the table to fetch from
            top: Number of records to fetch per request (None for no limit,
                though the API server may still apply a default limit,
                typically 100 records)
            skip: Number of records to skip
            filter_query: [['field', 'operator', 'value']]
            all_records: Whether to fetch all records (may take a long time)
            new_data_only: Only fetch records newer than last sync
            date_created_start: Optional start date for filtering
            fail_on_filter_error: Whether to raise an error on filter issues

        Returns:
            DataFrame containing the fetched records

        Raises:
            LegacyERPError: If an error occurs during the API request
        """
        try:
            return super().fetch_table(
                table_name=table_name,
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                new_data_only=new_data_only,
                date_created_start=date_created_start,
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            raise LegacyERPError(f"Failed to fetch table: {e}")

    def fetch_product(self, product_sku: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single product by SKU.

        Args:
            product_sku: The product SKU to fetch

        Returns:
            Dictionary containing the product data or None if not found

        Raises:
            LegacyERPError: If an error occurs during the API request
        """
        logger.info(f"Fetching product with SKU: {product_sku}")
        try:
            # Define filter query for the specific product
            filter_query = [["Nummer", "=", product_sku]]
            
            # Fetch from the products table
            products_df = self.fetch_table(
                table_name="Artikel",
                filter_query=filter_query,
                top=1,  # We only need one matching record
            )
            
            if products_df.empty:
                logger.warning(f"No product found with SKU: {product_sku}")
                return None
            
            # Convert first row to dictionary and return
            return products_df.iloc[0].to_dict()
        
        except Exception as e:
            error_msg = f"Failed to fetch product with SKU {product_sku}: {e}"
            logger.error(error_msg)
            raise LegacyERPError(error_msg)

    def fetch_product_variants(self, parent_sku: str) -> pd.DataFrame:
        """
        Fetch all variants for a parent product.
        
        Args:
            parent_sku: The parent product SKU
            
        Returns:
            DataFrame containing the variant products
            
        Raises:
            LegacyERPError: If an error occurs during the API request
        """
        logger.info(f"Fetching variants for parent product: {parent_sku}")
        try:
            # Define filter query for variants of this parent
            filter_query = [["ParentArtikel", "=", parent_sku]]
            
            # Fetch variants from the products table
            variants_df = self.fetch_table(
                table_name="Artikel",
                filter_query=filter_query,
                all_records=True,  # Ensure all variants are fetched
            )
            
            logger.info(
                f"Found {len(variants_df)} variants for parent {parent_sku}"
            )
            return variants_df
            
        except Exception as e:
            error_msg = (
                f"Failed to fetch variants for parent {parent_sku}: {e}"
            )
            logger.error(error_msg)
            raise LegacyERPError(error_msg)

    def fetch_product_inventory(self, product_sku: str = None) -> pd.DataFrame:
        """
        Fetch inventory data for products.
        
        Args:
            product_sku: Optional specific product SKU to fetch inventory for
            
        Returns:
            DataFrame containing inventory data
            
        Raises:
            LegacyERPError: If an error occurs during the API request
        """
        logger.info(
            f"Fetching inventory data "
            f"{f'for SKU: {product_sku}' if product_sku else ''}"
        )
        try:
            # Define filter query if a specific product is requested
            filter_query = None
            if product_sku:
                filter_query = [["ArtikelNr", "=", product_sku]]
            
            # Fetch from the inventory table
            inventory_df = self.fetch_table(
                table_name="Lagerbestand",
                filter_query=filter_query,
            )
            
            logger.info(f"Found {len(inventory_df)} inventory records")
            return inventory_df
            
        except Exception as e:
            error_msg = f"Failed to fetch inventory data: {e}"
            logger.error(error_msg)
            raise LegacyERPError(error_msg)

    def fetch_molds(
        self,
        top: Optional[int] = None,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from the 'Formen' (Molds) table in the legacy ERP system.

        Args:
            top: Number of records to fetch per request (None for no limit).
            skip: Number of records to skip.
            filter_query: Optional filter query list (e.g., [['field', 'op', 'value']]).
            all_records: Whether to fetch all records, handling pagination.
            new_data_only: Only fetch records newer than last sync timestamp.
            date_created_start: Optional start date for filtering.
            fail_on_filter_error: Whether to raise an error on filter issues.

        Returns:
            DataFrame containing the fetched mold records.

        Raises:
            LegacyERPError: If an error occurs during the API request.
        """
        logger.info("Fetching molds (Formen) data.")
        try:
            return self.fetch_table(
                table_name="Formen",
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                new_data_only=new_data_only,
                date_created_start=date_created_start,
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            error_msg = f"Failed to fetch molds data: {e}"
            logger.error(error_msg)
            raise LegacyERPError(error_msg)

    def fetch_mold_articles(
        self,
        top: Optional[int] = None,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from the 'Form_Artikel' (Mold Articles) table.

        This table links molds (Formen) to articles/products (Artikel).

        Args:
            top: Number of records to fetch per request (None for no limit).
            skip: Number of records to skip.
            filter_query: Optional filter query list.
            all_records: Whether to fetch all records, handling pagination.
            new_data_only: Only fetch records newer than last sync timestamp.
            date_created_start: Optional start date for filtering.
            fail_on_filter_error: Whether to raise an error on filter issues.

        Returns:
            DataFrame containing the fetched mold article records.

        Raises:
            LegacyERPError: If an error occurs during the API request.
        """
        logger.info("Fetching mold articles (Form_Artikel) data.")
        try:
            return self.fetch_table(
                table_name="Form_Artikel",
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                new_data_only=new_data_only,
                date_created_start=date_created_start,
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            error_msg = f"Failed to fetch mold articles data: {e}"
            logger.error(error_msg)
            raise LegacyERPError(error_msg)


if __name__ == "__main__":
    # Reverted: Remove test code from main block
    pd.set_option("display.max_columns", None)
    # pd.set_option('display.max_rows', 10)
    # pd.set_option('display.width', 1000)

    client = LegacyERPClient(environment="live")

    # Original example code (can be kept or removed)
    form_artikel = client.fetch_table(
        table_name="Artikel_Variante",
        top=10  # Just get a sample
    )
    print(form_artikel.tail())


    