import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from pyerp.products.models import ParentProduct, VariantProduct


def check_relationships():
    # Get overall statistics
    total_variants = VariantProduct.objects.count()
    variants_with_parent = VariantProduct.objects.filter(parent__isnull=False).count()
    print(
        f"Variants with parent: {variants_with_parent}/{total_variants} ({round(variants_with_parent / total_variants * 100, 2)}%)",
    )

    # Check some variants without parents
    variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)[:10]
    print("\nVariants without parent (first 10):")
    for var in variants_without_parent:
        print(f"SKU: {var.sku}, Key: {var.legacy_key}, Familie: {var.legacy_familie}")

        # Check if a parent with matching Familie exists
        parent = ParentProduct.objects.filter(legacy_id=var.legacy_familie).first()
        if parent:
            print(
                f"  → Matching parent found: SKU: {parent.sku}, legacy_id: {parent.legacy_id}",
            )
        else:
            print("  → No matching parent found")

    # Check a variant with an established parent relation
    var_with_parent = VariantProduct.objects.filter(parent__isnull=False).first()
    if var_with_parent:
        parent = var_with_parent.parent
        print("\nExample of variant with parent:")
        print(
            f"Variant: {var_with_parent.sku}, Parent: {parent.sku}, Familie_: {var_with_parent.legacy_familie}, Parent legacy_id: {parent.legacy_id}",
        )


if __name__ == "__main__":
    check_relationships()
