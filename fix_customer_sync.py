#!/usr/bin/env python
"""Script to fix the customer sync mapping configuration

This script uses the Django management command framework to ensure proper
initialization of the Django environment.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line


class Command:
    """Fix customer sync mappings."""

    def handle(self):
        """Fix the customer sync mapping by updating the source config."""
        try:
            from pyerp.sync.models import SyncMapping
            
            print("Looking for customer sync mapping...")
            
            try:
                # First try with the exact entity_type
                customer_mapping = SyncMapping.objects.get(entity_type='customer')
            except SyncMapping.DoesNotExist:
                # If not found, try to look for any mapping that might be for customers
                customer_mappings = SyncMapping.objects.filter(entity_type__icontains='customer')
                if not customer_mappings.exists():
                    print("No customer sync mappings found.")
                    return
                customer_mapping = customer_mappings.first()
            
            print(f"Found mapping: {customer_mapping}")
            
            # Get the current source config
            source = customer_mapping.source
            source_config = source.config
            
            print(f"Current source config: {source_config}")
            
            # Make a copy of the config
            new_config = source_config.copy()
            
            # Update the config with environment and table_name directly in the config section
            if 'config' in new_config:
                new_config['config']['environment'] = 'live'
                new_config['config']['table_name'] = 'Kunden'
            else:
                new_config['config'] = {
                    'environment': 'live',
                    'table_name': 'Kunden'
                }
            
            print(f"Updated source config: {new_config}")
            
            # Save the updated config
            source.config = new_config
            source.save()
            
            print(f"Successfully updated customer sync mapping with ID {customer_mapping.id}!")
            
        except Exception as e:
            print(f"Error updating customer sync mapping: {e}")


def run():
    """Run as a Django management command."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings")
    
    # This will ensure the Django environment is properly initialized
    execute_from_command_line(["manage.py", "shell"])
    
    # Now run our command
    Command().handle()


if __name__ == "__main__":
    run() 