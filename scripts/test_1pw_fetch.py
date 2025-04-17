#!/usr/bin/env python
"""
Test script for fetching secrets from 1Password using the Connect SDK.

This script initializes the 1Password client based on environment variables
(OP_CONNECT_HOST, OP_CONNECT_TOKEN) and attempts to fetch specified items
from different vaults using the helper functions defined in Django settings.
It also lists all items found in the tested vaults.

Usage:
  python scripts/test_1pw_fetch.py
"""

import os
import sys
import logging
from pathlib import Path

# --- Setup Django Environment ---
# Add project root to sys.path to allow importing Django modules
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Set the DJANGO_SETTINGS_MODULE environment variable
# Use 'pyerp.config.settings.base' to access the helper functions directly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.base")

# Configure Django settings (this loads the settings file)
try:
    from django.conf import settings
    settings.configure()  # Minimal configuration needed to load settings
except RuntimeError as e:
    # Handle cases where settings might already be configured
    if "Settings already configured" not in str(e):
        raise

# --- Import necessary components from settings ---
try:
    # Import the initialized client and helper functions
    from pyerp.config.settings.base import (
        op_client,
        get_op_item_fields  # get_vault_uuid_by_name is implicitly used
    )
except ImportError as e:
    logging.error(f"Failed to import from settings: {e}", exc_info=True)
    sys.exit(1)

# --- Basic Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- Test Cases ---
# List of tuples: (vault_name, item_name)
TEST_ITEMS = [
    ("dev", "postgres_db"),          # Expected DB credentials
    ("dev", "image_cms_api"),        # Expected Image API credentials
    ("dev-high", "buchhaltungsbutler_api"),  # Test fetching BB credentials
    ("dev", "non_existent_item"),    # Expected to fail (item not found)
    ("non_existent_vault", "any_item"),  # Expected to fail (vault not found)
]


def run_tests():
    """Runs the 1Password fetch tests and lists items in vaults."""
    logging.info("--- Starting 1Password Fetch Test ---")

    if not op_client:
        logging.error(
            "1Password client (op_client) is not initialized. "
            "Check OP_CONNECT_HOST and OP_CONNECT_TOKEN environment variables "
            "and ensure the onepasswordconnectsdk is installed."
        )
        sys.exit(1)

    logging.info("1Password client appears to be initialized.")

    success_count = 0
    failure_count = 0
    results = {}  # Store results for summary
    listed_vaults = set()  # Keep track of vaults whose items have been listed

    for vault_name, item_name in TEST_ITEMS:
        logging.info("-" * 40)
        logging.info(
            f"Testing fetch for: Vault='{vault_name}', Item='{item_name}'"
        )
        test_key = f"{vault_name}/{item_name}"
        results[test_key] = "PENDING"  # Initial status

        item_fields, vault_uuid = get_op_item_fields(
            op_client, vault_name, item_name
        )

        # --- List items in the vault (if not already listed) ---
        if vault_uuid and vault_uuid not in listed_vaults:
            try:
                logging.info(
                    f"Attempting to list items in vault '{vault_name}' "
                    f"(UUID: {vault_uuid})..."
                )
                items = op_client.get_items(vault_id=vault_uuid)
                item_titles = sorted([item.title for item in items])
                logging.info(
                    f"Items found in vault '{vault_name}' "
                    f"({len(item_titles)} items): {item_titles}"
                )
            except Exception as e:
                logging.warning(
                    f"Could not list items for vault '{vault_name}': {e}",
                    exc_info=True
                )
            listed_vaults.add(vault_uuid)
        elif not vault_uuid and vault_name != "non_existent_vault":
            # Log if we couldn't get vault_uuid for a non-test vault
            logging.warning(
                f"Could not get UUID for vault '{vault_name}', "
                f"cannot list items."
            )

        # --- Original Test Logic --- 
        is_expected_failure = ("non_existent" in vault_name or
                               "non_existent" in item_name)

        if item_fields:
            logging.info(
                f"Success: Fetched item '{item_name}' from vault "
                f"'{vault_name}'."
            )
            logging.info(f"Fields found: {list(item_fields.keys())}")
            # Optionally log sensitive fields carefully (e.g., just existence)
            if 'password' in item_fields or 'API Secret' in item_fields:
                logging.info("  (Password/Secret field present)")
            success_count += 1
            results[test_key] = "SUCCESS"
        else:
            # Handle expected failures gracefully
            if is_expected_failure:
                logging.info(
                    f"Expected Failure: Item '{item_name}' or vault "
                    f"'{vault_name}' not found, as expected."
                )
                # Count expected failures as success for the test purpose
                success_count += 1
                results[test_key] = "SUCCESS (Expected Failure)"
            elif vault_uuid is None and "non_existent_vault" not in vault_name:
                # This case handles when get_op_item_fields returns
                # vault_uuid=None but it wasn't an expected failure
                logging.error(f"Failed: Could not find vault '{vault_name}'.")
                failure_count += 1
                results[test_key] = "FAILED (Vault not found)"
            else:
                # This case handles when item_fields is None but it wasn't an
                # expected failure
                logging.error(
                    f"Failed: Could not retrieve fields for item '{item_name}'"
                    f" from vault '{vault_name}'. "
                    f"Check logs above for details."
                )
                failure_count += 1
                results[test_key] = "FAILED (Item fields not retrieved)"

    logging.info("-" * 40)
    logging.info("--- Test Summary ---")
    logging.info(f"Total tests run: {len(TEST_ITEMS)}")
    # Detailed results
    logging.info("Detailed Results:")
    for test_key, status in results.items():
        logging.info(f"  - {test_key}: {status}")

    logging.info(
        f"Successful fetches (including expected failures): {success_count}"
    )
    logging.info(f"Unexpected failures: {failure_count}")
    logging.info("--- Test Finished ---")

    # Exit with status code 1 if there were unexpected failures
    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
