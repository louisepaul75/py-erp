"""Management command to fix customer sync mapping configuration."""

from django.core.management.base import BaseCommand
from pyerp.sync.models import SyncMapping


class Command(BaseCommand):
    """Management command to fix the customer sync mapping configuration."""

    help = "Fix the customer sync mapping configuration by setting required config values"

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Looking for customer sync mapping...")
        
        try:
            # First try with the exact entity_type
            customer_mapping = SyncMapping.objects.get(entity_type='customer')
        except SyncMapping.DoesNotExist:
            # If not found, try to look for any mapping that might be for customers
            customer_mappings = SyncMapping.objects.filter(entity_type__icontains='customer')
            if not customer_mappings.exists():
                self.stdout.write(self.style.ERROR("No customer sync mappings found."))
                return
            customer_mapping = customer_mappings.first()
        
        self.stdout.write(f"Found mapping: {customer_mapping}")
        
        # Get the current source config
        source = customer_mapping.source
        source_config = source.config
        
        self.stdout.write(f"Current source config: {source_config}")
        
        # Make a copy of the config
        new_config = source_config.copy()
        
        # Ensure we have a config key
        if 'config' not in new_config:
            new_config['config'] = {}
        
        # Update the config with environment and table_name directly in the config section
        new_config['config']['environment'] = 'live'
        new_config['config']['table_name'] = 'Kunden'
        
        self.stdout.write(f"Updated source config: {new_config}")
        
        # Save the updated config
        source.config = new_config
        source.save()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated customer sync mapping with ID {customer_mapping.id}!"
            )
        ) 