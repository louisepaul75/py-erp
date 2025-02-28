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
    
    # If we want to search all pages, we need to call the API directly
    if search_all_pages:
        print(f"Searching ALL API pages for images (this may take a while)...")
        
        # Get total pages info
        first_page = client._make_request("all-files-and-articles/", params={"page": 1, "page_size": 1})
        if not first_page:
            print("Failed to connect to API")
            return
            
        total_records = first_page.get('count', 0)
        page_size = 100
        total_pages = (total_records + page_size - 1) // page_size
        
        print(f"Found {total_records} total images across {total_pages} pages")
        images = []
        
        # Process ALL pages - no limit
        for page in range(1, total_pages + 1):
            print(f"Processing page {page}/{total_pages}")
            
            # Get images for this page
            data = client._make_request("all-files-and-articles/", params={"page": page, "page_size": page_size})
            if not data:
                print(f"Failed to fetch page {page}")
                continue
            
            # Process each image
            for image_data in data.get('results', []):
                # Check if this might be related to our SKU
                articles = image_data.get('articles', [])
                
                # Check each article number
                for article in articles:
                    article_number = article.get('number')
                    if article_number == sku:
                        images.append(image_data)
                        print(f"Found matching image on page {page} - Type: {image_data.get('type', 'Unknown')}")
                        break
    else:
        # Use the existing method (which stops after finding images on the first page)
        print(f"Fetching images from API (first match only)...")
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
        if not parsed_image.get('external_id'):
            # Use a combination of image URL and type as a unique identifier
            image_url = parsed_image.get('image_url', '')
            image_type = parsed_image.get('image_type', 'Unknown')
            unique_id = f"{image_url}_{image_type}"
            parsed_image['external_id'] = unique_id
        
        # Print the external ID for debugging
        print(f"External ID: {parsed_image.get('external_id', 'None')}")
        
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
                    print(f"Updating existing image: {image.id}")
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
                    print("Found front Produktfoto! Setting as primary.")
                    ProductImage.objects.filter(product=product).update(is_primary=False)
                    image.is_primary = True
                
                # Save the image
                image.save()
                
                print(f"{'Created' if created else 'Updated'} image: {image.id} ({image.image_type})")
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
    
    # Default to searching all pages
    search_all_pages = True
    if len(sys.argv) > 2:
        search_all_pages = sys.argv[2].lower() == 'true'
    
    sync_product_images_for_sku(sku, search_all_pages=search_all_pages) 