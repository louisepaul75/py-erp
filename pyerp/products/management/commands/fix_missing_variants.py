"""
Management command to fix missing variants by creating placeholder parent products.  # noqa: E501
"""

import logging
import re
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import Product, ParentProduct, VariantProduct, ProductCategory  # noqa: E501

 # Configure logging
logger = logging.getLogger(__name__)  # noqa: F841


class Command(BaseCommand):
    help = 'Fix missing variants by creating placeholder parent products'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Perform a dry run without saving to the database'  # noqa: F841
        )
        parser.add_argument(
            '--limit',  # noqa: E128
            type=int,  # noqa: F841
            default=None,  # noqa: F841
            help='Limit the number of variants to process'  # noqa: F841
        )
        parser.add_argument(
            '--sku-pattern',  # noqa: E128
            type=str,  # noqa: F841
            default=None,  # noqa: F841
            help='Process only variants matching this SKU pattern (regex)'  # noqa: F841
        )
        parser.add_argument(
            '--create-parents',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Create placeholder parent products for missing variants'  # noqa: F841
        )
        parser.add_argument(
            '--group-by-prefix',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Group variants by SKU prefix when creating placeholder parents'  # noqa: E501
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        sku_pattern = options['sku_pattern']
        create_parents = options['create_parents']
        group_by_prefix = options['group_by_prefix']

        self.stdout.write(self.style.NOTICE('Starting missing variants analysis...'))  # noqa: E501

 # Get all variants from the old model that haven't been migrated
        migrated_variants = set(VariantProduct.objects.values_list('legacy_id', flat=True))  # noqa: E501
        old_variants = Product.objects.filter(is_parent=False)

        if sku_pattern:
            pattern = re.compile(sku_pattern)  # noqa: F841
            old_variants = old_variants.filter(sku__regex=sku_pattern)

        missing_variants = old_variants.exclude(legacy_id__in=migrated_variants)  # noqa: E501

        if limit:
            missing_variants = missing_variants[:limit]

        total_missing = missing_variants.count()
        self.stdout.write(self.style.SUCCESS(f'Found {total_missing} missing variants'))  # noqa: E501

 # Group variants by SKU prefix
        prefix_groups = {}
        for variant in missing_variants:
            prefix = variant.sku[:3] if len(variant.sku) >= 3 else variant.sku
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(variant)

 # Print summary of prefix groups
        self.stdout.write(self.style.NOTICE('\nVariants grouped by prefix:'))
        for prefix, variants in sorted(prefix_groups.items()):
            self.stdout.write(f'  {prefix}xxx: {len(variants)} variants')

 # Create placeholder parents if requested
        if create_parents and not dry_run:
            self.create_placeholder_parents(prefix_groups, group_by_prefix)
        elif create_parents and dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - Would create placeholder parents:'))  # noqa: E501
            self.simulate_parent_creation(prefix_groups, group_by_prefix)

 # Print detailed list of missing variants
        self.stdout.write(self.style.NOTICE('\nDetailed list of missing variants:'))  # noqa: E501
        for i, variant in enumerate(missing_variants[:20]):  # Show first 20 for brevity  # noqa: E501
            self.stdout.write(f'  {i+1}. {variant.sku} - {variant.name}')

        if len(missing_variants) > 20:
            self.stdout.write(f'  ... and {len(missing_variants) - 20} more')

 # Print summary
        self.stdout.write(self.style.SUCCESS(f'\nAnalysis completed: {total_missing} missing variants identified'))  # noqa: E501
        if dry_run and create_parents:
            self.stdout.write(self.style.WARNING('This was a dry run. No changes were made to the database.'))  # noqa: E501
        elif create_parents:
            self.stdout.write(self.style.SUCCESS('Placeholder parents created successfully.'))  # noqa: E501

    def create_placeholder_parents(self, prefix_groups, group_by_prefix):
        """Create placeholder parent products for missing variants."""
        self.stdout.write(self.style.NOTICE('\nCreating placeholder parent products...'))  # noqa: E501

 # Get or create uncategorized category
        uncategorized, _ = ProductCategory.objects.get_or_create(
            code='UNCATEGORIZED',  # noqa: E128
            defaults={'name': 'Uncategorized'}  # noqa: F841
        )

        created_parents = 0
        migrated_variants = 0

        with transaction.atomic():
            if group_by_prefix:
                for prefix, variants in prefix_groups.items():
                    parent_sku = f"{prefix}000"
                    parent_name = f"Product Group {prefix}xxx"

 # Create parent product
                    parent, created = ParentProduct.objects.get_or_create(
                        sku=parent_sku,  # noqa: E128
                        defaults={  # noqa: F841
                        'name': parent_name,  # noqa: E128
                        'base_sku': parent_sku,
                        'category': uncategorized,
                        'is_active': True,
                        'description': f"Placeholder parent for {len(variants)} variants with prefix {prefix}xxx"  # noqa: E501
                        }
                    )

                    if created:
                        created_parents += 1
                        self.stdout.write(f"  Created parent: {parent_sku} - {parent_name}")  # noqa: E501

 # Create variants
                    for variant in variants:
                        variant_code = variant.sku[3:] if len(variant.sku) >= 3 else ""  # noqa: E501

 # Create variant product
                        new_variant, created = VariantProduct.objects.get_or_create(  # noqa: E501
                            legacy_id=variant.legacy_id,  # noqa: F841
                            defaults={  # noqa: F841
                            'sku': variant.sku,  # noqa: E128
                            'name': variant.name,
                            'parent': parent,
                            'base_sku': parent.sku,
                            'variant_code': variant_code,
                            'legacy_sku': variant.legacy_sku or variant.sku,  # noqa: E501
                            'category': parent.category,
                            'is_active': variant.is_active,
                            'list_price': variant.list_price,
                            'wholesale_price': variant.wholesale_price,
                            'gross_price': variant.gross_price,
                            'cost_price': variant.cost_price,
                            'stock_quantity': variant.stock_quantity,
                            'description': variant.description,
                            'short_description': variant.short_description,
                        }
                        )

                        if created:
                            migrated_variants += 1
            else:
                for prefix, variants in prefix_groups.items():
                    for variant in variants:
                        parent_sku = f"{variant.sku}-P"
                        parent_name = f"{variant.name} (Parent)"

 # Create parent product
                        parent, created = ParentProduct.objects.get_or_create(
                            sku=parent_sku,  # noqa: E128
                            defaults={  # noqa: F841
                            'name': parent_name,  # noqa: E128
                            'base_sku': variant.sku,
                            'category': uncategorized,
                            'is_active': variant.is_active,
                            'description': f"Placeholder parent for variant {variant.sku}"  # noqa: E501
                            }
                        )

                        if created:
                            created_parents += 1
                            self.stdout.write(f"  Created parent: {parent_sku} - {parent_name}")  # noqa: E501

 # Create variant product
                        new_variant, created = VariantProduct.objects.get_or_create(  # noqa: E501
                            legacy_id=variant.legacy_id,  # noqa: F841
                            defaults={  # noqa: F841
                            'sku': variant.sku,
                            'name': variant.name,
                            'parent': parent,
                            'base_sku': parent.sku,
                            'variant_code': "V1",
                            'legacy_sku': variant.legacy_sku or variant.sku,  # noqa: E501
                            'category': parent.category,
                            'is_active': variant.is_active,
                            'list_price': variant.list_price,
                            'wholesale_price': variant.wholesale_price,
                            'gross_price': variant.gross_price,
                            'cost_price': variant.cost_price,
                            'stock_quantity': variant.stock_quantity,
                            'description': variant.description,
                            'short_description': variant.short_description,
                        }
                        )

                        if created:
                            migrated_variants += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created_parents} placeholder parents and migrated {migrated_variants} variants"))  # noqa: E501

    def simulate_parent_creation(self, prefix_groups, group_by_prefix):
        """Simulate creating placeholder parent products for missing variants."""  # noqa: E501
        if group_by_prefix:
            for prefix, variants in prefix_groups.items():
                parent_sku = f"{prefix}000"
                parent_name = f"Product Group {prefix}xxx"
                self.stdout.write(f"  Would create parent: {parent_sku} - {parent_name} for {len(variants)} variants")  # noqa: E501
        else:
            variant_count = sum(len(variants) for variants in prefix_groups.values())  # noqa: E501
            self.stdout.write(f"  Would create {variant_count} individual parent products, one for each variant")  # noqa: E501
