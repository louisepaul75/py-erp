#!/usr/bin/env python
"""
Lists vaults accessible by the 1Password Connect client.

This script initializes the Django settings to load the .env file
and the 1Password client, then calls the get_vaults() method.

Usage:
  python scripts/list_1pw_vaults.py
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
    # Need to configure Django settings explicitly when running script directly
    import django
    django.setup()
except RuntimeError as e:
    # Handle cases where settings might already be configured
    if "Settings already configured" not in str(e):
        logging.error(f"Error configuring Django: {e}", exc_info=True)
        sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error during Django setup: {e}", exc_info=True)
    sys.exit(1)


# --- Import necessary components from settings ---
try:
    # Import the initialized client
    from pyerp.config.settings.base import op_client
except ImportError as e:
    logging.error(f"Failed to import op_client from settings: {e}", exc_info=True)
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error importing op_client: {e}", exc_info=True)
    sys.exit(1)

# --- Basic Logging Configuration ---
# Reconfigure logging in case settings changed it
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def list_vaults():
    """Lists accessible 1Password vaults."""
    logging.info("--- Attempting to list 1Password Vaults ---")

    if not op_client:
        logging.error(
            "1Password client (op_client) is not initialized. "
            "Check OP_CONNECT_HOST and OP_CONNECT_TOKEN environment variables "
            "in config/env/.env.dev and ensure the onepasswordconnectsdk is installed."
        )
        sys.exit(1)

    logging.info("1Password client initialized. Fetching vaults...")

    try:
        vaults = op_client.get_vaults()
        if vaults:
            print("\nAccessible Vaults:") # Use print for guaranteed output
            logging.info("Accessible Vaults:")
            for vault in vaults:
                print(f"  - Name: {vault.name}, ID: {vault.id}") # Use print
                logging.info(f"  - Name: {vault.name}, ID: {vault.id}")
        else:
            print("\nNo vaults found or accessible with the current token.") # Use print
            logging.info("No vaults found or accessible with the current token.")

    except Exception as e:
        logging.error(f"Error fetching vaults from 1Password: {e}", exc_info=True)
        sys.exit(1)

    logging.info("--- Vault listing finished ---")

if __name__ == "__main__":
    list_vaults()
