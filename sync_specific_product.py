#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

# Import the necessary models and the ImageAPIClient
from pyerp.products.models import VariantProduct, ProductImage
from pyerp.products.image_api import ImageAPIClient
from django.db import transaction

def sync_product_images_for_sku(sku):
    """
    Manually sync all images for a specific product SKU
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
    
    # Get all images for this product
    print(f"Fetching images from API...")
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
        
        # Check if this image is attached to our product
        is_for_this_product = False
        for article in image_data.get('articles', []):
            if article.get('number') == sku:
                is_for_this_product = True
                # Set front flag
                parsed_image['is_front'] = article.get('front', False)
                break
        
        if not is_for_this_product:
            print(f"Skipping image - not directly attached to this product")
            continue
        
        print(f"Image type: {parsed_image['image_type']}, Front: {parsed_image.get('is_front', False)}")
        
        # Create or update the image
        try:
            with transaction.atomic():
                # Look for existing image
                try:
                    image = ProductImage.objects.get(
                        product=product,
                        external_id=parsed_image['external_id']
                    )
                    print(f"Updating existing image")
                    created = False
                except ProductImage.DoesNotExist:
                    image = ProductImage(
                        product=product, 
                        external_id=parsed_image['external_id']
                    )
                    print(f"Creating new image")
                    created = True
                
                # Update fields
                image.image_url = parsed_image['image_url']
                image.thumbnail_url = parsed_image.get('thumbnail_url')
                image.image_type = parsed_image['image_type']
                image.is_front = parsed_image.get('is_front', False)
                image.priority = client.get_image_priority(parsed_image)
                
                # Auto-generate alt text if not set
                if not image.alt_text:
                    image.alt_text = f"{product.name} - {parsed_image['image_type']}"
                
                # Store metadata
                image.metadata = parsed_image.get('metadata', {})
                
                # If this is a front Produktfoto, make it primary
                if parsed_image['image_type'] == 'Produktfoto' and parsed_image.get('is_front', False):
                    # Remove primary flag from all other images
                    ProductImage.objects.filter(product=product).update(is_primary=False)
                    image.is_primary = True
                
                # Save the image
                image.save()
                
                print(f"{'Created' if created else 'Updated'} image: {image.id}")
        except Exception as e:
            print(f"Error processing image: {str(e)}")
    
    # Report summary
    final_count = ProductImage.objects.filter(product=product).count()
    print(f"\nSync completed. Product now has {final_count} images.")
    
    # List all images
    print("\nFinal images for this product:")
    for img in ProductImage.objects.filter(product=product).order_by('priority'):
        print(f"- Type: {img.image_type}, Front: {img.is_front}, Primary: {img.is_primary}")

if __name__ == "__main__":
    sku = "816941"
    if len(sys.argv) > 1:
        sku = sys.argv[1]
    
    sync_product_images_for_sku(sku) 