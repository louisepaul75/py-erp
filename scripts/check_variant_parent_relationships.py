import os
import django
import sys

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pyerp.products.models import VariantProduct, ParentProduct

def check_variant_parent_relationships():
    print("\n=== VARIANT-PARENT RELATIONSHIP REPORT ===\n")
    
    # Overall statistics
    total_variants = VariantProduct.objects.count()
    variants_with_parent = VariantProduct.objects.filter(parent__isnull=False).count()
    variants_without_parent = total_variants - variants_with_parent
    
    print(f"Total variants: {total_variants}")
    print(f"Variants with parent: {variants_with_parent} ({round(variants_with_parent/total_variants*100, 2)}%)")
    print(f"Variants without parent: {variants_without_parent} ({round(variants_without_parent/total_variants*100, 2)}%)")
    
    # Check variants without parents
    if variants_without_parent > 0:
        print("\n--- VARIANTS WITHOUT PARENTS ---")
        no_parent_variants = VariantProduct.objects.filter(parent__isnull=True)
        
        # Count how many have a matching parent by Familie
        potential_fixes = 0
        no_matching_parent = 0
        
        print("\nChecking first 10 variants without parents:")
        for i, var in enumerate(no_parent_variants[:10]):
            print(f"\n{i+1}. Variant SKU: {var.sku}")
            print(f"   Legacy Key: {var.legacy_key}")
            print(f"   Legacy Familie: {var.legacy_familie}")
            
            # Check if matching parent exists
            matching_parent = ParentProduct.objects.filter(legacy_id=var.legacy_familie).first()
            if matching_parent:
                print(f"   ✓ Matching parent found: SKU: {matching_parent.sku}")
                potential_fixes += 1
            else:
                print(f"   ✗ No matching parent found")
                no_matching_parent += 1
        
        # Check all variants without parents
        all_potential_fixes = 0
        for var in no_parent_variants:
            matching_parent = ParentProduct.objects.filter(legacy_id=var.legacy_familie).first()
            if matching_parent:
                all_potential_fixes += 1
        
        print(f"\nOut of {variants_without_parent} variants without parents:")
        print(f"- {all_potential_fixes} have a matching parent that could be linked")
        print(f"- {variants_without_parent - all_potential_fixes} have no matching parent")
    
    # Example of correct relationship
    print("\n--- EXAMPLE OF CORRECT RELATIONSHIP ---")
    var_with_parent = VariantProduct.objects.filter(parent__isnull=False).first()
    if var_with_parent:
        parent = var_with_parent.parent
        print(f"Variant SKU: {var_with_parent.sku}")
        print(f"Parent SKU: {parent.sku}")
        print(f"Variant Legacy Familie: {var_with_parent.legacy_familie}")
        print(f"Parent Legacy ID: {parent.legacy_id}")
        print(f"Familie matches Legacy ID: {'✓' if var_with_parent.legacy_familie == parent.legacy_id else '✗'}")
    
    print("\n=== END OF REPORT ===\n")

if __name__ == "__main__":
    check_variant_parent_relationships() 