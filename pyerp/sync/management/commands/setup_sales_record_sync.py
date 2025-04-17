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
        """Create or update a sync mapping from configuration."""
        try:
            # Check for existing mappings
            existing_mappings = SyncMapping.objects.filter(entity_type=entity_type)
            existing_count = existing_mappings.count()

            if existing_count > 0:
                if not force:
                    if existing_count == 1:
                        # Return the single existing mapping if not forcing recreation
                        self.stdout.write(
                            f"Mapping for {entity_type} already exists (ID: {existing_mappings.first().id}). Use --force to recreate."
                        )
                        return existing_mappings.first()
                    else:
                        # Multiple mappings exist, and we are not forcing. This is ambiguous.
                        self.stdout.write(
                            self.style.WARNING(
                                f"Multiple ({existing_count}) mappings found for {entity_type}. "
                                f"Cannot return a single mapping. Use --force to delete and recreate."
                            )
                        )
                        # Raise an error or return None depending on desired behavior.
                        # Raising error to prevent unexpected behavior.
                        raise CommandError(f"Ambiguous state: {existing_count} mappings found for {entity_type} without --force.")
                else:
                    # Force is True, delete all existing mappings for this entity type
                    self.stdout.write(f"--force specified. Deleting {existing_count} existing mapping(s) for {entity_type}...")
                    deleted_count, _ = existing_mappings.delete()
                    self.stdout.write(f"Deleted {deleted_count} mapping(s).")
            # else: existing_count == 0 - proceed to create

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

            # Create or update source (using update_or_create for idempotency)
            source_name = f"legacy_erp_{entity_type}" # Use unique name
            source_defaults = {
                "description": f"Legacy ERP source for {entity_type}", # Updated description
                "config": {
                    "environment": source_config.get("config", {}).get(
                        "environment", "live"
                    ),
                    "table_name": source_config.get("config", {}).get("table_name"),
                    "page_size": source_config.get("config", {}).get("page_size", 100),
                    "extractor_class": source_config.get("extractor_class"),
                },
                "active": True, # Ensure source is active
            }
            source, created = SyncSource.objects.update_or_create(
                name=source_name, # Use unique name here
                defaults=source_defaults
            )
            # If the source was not created (i.e., it existed), ensure its config is updated
            if not created:
                # Compare and update only if necessary, or just update directly
                # Direct update is simpler here
                source.config = source_defaults["config"]
                source.description = source_defaults["description"] # Also update description
                source.active = source_defaults["active"]
                source.save(update_fields=["config", "description", "active"])
                action = "Updated"
            else:
                action = "Created"
            self.stdout.write(f"{action} source '{source.name}'.")

            # Create or update target (using update_or_create for idempotency)
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
                "active": True, # Ensure target is active
            }
            target, created = SyncTarget.objects.update_or_create(
                name="pyerp", # Assuming name identifies the target uniquely
                defaults=target_defaults
            )
            # If the target was not created, ensure its config is updated
            if not created:
                target.config = target_defaults["config"]
                target.description = target_defaults["description"]
                target.active = target_defaults["active"]
                target.save(update_fields=["config", "description", "active"])
                action = "Updated"
            else:
                action = "Created"
            self.stdout.write(f"{action} target '{target.name}'.")

            # Create the new mapping
            self.stdout.write(f"Creating new mapping for {entity_type}...")
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
                # Include loader_config directly in mapping_config as well?
                # Some pipeline logic might expect it there.
                "loader_config": loader_config.get("config", {}),
            }

            mapping = SyncMapping.objects.create(
                entity_type=entity_type,
                source=source,
                target=target,
                mapping_config=mapping_config,
                active=True, # Ensure the new mapping is active
            )
            self.stdout.write(f"Successfully created new mapping ID: {mapping.id}")
            return mapping

        except Exception as e:
            logger.error(f"Error creating mapping for {entity_type}: {e}", exc_info=True)
            raise CommandError(f"Error creating mapping for {entity_type}: {str(e)}")
