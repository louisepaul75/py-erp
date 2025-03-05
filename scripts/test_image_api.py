#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.config.settings.local')
django.setup()

from pyerp.products.image_api import ImageAPIClient

def main():
    # Create an instance of the ImageAPIClient
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

    # Test searching for product images
    test_sku = "910669"  # Example SKU from the codebase
    print(f"\nSearching for images for product SKU: {test_sku}")
    product_images = client.search_product_images(test_sku)
    
    if product_images:
        print(f"Found {len(product_images)} images for product {test_sku}")
        for idx, image in enumerate(product_images, 1):
            parsed_image = client.parse_image(image)
            print(f"\nImage {idx}:")
            print(f"External ID: {parsed_image.get('external_id')}")
            print(f"Image Type: {parsed_image.get('image_type')}")
            print(f"Image URL: {parsed_image.get('image_url')}")
            print(f"Thumbnail URL: {parsed_image.get('thumbnail_url')}")
    else:
        print(f"No images found for product {test_sku}")

if __name__ == "__main__":
    main() 