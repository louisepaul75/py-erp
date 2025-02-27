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
from pyerp.products.models import Product, ParentProduct, VariantProduct, ProductCategory
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
    
    print(f"New models - Parent products: {new_parent_count}")
    print(f"New models - Variant products: {new_variant_count}")
    
    # Check migration progress
    if old_parent_count > 0:
        parent_progress = (new_parent_count / old_parent_count) * 100
        print(f"Parent product migration progress: {parent_progress:.2f}%")
    else:
        print("No parent products in old model")
    
    if old_variant_count > 0:
        variant_progress = (new_variant_count / old_variant_count) * 100
        print(f"Variant product migration progress: {variant_progress:.2f}%")
    else:
        print("No variant products in old model")


def check_relationships():
    """Check the relationships between parent and variant products."""
    print("\n=== RELATIONSHIP CHECK ===")
    
    # Check variants per parent
    parents_with_variants = ParentProduct.objects.annotate(variant_count=Count('variants'))
    total_parents = parents_with_variants.count()
    parents_with_no_variants = parents_with_variants.filter(variant_count=0).count()
    
    print(f"Total parent products: {total_parents}")
    print(f"Parents with no variants: {parents_with_no_variants}")
    print(f"Parents with variants: {total_parents - parents_with_no_variants}")
    
    # Check distribution of variants
    if total_parents > 0:
        avg_variants = VariantProduct.objects.count() / total_parents
        print(f"Average variants per parent: {avg_variants:.2f}")
    
    # Check top 5 parents by variant count
    top_parents = parents_with_variants.order_by('-variant_count')[:5]
    print("\nTop 5 parents by variant count:")
    for parent in top_parents:
        print(f"  - {parent.sku}: {parent.name} ({parent.variant_count} variants)")


def check_sample_data():
    """Check sample data from the new models."""
    print("\n=== SAMPLE DATA ===")
    
    # Check a sample parent product
    try:
        sample_parent = ParentProduct.objects.first()
        if sample_parent:
            print(f"Sample parent product: {sample_parent.sku} - {sample_parent.name}")
            print(f"  Base SKU: {sample_parent.base_sku}")
            print(f"  Legacy ID: {sample_parent.legacy_id}")
            print(f"  Category: {sample_parent.category.name if sample_parent.category else 'None'}")
            
            # Check variants of this parent
            variants = sample_parent.variants.all()
            print(f"  Variants ({variants.count()}):")
            for variant in variants[:5]:  # Show first 5 variants
                print(f"    - {variant.sku}: {variant.name} (Variant code: {variant.variant_code})")
    except Exception as e:
        print(f"Error checking sample parent: {str(e)}")
    
    # Check a sample variant product
    try:
        sample_variant = VariantProduct.objects.first()
        if sample_variant:
            print(f"\nSample variant product: {sample_variant.sku} - {sample_variant.name}")
            print(f"  Parent: {sample_variant.parent.sku} - {sample_variant.parent.name}")
            print(f"  Base SKU: {sample_variant.base_sku}")
            print(f"  Variant code: {sample_variant.variant_code}")
            print(f"  Legacy SKU: {sample_variant.legacy_sku}")
            print(f"  Legacy ID: {sample_variant.legacy_id}")
    except Exception as e:
        print(f"Error checking sample variant: {str(e)}")


def check_sku_mapping():
    """
    Check if the SKU and legacy_id fields are correctly mapped in parent products.
    """
    print("\n=== Checking SKU Mapping ===")
    
    try:
        # Import models
        from pyerp.products.models import ParentProduct
        
        # Get all parent products
        parents = ParentProduct.objects.all()
        total_parents = parents.count()
        
        print(f"Total parent products: {total_parents}")
        
        # Check for potential mapping issues
        potential_issues = 0
        for parent in parents[:10]:  # Check first 10 for display
            print(f"Parent ID: {parent.id}, SKU: {parent.sku}, Legacy ID: {parent.legacy_id}")
            
            # Check if SKU looks like a legacy ID (typically shorter numeric value)
            if parent.sku and parent.sku.isdigit() and len(parent.sku) <= 4:
                potential_issues += 1
                print(f"  WARNING: SKU '{parent.sku}' looks like it might be a legacy ID")
            
            # Check if legacy_id looks like a SKU (typically longer numeric value)
            if parent.legacy_id and parent.legacy_id.isdigit() and len(parent.legacy_id) >= 5:
                potential_issues += 1
                print(f"  WARNING: Legacy ID '{parent.legacy_id}' looks like it might be a SKU")
        
        # Count total potential issues
        total_potential_issues = 0
        for parent in parents:
            if parent.sku and parent.sku.isdigit() and len(parent.sku) <= 4:
                total_potential_issues += 1
            if parent.legacy_id and parent.legacy_id.isdigit() and len(parent.legacy_id) >= 5:
                total_potential_issues += 1
        
        print(f"Total potential SKU mapping issues: {total_potential_issues}")
        
        if total_potential_issues > 0:
            print("RECOMMENDATION: Run 'python manage.py fix_parent_sku_mapping' to fix these issues")
        else:
            print("SKU mapping appears to be correct")
            
    except Exception as e:
        print(f"Error checking SKU mapping: {str(e)}")


def check_variant_parent_relationships():
    """
    Check the relationships between variant products and their parent products.
    """
    print("\n=== Checking Variant-Parent Relationships ===")
    
    try:
        # Import models
        from pyerp.products.models import VariantProduct, ParentProduct
        
        # Get all variants
        variants = VariantProduct.objects.all()
        total_variants = variants.count()
        
        # Count variants with and without parents
        variants_with_parent = VariantProduct.objects.filter(parent__isnull=False).count()
        variants_without_parent = VariantProduct.objects.filter(parent__isnull=True).count()
        
        print(f"Total variants: {total_variants}")
        print(f"Variants with parent: {variants_with_parent} ({variants_with_parent/total_variants*100:.2f}%)")
        print(f"Variants without parent: {variants_without_parent} ({variants_without_parent/total_variants*100:.2f}%)")
        
        # Check a sample of variants without parents
        if variants_without_parent > 0:
            print("\nSample of variants without parents:")
            orphan_variants = VariantProduct.objects.filter(parent__isnull=True)[:5]
            for variant in orphan_variants:
                print(f"Variant ID: {variant.id}, SKU: {variant.sku}")
                
                # Try to extract potential parent SKU
                import re
                match = re.match(r'^(\d+)[-_]', variant.sku)
                potential_parent_sku = match.group(1) if match else None
                
                if potential_parent_sku:
                    # Check if a parent with this SKU exists
                    parent_exists = ParentProduct.objects.filter(sku=potential_parent_sku).exists()
                    print(f"  Potential parent SKU: {potential_parent_sku}, Exists: {parent_exists}")
            
            print(f"\nRECOMMENDATION: Run 'python manage.py fix_variant_parent_relationships' to fix these relationships")
        else:
            print("All variants have parent products assigned")
            
    except Exception as e:
        print(f"Error checking variant-parent relationships: {str(e)}")


if __name__ == "__main__":
    print("Testing product model split...")
    
    check_model_structure()
    check_data_migration()
    check_relationships()
    check_sku_mapping()
    check_variant_parent_relationships()
    check_sample_data()
    
    print("\nTest completed.") 