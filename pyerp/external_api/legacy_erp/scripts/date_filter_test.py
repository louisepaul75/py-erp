"""
Date filter test script for the legacy ERP system.

This script demonstrates how to use date filtering with the legacy ERP API
client. It provides examples of filtering records by modified date.
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

# Import the proper client from the legacy_erp module
from pyerp.external_api.legacy_erp.simple_client import SimpleAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def test_date_filter(table_name="Kunden", days_ago=30, environment="live"):
    """
    Test date filtering by fetching records modified within the last N days.
    
    Args:
        table_name (str): Name of the table to query
        days_ago (int): Number of days to look back
        environment (str): API environment to use
    
    Returns:
        pandas.DataFrame: Filtered records
    """
    try:
        # Initialize API client using the proper SimpleAPIClient
        client = SimpleAPIClient(environment=environment)
        
        # Calculate the date threshold
        date_threshold = (
            datetime.now() - timedelta(days=days_ago)
        ).strftime("%Y-%m-%d")
        
        # Construct the filter query with the entire expression in quotes
        filter_query = f"'modified_date > \'{date_threshold}\''"
        logger.info(f"Using date filter: {filter_query}")
        
        # Fetch a sample without filter to verify connection
        df_full_sample = client.fetch_table(
            table_name=table_name,
            top=100,
        )
        print(df_full_sample.head())
        logger.info(f"Full sample size: {len(df_full_sample)}")
        logger.info(f"Full sample columns: {df_full_sample.columns}")

        # Fetch data with date filter
        df = client.fetch_table(
            table_name=table_name,
            top=1000,  # Limit results for testing
            filter_query=filter_query,
        )
        
        logger.info(
            f"Retrieved {len(df)} records modified after {date_threshold}"
        )
        return df
        
    except LegacyERPError as e:
        logger.error(f"Legacy ERP API error during date filter test: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during date filter test: {e}")
        raise


def main():
    """Main function to run the date filter test."""
    try:
        # Load environment variables from .env.dev
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        env_path = project_root / "config" / "env" / ".env.dev"
        print(f"Loading environment from: {env_path}")
        print(f"File exists: {env_path.exists()}")

        if not env_path.exists():
            raise FileNotFoundError(
                "Could not find .env.dev file. Expected location:\n"
                f"{env_path}\n"
                "Please ensure the file exists in the correct location."
            )

        load_dotenv(env_path)

        # Print loaded environment variables
        print("\nLoaded environment variables:")
        for key in os.environ:
            if key.startswith("LEGACY_ERP_API_"):
                # Mask the actual values for security
                value = os.getenv(key)
                print(f"{key}={value}")
        
        # Test with different time periods
        periods = [90]  # Try last 90 days
        
        for days in periods:
            print(f"\n=== Testing {days} day filter ===")
            try:
                df = test_date_filter(days_ago=days, environment="live")
                if not df.empty:
                    msg = f"\nFound {len(df)} records modified in last {days} days"
                    print(msg)
                    print("\nSample of retrieved data:")
                    pd.set_option('display.max_columns', None)
                    print(df.head())
                else:
                    print(f"No records found modified in the last {days} days")
            except Exception as e:
                print(f"Live environment failed: {e}")
                
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
