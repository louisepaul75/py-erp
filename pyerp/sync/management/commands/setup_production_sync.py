"""
Management command to set up production sync configuration.

This command creates the necessary SyncSource, SyncTarget, and SyncMapping records
for synchronizing production data from the legacy ERP system.
"""

import os
import yaml
from typing import Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pyerp.utils.logging import get_logger

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget


logger = get_logger(__name__)


class Command(BaseCommand):
    """Command to set up production sync configuration."""

    help = "Set up production data sync configuration"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--source",
            type=str,
            default="legacy_erp",
            help="Name for the source system",
        )
        parser.add_argument(
            "--target",
            type=str,
            default="pyerp",
            help="Name for the target system",
        )
        parser.add_argument(
            "--config-file",
            type=str,
            help="Path to YAML config file (defaults to standard location)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Execute the command."""
        source_name = options["source"]
        target_name = options["target"]
        config_file = options["config_file"]

        try:
            # Load configuration
            config = self._load_config(config_file)
            if not config:
                raise CommandError("Failed to load configuration")

            # Create or get source and target
            source, _ = SyncSource.objects.get_or_create(
                name=source_name,
                defaults={
                    "description": "Legacy ERP Production Data",
                    "config": {"environment": "live"},
                },
            )
            self.stdout.write(f"Source: {source}")

            target, _ = SyncTarget.objects.get_or_create(
                name=target_name,
                defaults={
                    "description": "pyERP Production Data",
                    "config": {},
                },
            )
            self.stdout.write(f"Target: {target}")

            # Create mappings
            mappings_created = 0
            for mapping_config in config.get("mappings", []):
                entity_type = mapping_config.get("entity_type")
                if not entity_type:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping mapping without entity_type")
                    )
                    continue

                mapping, created = SyncMapping.objects.update_or_create(
                    source=source,
                    target=target,
                    entity_type=entity_type,
                    defaults={
                        "mapping_config": mapping_config.get("mapping_config", {}),
                        "active": True,
                    },
                )

                action = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(f"{action} mapping for {entity_type}")
                )
                mappings_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully set up {mappings_created} production sync mappings"
                )
            )

        except Exception as e:
            logger.error(f"Failed to set up production sync: {e}", exc_info=True)
            raise CommandError(f"Setup failed: {e}")

    def _load_config(self, config_file: Optional[str] = None) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_file: Optional path to config file. If not provided,
                         uses the default production_sync.yaml location.

        Returns:
            Dict containing the configuration
        """
        if not config_file:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "config",
                "production_sync.yaml",
            )

        try:
            self.stdout.write(f"Loading config from {config_file}")
            with open(config_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to load config: {e}"))
            logger.error(f"Failed to load config: {e}", exc_info=True)
            return {} 