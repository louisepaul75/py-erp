"""
Test script to verify the new product model structure.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')
django.setup()

# Import Django models
from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory
from pyerp.products.models_new import Product  # Import Product from models_new.py
from django.db.models import Count


def check_model_structure():
    """Check the structure of the new models."""
    print("\n=== MODEL STRUCTURE ===")
    
    # Check if the new models exist
    print(f"ParentProduct model exists: {ParentProduct._meta.db_table in django.db.connection.introspection.table_names()}")
    print(f"VariantProduct model exists: {VariantProduct._meta.db_table in django.db.connection.introspection.table_names()}")
    
    # Check the fields of the new models
    print("\nParentProduct fields:")
    for field in ParentProduct._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")
    
    print("\nVariantProduct fields:")
    for field in VariantProduct._meta.get_fields():
        print(f"  - {field.name}: {field.__class__.__name__}")


def check_data_migration():
    """Check if data has been migrated to the new models."""
    print("\n=== DATA MIGRATION STATUS ===")
    
    # Count products in the old model
    old_parent_count = Product.objects.filter(is_parent=True).count()
    old_variant_count = Product.objects.filter(is_parent=False).count()
    
    print(f"Old model - Parent products: {old_parent_count}")
    print(f"Old model - Variant products: {old_variant_count}")
    
    # Count products in the new models
    new_parent_count = ParentProduct.objects.count()
    new_variant_count = VariantProduct.objects.count()
    
    print(f"New model - Parent products: {new_parent_count}")
    print(f"New model - Variant products: {new_variant_count}")
    
    # Calculate migration progress
    if old_parent_count > 0:
        parent_progress = (new_parent_count / old_parent_count) * 100
        print(f"Parent product migration progress: {parent_progress:.1f}%")
    else:
        print("No parent products to migrate")
    
    if old_variant_count > 0:
        variant_progress = (new_variant_count / old_variant_count) * 100
        print(f"Variant product migration progress: {variant_progress:.1f}%")
    else:
        print("No variant products to migrate")


def check_relationships():
    """Check the relationships between parent and variant products."""
    print("\n=== RELATIONSHIP CHECK ===")
    
    # Check variants with no parent
    orphan_variants = VariantProduct.objects.filter(parent__isnull=True).count()
    print(f"Orphan variants (no parent): {orphan_variants}")
    
    # Check parents with no variants
    childless_parents = ParentProduct.objects.annotate(
        variant_count=Count('variants')
    ).filter(variant_count=0).count()
    print(f"Childless parents (no variants): {childless_parents}")
    
    # Check average variants per parent
    total_parents = ParentProduct.objects.count()
    total_variants = VariantProduct.objects.count()
    if total_parents > 0:
        avg_variants = total_variants / total_parents
        print(f"Average variants per parent: {avg_variants:.1f}")
    else:
        print("No parent products found")


def check_sample_data():
    """Check sample data from both models."""
    print("\n=== SAMPLE DATA CHECK ===")
    
    # Get a sample parent product from the old model
    old_parent = Product.objects.filter(is_parent=True).first()
    if old_parent:
        print("\nSample parent product from old model:")
        print(f"  - SKU: {old_parent.sku}")
        print(f"  - Name: {old_parent.name}")
        print(f"  - Base SKU: {old_parent.base_sku}")
        
        # Try to find the corresponding parent in the new model
        try:
            new_parent = ParentProduct.objects.get(sku=old_parent.sku)
            print("\nCorresponding parent in new model:")
            print(f"  - SKU: {new_parent.sku}")
            print(f"  - Name: {new_parent.name}")
            print(f"  - Base SKU: {new_parent.base_sku}")
        except ParentProduct.DoesNotExist:
            print("\nNo corresponding parent found in new model")
    else:
        print("No parent products found in old model")
    
    # Get a sample variant product from the old model
    old_variant = Product.objects.filter(is_parent=False).first()
    if old_variant:
        print("\nSample variant product from old model:")
        print(f"  - SKU: {old_variant.sku}")
        print(f"  - Name: {old_variant.name}")
        print(f"  - Parent SKU: {old_variant.parent.sku if old_variant.parent else 'None'}")
        
        # Try to find the corresponding variant in the new model
        try:
            new_variant = VariantProduct.objects.get(sku=old_variant.sku)
            print("\nCorresponding variant in new model:")
            print(f"  - SKU: {new_variant.sku}")
            print(f"  - Name: {new_variant.name}")
            print(f"  - Parent SKU: {new_variant.parent.sku if new_variant.parent else 'None'}")
        except VariantProduct.DoesNotExist:
            print("\nNo corresponding variant found in new model")
    else:
        print("No variant products found in old model")


def check_sku_mapping():
    """Check SKU mapping between old and new models."""
    print("\n=== SKU MAPPING CHECK ===")
    
    # Get all SKUs from the old model
    old_skus = set(Product.objects.values_list('sku', flat=True))
    print(f"Total SKUs in old model: {len(old_skus)}")
    
    # Get all SKUs from the new models
    parent_skus = set(ParentProduct.objects.values_list('sku', flat=True))
    variant_skus = set(VariantProduct.objects.values_list('sku', flat=True))
    new_skus = parent_skus.union(variant_skus)
    print(f"Total SKUs in new models: {len(new_skus)}")
    
    # Check for missing SKUs
    missing_skus = old_skus - new_skus
    print(f"SKUs in old model but missing from new models: {len(missing_skus)}")
    if missing_skus and len(missing_skus) < 10:
        print("Missing SKUs:")
        for sku in missing_skus:
            print(f"  - {sku}")
    
    # Check for extra SKUs
    extra_skus = new_skus - old_skus
    print(f"SKUs in new models but not in old model: {len(extra_skus)}")
    if extra_skus and len(extra_skus) < 10:
        print("Extra SKUs:")
        for sku in extra_skus:
            print(f"  - {sku}")
    
    # Calculate coverage
    if old_skus:
        coverage = (len(old_skus) - len(missing_skus)) / len(old_skus) * 100
        print(f"SKU migration coverage: {coverage:.1f}%")
    else:
        print("No SKUs in old model")


def check_variant_parent_relationships():
    """Check if variant-parent relationships are preserved."""
    print("\n=== VARIANT-PARENT RELATIONSHIP CHECK ===")
    
    # Get variants with parents from the old model
    old_variants = Product.objects.filter(
        is_parent=False, 
        parent__isnull=False
    )[:100]  # Limit to 100 for performance
    
    total_checked = 0
    correctly_mapped = 0
    
    for old_variant in old_variants:
        total_checked += 1
        old_parent = old_variant.parent
        
        try:
            new_variant = VariantProduct.objects.get(sku=old_variant.sku)
            new_parent = new_variant.parent
            
            if new_parent and new_parent.sku == old_parent.sku:
                correctly_mapped += 1
            else:
                print(f"Mismatched parent for variant {old_variant.sku}:")
                print(f"  - Old parent: {old_parent.sku}")
                print(f"  - New parent: {new_parent.sku if new_parent else 'None'}")
        except VariantProduct.DoesNotExist:
            print(f"Variant {old_variant.sku} not found in new model")
    
    if total_checked > 0:
        accuracy = (correctly_mapped / total_checked) * 100
        print(f"Checked {total_checked} variant-parent relationships")
        print(f"Correctly mapped: {correctly_mapped} ({accuracy:.1f}%)")
    else:
        print("No variant-parent relationships to check")


if __name__ == "__main__":
    print("=== PRODUCT MODEL MIGRATION TEST ===")
    print("This script checks the migration from the old Product model to the new ParentProduct/VariantProduct models.")
    
    check_model_structure()
    check_data_migration()
    check_relationships()
    check_sample_data()
    check_sku_mapping()
    check_variant_parent_relationships()
    
    print("\nTest completed.") 