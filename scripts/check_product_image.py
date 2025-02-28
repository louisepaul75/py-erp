#!/usr/bin/env python
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

# Import models
from pyerp.products.models import VariantProduct, ProductImage

def check_product_images(sku):
    """Check if a product has Produktfoto images with front=True"""
    # Find the product
    product = VariantProduct.objects.filter(sku=sku).first()
    if not product:
        print(f"Product with SKU {sku} not found")
        return
    
    print(f"Product found: {product.name} (SKU: {product.sku})")
    
    # Check total number of images
    total_images = product.images.count()
    print(f"Total images: {total_images}")
    
    # Find all images
    all_images = product.images.all()
    print("\nAll images:")
    for img in all_images:
        print(f"- Type: {img.image_type}, Front: {img.is_front}, Primary: {img.is_primary}")
    
    # Find Produktfoto images with front=True
    produktfotos = product.images.filter(image_type__iexact='Produktfoto', is_front=True)
    produktfotos_count = produktfotos.count()
    print(f"\nProduktfotos with front=True: {produktfotos_count}")
    
    if produktfotos_count > 0:
        print("\nDetails of Produktfotos with front=True:")
        for img in produktfotos:
            print(f"- Type: {img.image_type}, Front: {img.is_front}, Primary: {img.is_primary}")
            print(f"  URL: {img.image_url}")
    
    # Check which image would be selected based on our new priority logic
    selected_image = None
    
    # First priority: Produktfoto with front=True
    selected_image = product.images.filter(image_type__iexact='Produktfoto', is_front=True).first()
    
    if not selected_image:
        # Second priority: Any Produktfoto
        selected_image = product.images.filter(image_type__iexact='Produktfoto').first()
    
    if not selected_image:
        # Third priority: Any front=True image
        selected_image = product.images.filter(is_front=True).first()
    
    if not selected_image:
        # Fourth priority: Any image marked as primary
        selected_image = product.images.filter(is_primary=True).first()
    
    if not selected_image:
        # Last resort: First image
        selected_image = product.images.first()
    
    if selected_image:
        print("\nImage that would be selected by our new priority logic:")
        print(f"- Type: {selected_image.image_type}, Front: {selected_image.is_front}, Primary: {selected_image.is_primary}")
        print(f"  URL: {selected_image.image_url}")
    else:
        print("\nNo image would be selected")

if __name__ == "__main__":
    sku = "816941"
    if len(sys.argv) > 1:
        sku = sys.argv[1]
    
    check_product_images(sku) 