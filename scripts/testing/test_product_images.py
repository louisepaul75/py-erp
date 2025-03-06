#!/usr/bin/env python
"""
Test script to retrieve images for a specific product.

This script connects to the external image database API
and fetches images for a specific product article number.

Usage:
    python scripts/test_product_images.py <article_number> [--verbose]
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
logger = logging.getLogger("product_images_test")


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


def get_product_images(config, article_number, verbose=False):
    """Fetch images for a specific product by article number"""
    endpoint = "all-files-and-articles/"
    url = f"{config['base_url'].rstrip('/')}/{endpoint}"

    logger.info(f"Searching for images for article number: {article_number}")

    try:
        # Fetch all pages until we find images for the article
        product_images = []
        page = 1
        page_size = 50
        total_pages = None

        while total_pages is None or page <= total_pages:
            page_url = f"{url}?page={page}&page_size={page_size}"

            response = requests.get(
                page_url,
                auth=HTTPBasicAuth(config["username"], config["password"]),
                timeout=config["timeout"],
            )

            if response.status_code != 200:
                logger.error(
                    f"❌ API request failed with status code: {response.status_code}",
                )
                logger.error(f"Response: {response.text}")
                return []

            data = response.json()

            # Calculate total pages on first response
            if total_pages is None:
                count = data.get("count", 0)
                total_pages = (count + page_size - 1) // page_size
                logger.info(
                    f"Found {count} total records, {total_pages} pages to process",
                )

            # Process the results
            for item in data.get("results", []):
                articles = item.get("articles", [])

                # Check if any article matches our article number
                for article in articles:
                    if article.get("number") == article_number:
                        product_images.append(item)
                        break

            # Show progress
            if page % 5 == 0:
                logger.info(f"Processed {page} of {total_pages} pages...")

            page += 1

            # If we've found at least one image and not in verbose mode, we can
            # stop
            if product_images and not verbose:
                logger.info(f"Found {len(product_images)} images, stopping search")
                break

        if not product_images:
            logger.warning(f"No images found for article number: {article_number}")
        else:
            logger.info(
                f"✅ Found {len(product_images)} images for article: {article_number}",
            )

            # Process images to extract URLs
            for i, item in enumerate(product_images):
                # Extract images from original_file and exported_files
                print(f"\nImage {i + 1}:")

                if verbose:
                    # In verbose mode, print the full item details
                    print(json.dumps(item, indent=2))
                else:
                    # In normal mode, print just the image URLs
                    urls = []

                    # Check original file
                    if (
                        item.get("original_file")
                        and "file_url" in item["original_file"]
                    ):
                        urls.append(
                            {
                                "type": item["original_file"].get("type", "unknown"),
                                "format": item["original_file"].get(
                                    "format",
                                    "unknown",
                                ),
                                "url": item["original_file"]["file_url"],
                            },
                        )

                    # Check exported files
                    for export in item.get("exported_files", []):
                        if export.get("image_url"):
                            urls.append(
                                {
                                    "type": export.get("type", "unknown"),
                                    "resolution": export.get("resolution", []),
                                    "url": export["image_url"],
                                },
                            )

                    # Print the URLs
                    for url_info in urls:
                        print(
                            f"  - {url_info['type']} ({
                                ', '.join(
                                    str(r) for r in url_info.get('resolution', []) if r
                                )
                            }): {url_info['url']}",
                        )

                    # Print if this is a front image
                    for article in item.get("articles", []):
                        if article.get("number") == article_number:
                            is_front = article.get("front", False)
                            print(f"  - Is front image: {is_front}")
                            break

        return product_images

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Connection error: {e}")
        return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test fetching images for a specific product",
    )
    parser.add_argument("article_number", help="The article number to search for")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display verbose output",
    )
    args = parser.parse_args()

    # Load configuration
    config = setup_environment()

    # Get product images
    get_product_images(config, args.article_number, args.verbose)
