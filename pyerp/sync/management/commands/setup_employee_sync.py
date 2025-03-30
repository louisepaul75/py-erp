"""Management command for setting up employee sync mapping."""

import logging
import yaml
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Set up employee sync mapping."""

    help = "Set up sync mapping for employees"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Setting up employee sync mapping...")

        # Load sync configuration
        config_path = Path(settings.BASE_DIR) / "sync" / "config" / "business_sync.yaml"
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        except Exception as e:
            self.stderr.write(f"Failed to load sync configuration: {e}")
            return

        # Get employee configuration
        employee_config = config.get("employees", {})
        if not employee_config:
            self.stderr.write("No employee configuration found")
            return

        # Create or update source
        source_name = employee_config.get("name", "employees_sync")
        source_config = employee_config.get("source", {})
        
        # Ensure all required fields are in the source config
        source_config_dict = {
            "type": source_config.get("type", "legacy_api"),
            "extractor_class": source_config.get("extractor_class"),
            "environment": source_config.get("config", {}).get("environment"),
            "table_name": source_config.get("config", {}).get("table_name"),
            "filters": source_config.get("config", {}).get("filters", {}),
            "all_records": source_config.get("config", {}).get("all_records", True),
            "page_size": source_config.get("config", {}).get("page_size", 1000)
        }

        source, created = SyncSource.objects.update_or_create(
            name=source_name,
            defaults={
                "description": employee_config.get("description", ""),
                "config": source_config_dict,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync source: {source}")
        else:
            self.stdout.write(f"Updated sync source: {source}")

        # Create or update target
        loader_config = employee_config.get("loader", {})
        target_config = {
            "loader_class": loader_config.get("class"),
            "app_name": loader_config.get("config", {}).get("app_name", "business"),
            "model_name": loader_config.get("config", {}).get("model_name", "Employee"),
            "unique_field": loader_config.get("config", {}).get("unique_field", "employee_number"),
            "update_strategy": loader_config.get("config", {}).get("update_strategy", "newest_wins"),
        }
        target_name = f"{target_config['app_name']}.{target_config['model_name']}"

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
        transformer_config = employee_config.get("transformer", {})
        mapping_config = {
            "transformer_class": transformer_config.get("class"),
            "field_mappings": transformer_config.get("config", {}).get("field_mappings", {}),
            "validation_rules": transformer_config.get("config", {}).get("validation_rules", []),
            "transformation": {
                "type": transformer_config.get("type", "custom"),
                "config": transformer_config.get("config", {}),
                "field_mappings": transformer_config.get("config", {}).get("field_mappings", {}),
            },
            "scheduling": employee_config.get("schedule", {}),
            "incremental": employee_config.get("incremental", {}),
        }
        mapping, created = SyncMapping.objects.update_or_create(
            source=source,
            target=target,
            entity_type="employee",
            defaults={
                "mapping_config": mapping_config,
                "active": True,
            },
        )
        if created:
            self.stdout.write(f"Created sync mapping for employees: {mapping}")
        else:
            self.stdout.write(f"Updated sync mapping for employees: {mapping}")

        self.stdout.write(
            self.style.SUCCESS("Employee sync mapping setup completed successfully")
        ) 