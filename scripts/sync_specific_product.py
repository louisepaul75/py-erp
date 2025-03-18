#!/usr/bin/env python
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)  # noqa: E402

from pyerp.utils.env_loader import load_environment_variables  # noqa: E402
import django  # noqa: E402

# Load environment variables using env_loader (will load if .env file exists)
load_environment_variables(verbose=True)

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Import the necessary models and the ImageAPIClient
from django.db import transaction

from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.products.models import ProductImage, VariantProduct


def sync_product_images_for_sku(sku, search_all_pages=True):
    """
    Manually sync all images for a specific product SKU

    Args:
        sku (str): The product SKU to sync images for
        search_all_pages (bool): Whether to search all pages of the API
                                or stop after finding the first image
    """
    print(f"Starting image sync for product with SKU: {sku}")

    # Find the product
    try:
        product = VariantProduct.objects.get(sku=sku)
        print(f"Found product: {product.name} (SKU: {product.sku})")
    except VariantProduct.DoesNotExist:
        print(f"Error: Product with SKU {sku} not found")
        return

    # Initialize the API client
    client = ImageAPIClient()

    # Get images from API
    print("Searching for images in API...")
    images = client.search_product_images(sku)

    if not images:
        print(f"No images found in API for SKU {sku}")
        return

    print(f"Found {len(images)} images in API")

    # Process each image
    for idx, image_data in enumerate(images):
        print(f"\nProcessing image {idx + 1} of {len(images)}")

        # Parse the image
        parsed_image = client.parse_image(image_data)

        # Create a unique external_id if not present
        if not parsed_image.get("external_id"):
            # Use a combination of image URL and type as a unique identifier
            image_url = parsed_image.get("image_url", "")
            image_type = parsed_image.get("image_type", "Unknown")
            unique_id = f"{image_url}_{image_type}"
            parsed_image["external_id"] = unique_id

        # Print the external ID for debugging
        print(f"External ID: {parsed_image.get('external_id', 'None')}")

        # Check if this image is attached to our product
        is_for_this_product = False
        for article in image_data.get("articles", []):
            if article.get("number") == sku:
                is_for_this_product = True
                # Set front flag
                parsed_image["is_front"] = article.get("front", False)
                break

        if not is_for_this_product:
            print("Skipping image - not directly attached to this product")
            continue

        print(
            f"Image type: {parsed_image['image_type']}, Front: {parsed_image.get('is_front', False)}",
        )

        # Create or update the image
        try:
            with transaction.atomic():
                # Look for existing image
                try:
                    image = ProductImage.objects.get(
                        product=product,
                        external_id=parsed_image["external_id"],
                    )
                    print(f"Updating existing image: {image.id}")
                    created = False
                except ProductImage.DoesNotExist:
                    # Let Django handle ID generation
                    image = ProductImage(
                        product=product,
                        external_id=parsed_image["external_id"],
                    )
                    print("Creating new image")
                    created = True

                # Update fields
                image.image_url = parsed_image["image_url"]
                image.thumbnail_url = parsed_image.get("thumbnail_url")
                image.image_type = parsed_image["image_type"]
                image.is_front = parsed_image.get("is_front", False)
                image.priority = client.get_image_priority(parsed_image)

                # Auto-generate alt text if not set
                if not image.alt_text:
                    image.alt_text = f"{product.name} - {parsed_image['image_type']}"

                # Store metadata
                image.metadata = parsed_image.get("metadata", {})

                # If this is a front Produktfoto, make it primary
                if parsed_image["image_type"] == "Produktfoto" and parsed_image.get(
                    "is_front",
                    False,
                ):
                    # Remove primary flag from all other images
                    print("Found front Produktfoto! Setting as primary.")
                    ProductImage.objects.filter(product=product).update(
                        is_primary=False,
                    )
                    image.is_primary = True
                else:
                    image.is_primary = False

                # Save the image
                image.save()

                if created:
                    print(f"Created new image: {image.id}")
                else:
                    print(f"Updated image: {image.id}")

        except Exception as e:
            print(f"Error processing image: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sync_specific_product.py <sku>")
        sys.exit(1)

    sku = sys.argv[1]
    sync_product_images_for_sku(sku)
