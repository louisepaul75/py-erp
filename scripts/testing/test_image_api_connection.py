#!/usr/bin/env python
"""
Test script for the Image API connection.

This script attempts to connect to the external image database API
and fetch a small amount of data to verify the connection works.

Usage:
    python scripts/test_image_api_connection.py [--verbose]
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

from pyerp.utils.env_loader import load_environment_variables

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the centralized environment loader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("image_api_test")


def setup_environment():
    """Load environment variables using centralized loader"""
    # Load environment variables
    load_environment_variables()

    # Check if required variables are set
    required_vars = ["IMAGE_API_URL", "IMAGE_API_USERNAME", "IMAGE_API_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}",
        )
        logger.error("Please set these variables in your .env file or environment.")
        sys.exit(1)

    return {
        "base_url": os.environ.get("IMAGE_API_URL"),
        "username": os.environ.get("IMAGE_API_USERNAME"),
        "password": os.environ.get("IMAGE_API_PASSWORD"),
        "timeout": int(os.environ.get("IMAGE_API_TIMEOUT", 30)),
    }


def test_api_connection(config, verbose=False):
    """Test connection to the image API"""
    endpoint = "all-files-and-articles/"
    url = f"{config['base_url'].rstrip('/')}/{endpoint}?page=1&page_size=1"

    logger.info(f"Testing connection to {config['base_url']}")

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(config["username"], config["password"]),
            timeout=config["timeout"],
        )

        # Check if request was successful
        if response.status_code == 200:
            data = response.json()

            logger.info("✅ Connection successful!")
            logger.info(f"API returned {data.get('count', 'unknown')} total records")

            if verbose and data.get("results"):
                logger.info("\nSample data (first record):")
                print(json.dumps(data["results"][0], indent=2))

            return True
        logger.error(f"❌ Connection failed with status code: {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Connection error: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Image API connection")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display verbose output",
    )
    args = parser.parse_args()

    # Load configuration
    config = setup_environment()

    # Test connection
    test_api_connection(config, args.verbose)
