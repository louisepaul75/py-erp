"""Create sync mappings from YAML configuration."""

import yaml
from pathlib import Path
from django.core.management.base import BaseCommand

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


class Command(BaseCommand):
    """Django management command to create sync mappings from YAML configuration."""

    help = "Create sync mappings from YAML configuration files"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--config-dir",
            type=str,
            default="pyerp/sync/config",
            help="Directory containing sync configuration files",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        config_dir = Path(options["config_dir"])
        self.stdout.write(f"Loading configurations from {config_dir}")

        # Process each YAML file in the config directory
        for config_file in config_dir.glob("*.yaml"):
            self.stdout.write(f"Processing {config_file}")

            try:
                with open(config_file) as f:
                    config = yaml.safe_load(f)

                # Process each component in the configuration
                for component_name, component_config in config.items():
                    # Skip metadata entries (those starting with _)
                    if component_name.startswith("_"):
                        continue

                    self.stdout.write(f"\nProcessing component: {component_name}")

                    try:
                        # Get or create source
                        source_config = component_config.get("source", {})
                        source_name = f"{config_file.stem}_{component_name}"
                        source, created = SyncSource.objects.get_or_create(
                            name=source_name,
                            defaults={
                                "description": component_config.get("description", ""),
                                "config": source_config,
                                "active": True,
                            },
                        )
                        if created:
                            self.stdout.write(f"Created source: {source}")
                        else:
                            self.stdout.write(f"Using existing source: {source}")

                        # Get or create target from loader configuration
                        loader_config = component_config.get("loader", {}).get(
                            "config", {}
                        )
                        app_name = loader_config.get("app_name")
                        model_name = loader_config.get("model_name")

                        # Skip if target configuration is missing required fields
                        if not app_name or not model_name:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Skipping target creation for {component_name} - "
                                    f"Missing app_name or model_name in loader configuration"
                                )
                            )
                            continue

                        target_name = f"{app_name}.{model_name}"
                        target, created = SyncTarget.objects.get_or_create(
                            name=target_name,
                            defaults={
                                "description": f"Target for {component_name}",
                                "config": loader_config,
                                "active": True,
                            },
                        )
                        if created:
                            self.stdout.write(f"Created target: {target}")
                        else:
                            self.stdout.write(f"Using existing target: {target}")

                        # Create mapping configuration
                        transformer_config = component_config.get("transformer", {})
                        mapping_config = {
                            "field_mappings": transformer_config.get("config", {}).get(
                                "field_mappings", {}
                            ),
                            "validation_rules": transformer_config.get(
                                "config", {}
                            ).get("validation_rules", []),
                            "custom_transformers": transformer_config.get(
                                "config", {}
                            ).get("custom_transformers", []),
                            "transformer_class": transformer_config.get("class"),
                            "transform_method": transformer_config.get(
                                "config", {}
                            ).get("transform_method"),
                            "lookups": transformer_config.get("config", {}).get(
                                "lookups", {}
                            ),
                            "composite_key": transformer_config.get("config", {}).get(
                                "composite_key"
                            ),
                        }

                        mapping, created = SyncMapping.objects.get_or_create(
                            source=source,
                            target=target,
                            entity_type=component_name,
                            defaults={"mapping_config": mapping_config, "active": True},
                        )
                        if created:
                            self.stdout.write(f"Created mapping: {mapping}")
                        else:
                            self.stdout.write(f"Using existing mapping: {mapping}")

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error processing component {component_name}: {e}"
                            )
                        )
                        continue

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {config_file}: {e}")
                )
                continue

        self.stdout.write(self.style.SUCCESS("Finished creating sync mappings"))
