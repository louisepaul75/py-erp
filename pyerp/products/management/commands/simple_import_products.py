"""
Management command to populate the ParentProduct and VariantProduct tables with sample data.  # noqa: E501
This is a simplified version that doesn't depend on external APIs.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct, VariantProduct, ProductCategory  # noqa: E501

 # Configure logging
logger = logging.getLogger(__name__)  # noqa: F841


class Command(BaseCommand):
    help = 'Populate ParentProduct and VariantProduct tables with sample data'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Run without making changes to the database'  # noqa: F841
        )
        parser.add_argument(
            '--parent-count',  # noqa: E128
            type=int,  # noqa: F841
            default=10,  # noqa: F841
            help='Number of parent products to create'  # noqa: F841
        )
        parser.add_argument(
            '--variants-per-parent',  # noqa: E128
            type=int,  # noqa: F841
            default=3,  # noqa: F841
            help='Number of variants per parent'  # noqa: F841
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        parent_count = options['parent_count']
        variants_per_parent = options['variants_per_parent']

        self.stdout.write(self.style.NOTICE(f'Starting import of {parent_count} parent products and {parent_count * variants_per_parent} variants...'))  # noqa: E501

 # Create a default category if needed
        category, created = ProductCategory.objects.get_or_create(
            code='DEFAULT',  # noqa: E128
            defaults={'name': 'Default Category'}  # noqa: F841
        )

 # Begin transaction
        with transaction.atomic():
            parents_created = 0  # noqa: F841
            for i in range(1, parent_count + 1):
                try:
                    parent_sku = f"P{i:04d}"
                    legacy_id = f"LEGACY_KEY_{i}"
                    legacy_uid = f"UID_{i}"

                    parent = ParentProduct(
                        sku=parent_sku,  # noqa: E128
                        base_sku=parent_sku,  # noqa: F841
                        legacy_id=legacy_id,
                        legacy_uid=legacy_uid,
                        __KEY=legacy_id,  # noqa: F841
                        UID=legacy_uid,  # noqa: F841
                        FAMILIE_=f"Family {i}",  # noqa: F841
                        name=f"Parent Product {i}",  # noqa: F841
                        is_active=True  # noqa: F841
                    )

                    if not dry_run:
                        parent.save()
                        parents_created += 1
                        self.stdout.write(f"Created parent product: {parent_sku}")  # noqa: E501

 # Create variant products for this parent
                    for j in range(1, variants_per_parent + 1):
                        variant_sku = f"{parent_sku}-V{j}"
                        variant_code = f"VAR{j}"

                        variant = VariantProduct(
                            sku=variant_sku,  # noqa: E128
                            legacy_sku=variant_sku,  # noqa: F841
                            base_sku=parent_sku,  # noqa: F841
                            legacy_id=f"{legacy_id}_V{j}",
                            legacy_uid=f"{legacy_uid}_V{j}",
                            __KEY=f"{legacy_id}_V{j}",  # noqa: F841
                            UID=f"{legacy_uid}_V{j}",  # noqa: F841
                            FAMILIE_=f"Family {i}",  # noqa: F841
                            name=f"Variant {j} of Parent {i}",  # noqa: F841
                            is_active=True,  # noqa: F841
                            variant_code=variant_code
                        )

                        if not dry_run:
                            variant.save()
                            self.stdout.write(f"  Created variant: {variant_sku}")  # noqa: E501

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating products: {str(e)}"))  # noqa: E501
                    raise

 # If it's a dry run, rollback the transaction
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes were saved to the database"))  # noqa: E501
                transaction.set_rollback(True)

 # Transaction completed
        if not dry_run:
            parent_count_db = ParentProduct.objects.count()
            variant_count_db = VariantProduct.objects.count()
            self.stdout.write(self.style.SUCCESS(f'Final product counts - Parents: {parent_count_db}, Variants: {variant_count_db}'))  # noqa: E501

        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))
