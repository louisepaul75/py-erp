import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import transaction

from pyerp.products.models import ParentProduct, VariantProduct


def create_placeholder_parents():
    print("\n=== CREATING PLACEHOLDER PARENT PRODUCTS ===\n")

    # Get variants without parents
    variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)
    total_orphans = variants_without_parent.count()

    print(f"Found {total_orphans} variants without parent products.")

    if total_orphans == 0:
        print("No orphaned variants found. Nothing to do.")
        return

    # Ask for confirmation
    print(
        "\nThis script will create placeholder parent products for orphaned variants.",
    )
    print(
        "These placeholder parents will use data from their variants with a 'PLACEHOLDER' prefix.",
    )
    choice = input("Do you want to proceed? (y/n): ")

    if choice.lower() != "y":
        print("Operation cancelled.")
        return

    # Track results
    created_parents = 0
    updated_relationships = 0
    errors = 0

    # Create parents and update relationships
    with transaction.atomic():
        for variant in variants_without_parent:
            try:
                # Create placeholder parent
                parent = ParentProduct(
                    sku=f"PLACEHOLDER-{variant.sku}",
                    name=(
                        f"PLACEHOLDER - {variant.name}"
                        if variant.name
                        else f"PLACEHOLDER Parent for {variant.sku}"
                    ),
                    description=variant.description,
                    is_active=variant.is_active,
                    # Set legacy_id to match the variant's legacy_familie for proper linking
                    legacy_id=variant.legacy_familie,
                    is_placeholder=True,  # Custom field to mark as placeholder
                )
                parent.save()
                created_parents += 1

                # Update variant to link to this parent
                variant.parent = parent
                variant.save()
                updated_relationships += 1

                print(
                    f"Created placeholder parent {parent.sku} for variant {variant.sku}",
                )
            except Exception as e:
                errors += 1
                print(f"Error processing variant {variant.sku}: {e!s}")

    # Summary
    print("\n=== OPERATION SUMMARY ===")
    print(f"Total orphaned variants: {total_orphans}")
    print(f"Placeholder parents created: {created_parents}")
    print(f"Variant relationships updated: {updated_relationships}")
    print(f"Errors encountered: {errors}")
    print(f"Success rate: {(updated_relationships / total_orphans) * 100:.2f}%")

    # Next steps
    print("\n=== NEXT STEPS ===")
    print("1. Review the created placeholder parents in the admin interface")
    print("2. Add additional data to the placeholder parents as needed")
    print("3. Run validation checks to ensure proper parent-child relationships")
    print("\n=== OPERATION COMPLETE ===\n")


if __name__ == "__main__":
    create_placeholder_parents()
