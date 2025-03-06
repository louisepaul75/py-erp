from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from pyerp.products.models import ParentProduct, VariantProduct


class Command(BaseCommand):
    help = "Creates placeholder parent products for variants without parents"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the operation without making changes",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Create placeholder parent products for variants without parents.

        Args:
            *args: Variable length argument list
            **options: Arbitrary keyword arguments:
                - dry_run: Run without making changes
                - force: Create even if parent exists

        Returns:
            None
        """
        dry_run = options["dry_run"]
        force = options["force"]

        self.stdout.write(
            self.style.SUCCESS("\n=== CREATING PLACEHOLDER PARENT PRODUCTS ===\n"),
        )

        # Get variants without parents
        variants = VariantProduct.objects.filter(parent__isnull=True)

        if not variants.exists():
            self.stdout.write(self.style.SUCCESS("No variants without parents found."))
            return

        variant_count = variants.count()
        self.stdout.write(f"Found {variant_count} variants without parents.")

        # Group variants by base SKU
        sku_groups = {}
        for variant in variants:
            base_sku = variant.base_sku or variant.sku
            if base_sku not in sku_groups:
                sku_groups[base_sku] = []
            sku_groups[base_sku].append(variant)

        group_count = len(sku_groups)
        self.stdout.write(f"Grouped into {group_count} potential parent products.")

        # Process each group
        created_count = 0
        skipped_count = 0
        error_count = 0

        with transaction.atomic():
            for base_sku, group_variants in sku_groups.items():
                try:
                    # Check if parent already exists
                    existing_parent = ParentProduct.objects.filter(
                        base_sku=base_sku
                    ).first()

                    if existing_parent and not force:
                        skip_msg = f"Parent already exists for {base_sku} - skipping"
                        self.stdout.write(skip_msg)
                        skipped_count += 1
                        continue

                    # Create parent product
                    first_variant = group_variants[0]
                    name_prefix = "Parent Product for"
                    parent_name = f"{name_prefix} {first_variant.name}"
                    parent_sku = f"{base_sku}-P"

                    if not dry_run:
                        desc = "Automatically created placeholder parent product"
                        parent = ParentProduct.objects.create(
                            sku=parent_sku,
                            base_sku=base_sku,
                            name=parent_name,
                            description=desc,
                        )

                        # Link variants to parent
                        for variant in group_variants:
                            variant.parent = parent
                            variant.save()

                        created_count += 1
                    else:
                        variant_count = len(group_variants)
                        msg_parts = [
                            f"Would create parent {parent_sku}",
                            f"for {variant_count} variants",
                        ]
                        msg = " ".join(msg_parts)
                        self.stdout.write(msg)

                except Exception as e:
                    error_msg = f"Error processing {base_sku}: {e!s}"
                    self.stdout.write(self.style.ERROR(error_msg))
                    error_count += 1

        # Print summary
        summary_parts = [
            "\nCreated",
            str(created_count),
            "parents,",
            f"Skipped {skipped_count},",
            f"Errors {error_count}",
        ]
        summary = " ".join(summary_parts)
        self.stdout.write(self.style.SUCCESS(summary))

        if dry_run:
            dry_run_msg = "This was a dry run - no changes made."
            self.stdout.write(self.style.WARNING(dry_run_msg))

        # Next steps
        self.stdout.write(self.style.SUCCESS("\n=== NEXT STEPS ==="))
        self.stdout.write(
            "1. Review the created placeholder parents in the admin interface",
        )
        self.stdout.write("2. Add additional data to the placeholder parents as needed")
        self.stdout.write(
            "3. Run validation checks to ensure proper parent-child relationships",
        )
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION COMPLETE ===\n"))
