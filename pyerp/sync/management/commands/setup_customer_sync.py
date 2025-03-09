"""Management command for setting up customer sync mapping."""

import logging
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Set up customer sync mapping."""

    help = 'Set up sync mapping for customers'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up customer sync mapping...")

        # Load sync configuration
        config_path = (
            Path(__file__).resolve().parent.parent.parent /
            'config' / 'customer_sync.yaml'
        )
        self.stdout.write(f"Looking for config file at: {config_path}")
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.stderr.write(
                f"Failed to load sync configuration from {config_path}: {e}"
            )
            return

        # Create or update source
        source_name = config.get('name', 'customer_sync')
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

        # Create or update target
        target_config = config.get('target', {})
        target_name = (
            f"{target_config.get('app_name', 'business_modules.sales')}."
            f"{target_config.get('model_name', 'Customer')}"
        )
        target, created = SyncTarget.objects.update_or_create(
            name=target_name,
            defaults={
                'description': f"Target for {source_name}",
                'config': target_config,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f"Created sync target: {target}")
        else:
            self.stdout.write(f"Updated sync target: {target}")

        # Create or update mapping
        mapping_config = {
            'transformation': config.get('transformation', {}),
            'scheduling': config.get('scheduling', {}),
            'incremental': config.get('incremental', {}),
        }
        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type='customer',
            defaults={
                'mapping_config': mapping_config,
                'active': True,
            }
        )
        if created:
            self.stdout.write(f"Created sync mapping: {mapping}")
        else:
            self.stdout.write(f"Updated sync mapping: {mapping}")

        self.stdout.write(
            self.style.SUCCESS(
                "Customer sync mapping setup completed successfully"
            )
        ) 