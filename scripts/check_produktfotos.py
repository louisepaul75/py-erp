#!/usr/bin/env python
import os
import sys

import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

# Import the necessary models and the ImageAPIClient
from pyerp.products.image_api import ImageAPIClient
from pyerp.products.models import VariantProduct


def search_all_produktfotos_for_sku(sku, limit_pages=10):
    """
    Search through the API for any Produktfoto images that might be associated with the SKU
    """
    print(f"Searching for Produktfoto images for SKU: {sku}")

    # Find the product
    try:
        product = VariantProduct.objects.get(sku=sku)
        print(f"Found product: {product.name} (SKU: {product.sku})")
    except VariantProduct.DoesNotExist:
        print(f"Error: Product with SKU {sku} not found")
        return None

    # Initialize the API client
    client = ImageAPIClient()

    # Get API metadata to know total pages
    first_page = client._make_request(
        "all-files-and-articles/",
        params={"page": 1, "page_size": 1},
    )
    if not first_page:
        print("Failed to connect to API")
        return None

    total_records = first_page.get("count", 0)
    page_size = 100
    total_pages = (total_records + page_size - 1) // page_size

    print(f"Found {total_records} total images across {total_pages} pages")

    # Limit pages if requested
    if limit_pages:
        total_pages = min(total_pages, limit_pages)

    found_images = []
    produktfotos = []

    # Process each page
    for page in range(1, total_pages + 1):
        print(f"Processing page {page}/{total_pages}")

        # Get images for this page
        data = client._make_request(
            "all-files-and-articles/",
            params={"page": page, "page_size": page_size},
        )
        if not data:
            print(f"Failed to fetch page {page}")
            continue

        # Process each image
        for image_data in data.get("results", []):
            # Check if this might be related to our SKU
            articles = image_data.get("articles", [])

            # Check each article number
            for article in articles:
                article_number = article.get("number")
                if not article_number:
                    continue

                # Check if this might be our product
                # Either exact match or contains the SKU
                if (
                    article_number == sku
                    or article_number.startswith(sku)
                    or sku.startswith(article_number)
                ):
                    # Parse the image
                    parsed_image = client.parse_image(image_data)
                    found_images.append(
                        {
                            "article_number": article_number,
                            "image_type": parsed_image["image_type"],
                            "is_front": article.get("front", False),
                            "image_url": parsed_image["image_url"],
                        },
                    )

                    # Check if it's a Produktfoto
                    if parsed_image["image_type"] == "Produktfoto":
                        produktfotos.append(
                            {
                                "article_number": article_number,
                                "is_front": article.get("front", False),
                                "image_url": parsed_image["image_url"],
                                "external_id": parsed_image["external_id"],
                            },
                        )

    # Print results
    print(f"\nFound {len(found_images)} potentially related images")

    if found_images:
        print("\nAll potentially related images:")
        for img in found_images:
            print(
                f"- Article: {img['article_number']}, Type: {img['image_type']}, Front: {img['is_front']}",
            )
            print(f"  URL: {img['image_url']}")

    print(f"\nFound {len(produktfotos)} Produktfoto images")

    if produktfotos:
        print("\nAll Produktfoto images:")
        for img in produktfotos:
            print(f"- Article: {img['article_number']}, Front: {img['is_front']}")
            print(f"  URL: {img['image_url']}")
            print(f"  External ID: {img['external_id']}")

    return produktfotos


if __name__ == "__main__":
    sku = "816941"
    if len(sys.argv) > 1:
        sku = sys.argv[1]

    search_all_produktfotos_for_sku(sku, limit_pages=5)
