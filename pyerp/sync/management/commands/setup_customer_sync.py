"""Management command for setting up customer sync mapping."""

import logging
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Set up customer sync mapping."""

    help = "Set up sync mapping for customers"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up customer sync mapping...")

        # Load sync configuration
        config_path = (
            Path(__file__).resolve().parent.parent.parent
            / "config"
            / "customers_sync.yaml"
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

        # Set up customer sync
        self._setup_customer_sync(config)

        # Set up address sync
        self._setup_address_sync(config)

    def _setup_customer_sync(self, config: dict) -> None:
        """Set up customer sync mapping.

        Args:
            config: Configuration dictionary
        """
        # Get customer configuration
        customer_config = config.get("customers", {})
        if not customer_config:
            self.stderr.write("No customer configuration found")
            return

        # Create or update source
        source_name = customer_config.get("name", "customers_sync")
        source_config = customer_config.get("source", {})
        source, created = SyncSource.objects.update_or_create(
            name=source_name,
            defaults={
                "description": customer_config.get("description", ""),
                "config": source_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync source: {source}")
        else:
            self.stdout.write(f"Updated sync source: {source}")

        # Create or update target
        target_config = customer_config.get("loader", {}).get("config", {})
        app_name = target_config.get("app_name", "sales")
        model_name = target_config.get("model_name", "Customer")
        target_name = f"{app_name}.{model_name}"
        target, created = SyncTarget.objects.update_or_create(
            name=target_name,
            defaults={
                "description": f"Target for {source_name}",
                "config": target_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync target: {target}")
        else:
            self.stdout.write(f"Updated sync target: {target}")

        # Create or update mapping
        mapping_config = {
            "transformation": customer_config.get("transformer", {}),
            "scheduling": customer_config.get("schedule", {}),
            "incremental": customer_config.get("incremental", {}),
        }
        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type="customer",
            defaults={
                "mapping_config": mapping_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync mapping: {mapping}")
        else:
            self.stdout.write(f"Updated sync mapping: {mapping}")

        self.stdout.write(
            self.style.SUCCESS("Customer sync mapping setup completed successfully")
        )

    def _setup_address_sync(self, config: dict) -> None:
        """Set up address sync mapping.

        Args:
            config: Configuration dictionary
        """
        # Create or update source for addresses
        source_name = "customers_sync_addresses"
        source_config = config.get("addresses", {}).get("source", {})
        source, created = SyncSource.objects.update_or_create(
            name=source_name,
            defaults={
                "description": "Synchronize customer addresses from legacy system",
                "config": source_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync source: {source}")
        else:
            self.stdout.write(f"Updated sync source: {source}")

        # Create or update target for addresses
        target_config = config.get("addresses", {}).get("target", {})
        app_name = target_config.get("app_name", "sales")
        model_name = target_config.get("model_name", "Address")
        target_name = f"{app_name}.{model_name}"
        target, created = SyncTarget.objects.update_or_create(
            name=target_name,
            defaults={
                "description": f"Target for {source_name}",
                "config": target_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync target: {target}")
        else:
            self.stdout.write(f"Updated sync target: {target}")

        # Create or update mapping for addresses
        mapping_config = {
            "transformation": config.get("addresses", {}).get("transformation", {}),
            "scheduling": config.get("addresses", {}).get("scheduling", {}),
            "incremental": config.get("addresses", {}).get("incremental", {}),
        }
        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type="address",
            defaults={
                "mapping_config": mapping_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync mapping: {mapping}")
        else:
            self.stdout.write(f"Updated sync mapping: {mapping}")

        self.stdout.write(
            self.style.SUCCESS("Address sync mapping setup completed successfully")
        )
