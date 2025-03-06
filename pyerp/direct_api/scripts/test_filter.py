"""
test_filter.py - Test script for verifying the updated filtering implementation

This script tests various filter scenarios with the SimpleAPIClient to ensure
that the updated filtering implementation works correctly with the legacy ERP API.  # noqa: E501

Usage:
    python test_filter.py [options]

Options:
    --env ENV             Environment to use (default: live)
    --table TABLE         Table to test filters on (default: Artikel)
    --verbose             Enable verbose output
    --list-tables         List available tables in the legacy ERP system
"""

from pyerp.direct_api.scripts.getTable import SimpleAPIClient
import os
import sys
import argparse
import logging
from pathlib import Path

 # Add the parent directory to the path so we can import the getTable module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

 # Configure logging
logging.basicConfig(
    level=logging.INFO,  # noqa: E128
    format='%(asctime)s - %(levelname)s - %(message)s',  # noqa: F841
    handlers=[logging.StreamHandler(sys.stdout)]  # noqa: F841
)
logger = logging.getLogger(__name__)

 # Explicitly set environment variables for legacy ERP API URLs
os.environ['LEGACY_ERP_API_TEST'] = 'http://192.168.73.26:8090'
os.environ['LEGACY_ERP_API_LIVE'] = 'http://192.168.73.28:8080'
logger.info(f"Set LEGACY_ERP_API_LIVE to: {os.environ['LEGACY_ERP_API_LIVE']}")
logger.info(f"Set LEGACY_ERP_API_TEST to: {os.environ['LEGACY_ERP_API_TEST']}")

 # Import the SimpleAPIClient from getTable


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Test the updated filtering implementation')  # noqa: F841

    parser.add_argument('--env', default='live',
                        help='Environment to use (default: live)')  # noqa: F841

    parser.add_argument('--table', default='Artikel',
                        help='Table to test filters on (default: Artikel)')  # noqa: F841

    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')  # noqa: F841

    parser.add_argument('--list-tables', action='store_true',
                        help='List available tables in the legacy ERP system')  # noqa: F841

    return parser.parse_args()


def list_available_tables(client):
    """List available tables in the legacy ERP system."""
    logger.info("=== Listing Available Tables ===")

    try:
        url = f"{client.base_url}/rest/$catalog"
        logger.info(f"Requesting catalog from: {url}")

        response = client.session.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                logger.info(f"Found {len(data)} tables:")
                for table in data:
                    if isinstance(table, dict) and 'name' in table:
                        logger.info(f"  - {table['name']}")
                    else:
                        logger.info(f"  - {table}")
            else:
                logger.info(f"Unexpected catalog response format: {data}")
        else:
            logger.error(
                f"Failed to get catalog: {response.status_code} - {response.text}")  # noqa: E501
    except Exception as e:
        logger.error(f"Error listing tables: {e}")


def test_simple_equality_filter(client, table_name):
    """Test a simple equality filter."""
    logger.info("=== Testing Simple Equality Filter ===")
    filter_query = "Artikel_Nr = '115413'"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_text_search_filter(client, table_name):
    """Test a text search filter with LIKE operator."""
    logger.info("=== Testing Text Search Filter (LIKE) ===")
    filter_query = "Bezeichnung LIKE '%Test%'"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return True  # Consider success even if no records found
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_numeric_comparison_filter(client, table_name):
    """Test a numeric comparison filter."""
    logger.info("=== Testing Numeric Comparison Filter ===")
    filter_query = "Preis > 10"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_boolean_filter(client, table_name):
    """Test a boolean filter."""
    logger.info("=== Testing Boolean Filter ===")
    filter_query = "aktiv = true"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_date_filter(client, table_name):
    """Test a date filter."""
    logger.info("=== Testing Date Filter ===")
    filter_query = "CREATIONDATE >= '2023-01-01'"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_combined_filter(client, table_name):
    """Test a combined filter with AND operator."""
    logger.info("=== Testing Combined Filter (AND) ===")
    filter_query = "Preis > 5 AND aktiv = true"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_or_filter(client, table_name):
    """Test a filter with OR operator."""
    logger.info("=== Testing OR Filter ===")
    filter_query = "Artikel_Nr = '115413' OR Artikel_Nr = '115414'"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,  # noqa: E128
            top=10,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_pagination_with_filter(client, table_name):
    """Test pagination with a filter."""
    logger.info("=== Testing Pagination with Filter ===")
    filter_query = "Preis > 0"
    logger.info(f"Filter query: {filter_query}")

    try:
        df = client.fetch_table(
            table_name=table_name,
            all_records=True,  # noqa: F841
            filter_query=filter_query
        )

        logger.info(f"Result: {len(df)} records found")
        if not df.empty:
            logger.info(f"First record: {df.iloc[0].to_dict()}")
            logger.info(f"Last record: {df.iloc[-1].to_dict()}")
        return len(df) > 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def main():
    """Main function to execute when script is run."""
    args = parse_args()

 # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

 # Create the client
    client = SimpleAPIClient(environment=args.env)

 # List available tables if requested
    if args.list_tables:
        list_available_tables(client)
        return 0

 # Run the tests
    tests = [
             ("Simple Equality Filter", test_simple_equality_filter),  # noqa: E128
             ("Text Search Filter", test_text_search_filter),
             ("Numeric Comparison Filter", test_numeric_comparison_filter),
             ("Boolean Filter", test_boolean_filter),
             ("Date Filter", test_date_filter),
             ("Combined Filter", test_combined_filter),
             ("OR Filter", test_or_filter),
             ("Pagination with Filter", test_pagination_with_filter)
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n\nRunning test: {test_name}")
        try:
            result = test_func(client, args.table)
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            logger.error(f"Test {test_name} raised an exception: {e}")
            results[test_name] = "ERROR"

 # Print summary
    logger.info("\n\n=== TEST RESULTS SUMMARY ===")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")

 # Overall result
    if all(result == "PASS" for result in results.values()):
        logger.info("\nAll tests PASSED!")
        return 0
    else:
        logger.info("\nSome tests FAILED or had ERRORS!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
