#!/usr/bin/env python
import logging
from pyerp.products.image_api import ImageAPIClient
import os
import sys
import django

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.local')
django.setup()


def main():
    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3').setLevel(logging.DEBUG)

    client = ImageAPIClient()

    # Test getting all images (first page)
    print("\nFetching first page of all images...")
    images = client.get_all_images(page=1, page_size=5)

    if images:
        print(f"Successfully retrieved {len(images)} images")

        # Display details of the first image
        if len(images) > 0:
            first_image = client.parse_image(images[0])
            print("\nFirst image details:")
            print(f"External ID: {first_image.get('external_id')}")
            print(f"Image Type: {first_image.get('image_type')}")
            print(f"Image URL: {first_image.get('image_url')}")
            print(f"Thumbnail URL: {first_image.get('thumbnail_url')}")
    else:
        print("No images found or error occurred")


if __name__ == "__main__":
    main()
