"""Management command for setting up inventory sync mapping."""

import logging
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Set up inventory sync mapping."""

    help = "Set up sync mapping for inventory components"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up inventory sync mapping...")

        # Load sync configuration
        config_path = (
            Path(settings.BASE_DIR).parent
            / "pyerp"
            / "sync"
            / "config"
            / "inventory_sync.yaml"
        )
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.stderr.write(f"Failed to load sync configuration: {e}")
            return

        # Process each component in the configuration
        for component_key, component_config in config.items():
            if component_key.startswith("_"):
                # Skip metadata entries
                continue

            self.stdout.write(f"\nSetting up {component_key} sync...")
            self._setup_component_sync(component_key, component_config)

        self.stdout.write(
            self.style.SUCCESS("Inventory sync mapping setup completed successfully")
        )

    def _setup_component_sync(self, component_key: str, config: dict) -> None:
        """Set up sync mapping for a component.

        Args:
            component_key: Key identifying the component
            config: Configuration dictionary for the component
        """
        # Create or update source
        source_name = config.get("name", f"{component_key}_sync")
        source_config = config.get("source", {}).get("config", {})
        source_type = config.get("source", {}).get("type", "legacy_api")

        # Add source type to config
        source_config["type"] = source_type

        # Add extractor class to config if present
        extractor_class = config.get("source", {}).get("extractor_class")
        if extractor_class:
            source_config["extractor_class"] = extractor_class

        source, created = SyncSource.objects.update_or_create(
            name=source_name,
            defaults={
                "description": config.get("description", ""),
                "config": source_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync source: {source}")
        else:
            self.stdout.write(f"Updated sync source: {source}")

        # Create or update target
        target_config = config.get("loader", {}).get("config", {})
        app_name = target_config.get("app_name", "inventory")
        model_name = target_config.get("model_name", component_key.title())
        target_name = f"{app_name}.{model_name}"

        # Add loader class to target config if present
        loader_class = config.get("loader", {}).get("class")
        if loader_class:
            target_config["loader_class"] = loader_class

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
        transformer_config = config.get("transformer", {})
        transformer_class = transformer_config.get("class")

        # Create transformation section with transformer class and config
        transformation = {
            "transformer_class": transformer_class,
            "config": transformer_config.get("config", {}),
            "type": transformer_config.get("type", "custom"),
        }

        mapping_config = {
            "transformation": transformation,
            "scheduling": config.get("schedule", {}),
            "incremental": config.get("incremental", {}),
            "dependencies": config.get("dependencies", []),
        }

        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type=component_key,
            defaults={
                "mapping_config": mapping_config,
                "active": True,
            },
        )

        if created:
            self.stdout.write(f"Created sync mapping for {component_key}: {mapping}")
        else:
            self.stdout.write(f"Updated sync mapping for {component_key}: {mapping}")
