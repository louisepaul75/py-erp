#!/usr/bin/env python
"""
Script to check inventory data relationships
"""
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

# Import models after Django setup
from pyerp.business_modules.inventory.models import ProductStorage
from pyerp.business_modules.products.models import VariantProduct
from django.db.models import Sum, Count

def check_inventory_data():
    """Check inventory data relationships"""
    print("Checking inventory data relationships...")
    
    # Basic counts
    total_product_storage = ProductStorage.objects.count()
    total_variant_products = VariantProduct.objects.count()
    products_with_storage = VariantProduct.objects.filter(storage_locations__isnull=False).distinct().count()
    
    print("\nBasic Counts:")
    print(f"  Total ProductStorage records: {total_product_storage}")
    print(f"  Total VariantProduct records: {total_variant_products}")
    print(f"  VariantProducts with inventory: {products_with_storage}")
    
    # Check for products with inventory records but zero current_stock
    zero_stock_with_inventory = VariantProduct.objects.filter(
        storage_locations__isnull=False, 
        current_stock=0
    ).distinct().count()
    
    print("\nData Integrity Checks:")
    print(f"  Products with inventory records but zero current_stock: {zero_stock_with_inventory}")
    
    # Check for orphaned ProductStorage records
    orphaned_storage = ProductStorage.objects.filter(product__isnull=True).count()
    print(f"  Orphaned ProductStorage records (invalid product references): {orphaned_storage}")
    
    # Sample data
    print("\nSample ProductStorage Records:")
    for ps in ProductStorage.objects.select_related('product', 'box_slot')[:5]:
        print(f"  Product: {ps.product.sku}, Quantity: {ps.quantity}, Location: {ps.box_slot}")
    
    # Check for mismatched inventory quantities
    print("\nProducts with mismatched inventory quantities (sample):")
    mismatched = 0
    for product in VariantProduct.objects.filter(storage_locations__isnull=False).distinct()[:10]:
        inventory_sum = ProductStorage.objects.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        if product.current_stock != inventory_sum:
            mismatched += 1
            print(f"  Product {product.sku}: current_stock={product.current_stock}, inventory_sum={inventory_sum}")
    
    print(f"  Total mismatched (from sample): {mismatched}")
    
    # Distribution of products by storage location count
    storage_counts = VariantProduct.objects.filter(
        storage_locations__isnull=False
    ).annotate(
        location_count=Count('storage_locations')
    ).values('location_count').annotate(
        product_count=Count('id')
    ).order_by('location_count')
    
    print("\nDistribution of products by storage location count:")
    for item in storage_counts:
        print(f"  Products with {item['location_count']} storage locations: {item['product_count']}")

if __name__ == "__main__":
    check_inventory_data() 