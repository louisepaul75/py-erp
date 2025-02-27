import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')
django.setup()

# Import Django models and database connection
from django.db import connection
from pyerp.products.models import Product

def list_tables():
    """List all tables in the database"""
    with connection.cursor() as cursor:
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        
        print("\n=== TABLES IN DATABASE ===")
        for table in tables:
            print(f"- {table[0]}")

def inspect_products_table():
    """Inspect the products table structure"""
    with connection.cursor() as cursor:
        cursor.execute('DESCRIBE products_product')
        columns = cursor.fetchall()
        
        print("\n=== PRODUCTS TABLE STRUCTURE ===")
        for column in columns:
            print(f"- {column[0]}: {column[1]}")

def count_products():
    """Count products by type"""
    total = Product.objects.count()
    parents = Product.objects.filter(is_parent=True).count()
    variants = Product.objects.filter(is_parent=False).count()
    
    print("\n=== PRODUCT COUNTS ===")
    print(f"Total products: {total}")
    print(f"Parent products: {parents}")
    print(f"Variant products: {variants}")

def sample_products():
    """Show sample products"""
    print("\n=== SAMPLE PARENT PRODUCTS ===")
    for product in Product.objects.filter(is_parent=True)[:5]:
        print(f"ID: {product.id}, SKU: {product.sku}, Name: {product.name}")
        print(f"  Legacy ID: {product.legacy_id}, Legacy SKU: {product.legacy_sku}")
        print(f"  Base SKU: {product.base_sku}, Variant Code: {product.variant_code}")
        print(f"  Variants: {product.variants.count()}")
        print()
    
    print("\n=== SAMPLE VARIANT PRODUCTS ===")
    for product in Product.objects.filter(is_parent=False)[:5]:
        parent_sku = product.parent.sku if product.parent else "None"
        print(f"ID: {product.id}, SKU: {product.sku}, Name: {product.name}")
        print(f"  Legacy ID: {product.legacy_id}, Legacy SKU: {product.legacy_sku}")
        print(f"  Base SKU: {product.base_sku}, Variant Code: {product.variant_code}")
        print(f"  Parent SKU: {parent_sku}")
        print()

if __name__ == "__main__":
    try:
        list_tables()
        inspect_products_table()
        count_products()
        sample_products()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 