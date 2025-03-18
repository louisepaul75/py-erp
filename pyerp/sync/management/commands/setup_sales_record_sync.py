"""Management command to set up sales record sync mappings."""

import os
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


class Command(BaseCommand):
    """Command to set up sales record sync mappings."""

    help = "Set up sales record sync mappings from configuration"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force recreation of existing mappings",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            # Load configuration
            config = self._load_config()
            if not config:
                raise CommandError("Failed to load sales record sync configuration")

            # Create mappings
            self.stdout.write("Setting up sales record sync mappings...")

            # Create sales record mapping
            sales_record_config = config.get("sales_records")
            if sales_record_config:
                sales_record_mapping = self._create_mapping(
                    "sales_records",
                    sales_record_config,
                    force=options.get("force", False),
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully set up sales_records mapping (ID: {sales_record_mapping.id})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "sales_records configuration not found in YAML file"
                    )
                )

            # Create sales record item mapping
            sales_record_item_config = config.get("sales_record_items")
            if sales_record_item_config:
                sales_record_item_mapping = self._create_mapping(
                    "sales_record_items",
                    sales_record_item_config,
                    force=options.get("force", False),
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully set up sales_record_items mapping (ID: {sales_record_item_mapping.id})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "sales_record_items configuration not found in YAML file"
                    )
                )

            self.stdout.write(
                self.style.SUCCESS("Sales record sync mappings set up successfully")
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Error setting up sales record sync mappings: {str(e)}"
                )
            )
            raise CommandError(f"Error setting up sales record sync mappings: {str(e)}")

    def _load_config(self):
        """Load the sync configuration from YAML."""
        config_path = (
            Path(__file__).parent.parent.parent / "config" / "sales_record_sync.yaml"
        )
        if not os.path.exists(config_path):
            raise CommandError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise CommandError(f"Error loading configuration: {e}")

    def _create_mapping(self, entity_type, config, force=False):
        """Create a sync mapping from configuration."""
        try:
            # Check if mapping already exists
            try:
                existing_mapping = SyncMapping.objects.get(entity_type=entity_type)
                if not force:
                    self.stdout.write(
                        f"Mapping for {entity_type} already exists (ID: {existing_mapping.id})"
                    )
                    return existing_mapping
                else:
                    self.stdout.write(f"Recreating mapping for {entity_type}")
                    existing_mapping.delete()
            except SyncMapping.DoesNotExist:
                pass

            # Get source configuration
            source_config = config.get("source", {})
            if not source_config:
                raise CommandError(f"Source configuration not found for {entity_type}")

            # Get transformer configuration
            transformer_config = config.get("transformer", {})
            if not transformer_config:
                raise CommandError(
                    f"Transformer configuration not found for {entity_type}"
                )

            # Get loader configuration
            loader_config = config.get("loader", {})
            if not loader_config:
                raise CommandError(f"Loader configuration not found for {entity_type}")

            # Create or get source
            source_defaults = {
                "description": f"Source for {entity_type}",
                "config": {
                    "environment": source_config.get("config", {}).get(
                        "environment", "live"
                    ),
                    "table_name": source_config.get("config", {}).get("table_name"),
                    "page_size": source_config.get("config", {}).get("page_size", 100),
                    "extractor_class": source_config.get("extractor_class"),
                },
                "active": True,
            }
            source, _ = SyncSource.objects.get_or_create(
                name="legacy_erp", defaults=source_defaults
            )
            if not _:
                source.config.update(source_defaults["config"])
                source.save()

            # Create or get target
            target_defaults = {
                "description": f"Target for {entity_type}",
                "config": {
                    "app_name": loader_config.get("config", {}).get("app_name"),
                    "model_name": loader_config.get("config", {}).get("model_name"),
                    "parent_field": loader_config.get("config", {}).get("parent_field"),
                    "unique_field": loader_config.get("config", {}).get("unique_field"),
                    "parent_mapping": loader_config.get("config", {}).get(
                        "parent_mapping"
                    ),
                    "update_strategy": loader_config.get("config", {}).get(
                        "update_strategy"
                    ),
                    "loader_class": loader_config.get("class"),
                },
                "active": True,
            }
            target, _ = SyncTarget.objects.get_or_create(
                name="pyerp", defaults=target_defaults
            )
            if not _:
                target.config.update(target_defaults["config"])
                target.save()

            # Create mapping
            mapping_config = {
                "transformer_class": transformer_config.get("class"),
                "transform_method": transformer_config.get("config", {}).get(
                    "transform_method"
                ),
                "model_path": f"pyerp.business_modules.{loader_config.get('config', {}).get('app_name')}.models.{loader_config.get('config', {}).get('model_name')}",
                "source_table": source_config.get("config", {}).get("table_name"),
                "field_mappings": transformer_config.get("config", {}).get(
                    "field_mappings", {}
                ),
                "lookups": transformer_config.get("config", {}).get("lookups", {}),
                "composite_key": transformer_config.get("config", {}).get(
                    "composite_key"
                ),
            }

            mapping = SyncMapping.objects.create(
                entity_type=entity_type,
                source=source,
                target=target,
                mapping_config=mapping_config,
                active=True,
            )

            return mapping

        except Exception as e:
            raise CommandError(f"Error creating mapping for {entity_type}: {str(e)}")
