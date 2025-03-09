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
from typing import Optional

import pandas as pd
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class SimpleTestClient:
    """Simplified API client for testing date filters."""

    def __init__(self, environment: str = "live"):
        """Initialize with environment."""
        # Get base URL from environment
        env_var = f"LEGACY_ERP_API_{environment.upper()}"
        self.base_url = os.getenv(env_var)
        self.username = os.getenv("LEGACY_API_USERNAME")
        self.password = os.getenv("LEGACY_API_PASSWORD")
        
        if not self.base_url:
            available_envs = [
                key.replace("LEGACY_ERP_API_", "").lower()
                for key in os.environ
                if key.startswith("LEGACY_ERP_API_")
            ]
            raise ValueError(
                f"No URL found for environment '{environment}'. "
                f"Available environments: {available_envs}"
            )
            
        if not self.username or not self.password:
            raise ValueError(
                "Missing API credentials. Please set LEGACY_API_USERNAME "
                "and LEGACY_API_PASSWORD environment variables."
            )
            
        logger.info(f"Initialized API client with URL: {self.base_url}")
        self.session = requests.Session()
        # Set reasonable timeouts
        self.session.timeout = (5, 15)  # (connect timeout, read timeout)

    def fetch_table(
        self,
        table_name: str,
        top: int = 1000,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        new_data_only: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table with optional filtering.
        
        Args:
            table_name: Name of the table to query
            top: Maximum number of records to fetch
            filter_query: OData filter query string
            all_records: Whether to fetch all records
            new_data_only: Whether to only fetch new records
            
        Returns:
            DataFrame containing the fetched records
        """
        url = f"{self.base_url}/rest/{table_name}"
        base_url = f"{url}?$top={top}"
        
        if filter_query:
            url = f"{base_url}&$filter={filter_query}"
        else:
            url = base_url
            
        logger.info(f"Fetching from URL: {url}")
        
        try:
            logger.info("Attempting to connect to the API...")
            response = self.session.get(
                url,
                auth=(self.username, self.password),
                verify=False,  # Skip SSL verification for internal servers
            )
            logger.info(f"Connection established. Status code: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and "value" in data:
                records = data["value"]
            elif isinstance(data, list):
                records = data
            else:
                records = []
                
            df = pd.DataFrame(records)
            logger.info(f"Retrieved {len(df)} records")
            return df
            
        except requests.exceptions.SSLError:
            logger.warning("SSL verification failed, retrying without verification...")
            response = self.session.get(
                url,
                auth=(self.username, self.password),
                verify=False,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "value" in data:
                records = data["value"]
            elif isinstance(data, list):
                records = data
            else:
                records = []
            df = pd.DataFrame(records)
            logger.info(f"Retrieved {len(df)} records")
            return df
        except requests.exceptions.ConnectTimeout:
            logger.error(f"Connection timed out while trying to reach {url}")
            logger.error("Please check if the server is accessible and the network connection is stable")
            raise
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to {url}")
            logger.error("This could be due to:")
            logger.error("1. The server is not running")
            logger.error("2. The network is not properly configured")
            logger.error("3. You're not connected to the required network/VPN")
            logger.error(f"Detailed error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise


def test_date_filter(table_name="Kunden", days_ago=30, environment="test"):
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
        # Initialize API client
        client = SimpleTestClient(environment=environment)
        
        # Calculate the date threshold
        date_threshold = (
            datetime.now() - timedelta(days=days_ago)
        ).strftime("%Y-%m-%d")
        
        # Construct the filter query with plain symbols
        filter_query = f"modified_date > '{date_threshold}'"
        logger.info(f"Using date filter: {filter_query}")
        
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
