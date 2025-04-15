#!/usr/bin/env python
"""
Test script for fetching secrets from 1Password using the Connect SDK.

This script initializes the 1Password client based on environment variables
(OP_CONNECT_HOST, OP_CONNECT_TOKEN) and attempts to fetch specified items
from different vaults using the helper functions defined in Django settings.

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
    settings.configure() # Minimal configuration needed to load settings
except RuntimeError as e:
    # Handle cases where settings might already be configured
    if "Settings already configured" not in str(e):
        raise

# --- Import necessary components from settings ---
try:
    # Import the initialized client and helper functions
    from pyerp.config.settings.base import (
        op_client,
        get_vault_uuid_by_name,
        get_op_item_fields
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
    # ("dev-high", "buchhaltungsbutler_api"), # Removed: May be env-specific
    ("dev", "non_existent_item"),    # Expected to fail (item not found)
    ("non_existent_vault", "any_item"), # Expected to fail (vault not found)
]


def run_tests():
    """Runs the 1Password fetch tests."""
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

    for vault_name, item_name in TEST_ITEMS:
        logging.info("-" * 40)
        logging.info(f"Testing fetch for: Vault='{vault_name}', Item='{item_name}'")

        item_fields, vault_uuid = get_op_item_fields(op_client, vault_name, item_name)

        if vault_uuid is None and "non_existent_vault" not in vault_name:
             logging.error(f"Failed: Could not find vault '{vault_name}'.")
             failure_count += 1
        elif item_fields:
            logging.info(f"Success: Fetched item '{item_name}' from vault '{vault_name}'.")
            logging.info(f"Fields found: {list(item_fields.keys())}")
            # Optionally log sensitive fields carefully (e.g., just existence)
            if 'password' in item_fields or 'API Secret' in item_fields:
                 logging.info("  (Password/Secret field present)")
            success_count += 1
        else:
            # Handle expected failures gracefully
            if "non_existent" in vault_name or "non_existent" in item_name:
                 logging.info(f"Expected Failure: Item '{item_name}' or vault '{vault_name}' not found, as expected.")
                 success_count += 1 # Count expected failures as success for the test purpose
            else:
                 logging.error(f"Failed: Could not retrieve fields for item '{item_name}' from vault '{vault_name}'. Check logs above for details.")
                 failure_count += 1

    logging.info("-" * 40)
    logging.info("--- Test Summary ---")
    logging.info(f"Total tests run: {len(TEST_ITEMS)}")
    logging.info(f"Successful fetches (including expected failures): {success_count}")
    logging.info(f"Unexpected failures: {failure_count}")
    logging.info("--- Test Finished ---")

    # Exit with status code 1 if there were unexpected failures
    if failure_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
