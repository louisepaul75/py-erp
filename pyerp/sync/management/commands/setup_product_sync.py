"""Management command for setting up product sync mapping."""

import logging
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Set up product sync mapping."""

    help = 'Set up sync mapping for products (parents and variants)'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up product sync mapping...")

        # Load sync configuration
        config_path = (
            Path(settings.BASE_DIR) / 'sync' / 'config' / 'products_sync.yaml'
        )
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.stderr.write(f"Failed to load sync configuration: {e}")
            return

        # Create or update source for parent products
        source_name = config.get('name', 'products_sync')
        source_config = config.get('source', {})
        source, created = SyncSource.objects.update_or_create(
            name=source_name,
            defaults={
                'description': config.get('description', ''),
                'config': source_config,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f"Created sync source: {source}")
        else:
            self.stdout.write(f"Updated sync source: {source}")

        # Create or update target for parent products
        target_config = config.get('target', {})
        app_name = target_config.get('app_name', 'products')
        model_name = target_config.get('model_name', 'ParentProduct')
        target_name = f"{app_name}.{model_name}"
        
        target, created = SyncTarget.objects.update_or_create(
            name=target_name,
            defaults={
                'description': f"Target for {source_name} parent products",
                'config': target_config,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f"Created sync target: {target}")
        else:
            self.stdout.write(f"Updated sync target: {target}")

        # Create or update mapping for parent products
        mapping_config = {
            'transformation': config.get('transformation', {}),
            'scheduling': config.get('scheduling', {}),
            'incremental': config.get('incremental', {}),
        }
        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type='parent_product',
            defaults={
                'mapping_config': mapping_config,
                'active': True,
            }
        )
        if created:
            self.stdout.write(
                f"Created sync mapping for parent products: {mapping}"
            )
        else:
            self.stdout.write(
                f"Updated sync mapping for parent products: {mapping}"
            )

        # Handle variant products if configured
        if 'variants' in config:
            variant_config = config.get('variants', {})
            variant_source_config = variant_config.get('source', {})
            
            # Create or update source for variant products
            variant_source, created = SyncSource.objects.update_or_create(
                name=f"{source_name}_variants",
                defaults={
                    'description': f"Variant products for {source_name}",
                    'config': variant_source_config,
                    'active': True,
                }
            )
            if created:
                self.stdout.write(
                    f"Created sync source for variants: {variant_source}"
                )
            else:
                self.stdout.write(
                    f"Updated sync source for variants: {variant_source}"
                )

            # Create or update target for variant products
            variant_target_name = "products.VariantProduct"
            loader_class = 'pyerp.sync.loaders.django_model.DjangoModelLoader'
            variant_target_config = {
                'loader_class': loader_class,
                'app_name': 'products',
                'model_name': 'VariantProduct',
                'unique_field': 'sku',
                'conflict_strategy': 'newest_wins',
            }
            
            target_desc = f"Target for {source_name} variant products"
            variant_target, created = SyncTarget.objects.update_or_create(
                name=variant_target_name,
                defaults={
                    'description': target_desc,
                    'config': variant_target_config,
                    'active': True,
                }
            )
            if created:
                self.stdout.write(
                    f"Created sync target for variants: {variant_target}"
                )
            else:
                self.stdout.write(
                    f"Updated sync target for variants: {variant_target}"
                )

            # Create or update mapping for variant products
            variant_mapping_config = {
                'transformation': variant_config.get('transformation', {}),
                'scheduling': config.get('scheduling', {}),
                'incremental': config.get('incremental', {}),
            }
            variant_mapping, created = SyncMapping.objects.update_or_create(
                source=variant_source,
                target=variant_target,
                entity_type='product_variant',
                defaults={
                    'mapping_config': variant_mapping_config,
                    'active': True,
                }
            )
            created_msg = "Created sync mapping for variant products: {0}"
            updated_msg = "Updated sync mapping for variant products: {0}"
            
            if created:
                self.stdout.write(created_msg.format(variant_mapping))
            else:
                self.stdout.write(updated_msg.format(variant_mapping))

        success_msg = "Product sync mapping setup completed successfully"
        self.stdout.write(self.style.SUCCESS(success_msg)) 