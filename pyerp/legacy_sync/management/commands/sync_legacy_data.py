"""
Management command to synchronize data from the legacy ERP system.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.legacy_sync.sync_tasks import (
    sync_products, sync_customers, sync_orders, sync_inventory, 
    sync_variant_products, sync_entity
)
from pyerp.legacy_sync.models import EntityMappingConfig

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize data from the legacy ERP system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            type=str,
            help='Entity type to synchronize (default: all)'
        )
        parser.add_argument(
            '--new-only',
            action='store_true',
            help='Only synchronize new or modified records'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force synchronization even if there are errors'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available entity types for synchronization'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_entity_types()
            return
        
        entity_type = options['entity']
        new_only = options['new_only']
        force = options['force']
        
        # If no entity type is specified, sync all active entity types
        if not entity_type:
            self.sync_all(new_only, force)
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting synchronization of {entity_type} data'))
        self.stdout.write(f'New only: {new_only}, Force: {force}')
        
        start_time = timezone.now()
        
        try:
            # Use the generic sync_entity function
            stats = sync_entity(entity_type, new_only=new_only)
            self.stdout.write(self.style.SUCCESS(
                f'{entity_type.capitalize()} synchronized: {stats["total_fetched"]} fetched, '
                f'{stats["created"]} created, {stats["updated"]} updated, '
                f'{stats["errors"]} errors'
            ))
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(self.style.SUCCESS(f'Synchronization completed in {duration:.2f} seconds'))
            
        except Exception as e:
            if force:
                self.stdout.write(self.style.WARNING(f'Error during synchronization: {e}'))
                self.stdout.write(self.style.WARNING('Continuing due to --force flag'))
            else:
                self.stdout.write(self.style.ERROR(f'Error during synchronization: {e}'))
                raise CommandError(f'Synchronization failed: {e}')
    
    def sync_all(self, new_only, force):
        """
        Synchronize all active entity types.
        """
        self.stdout.write(self.style.SUCCESS('Starting synchronization of all entity types'))
        self.stdout.write(f'New only: {new_only}, Force: {force}')
        
        start_time = timezone.now()
        
        # Get all active entity types
        entity_types = EntityMappingConfig.objects.filter(is_active=True).values_list('entity_type', flat=True)
        
        if not entity_types:
            self.stdout.write(self.style.WARNING('No active entity types found for synchronization'))
            return
        
        self.stdout.write(f'Found {len(entity_types)} active entity types: {", ".join(entity_types)}')
        
        success_count = 0
        error_count = 0
        
        for entity_type in entity_types:
            try:
                self.stdout.write(f'Synchronizing {entity_type}...')
                stats = sync_entity(entity_type, new_only=new_only)
                self.stdout.write(self.style.SUCCESS(
                    f'{entity_type.capitalize()} synchronized: {stats["total_fetched"]} fetched, '
                    f'{stats["created"]} created, {stats["updated"]} updated, '
                    f'{stats["errors"]} errors'
                ))
                success_count += 1
            except Exception as e:
                error_count += 1
                if force:
                    self.stdout.write(self.style.WARNING(f'Error during {entity_type} synchronization: {e}'))
                    self.stdout.write(self.style.WARNING('Continuing due to --force flag'))
                else:
                    self.stdout.write(self.style.ERROR(f'Error during {entity_type} synchronization: {e}'))
                    raise CommandError(f'Synchronization failed: {e}')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(self.style.SUCCESS(
            f'Synchronization completed in {duration:.2f} seconds. '
            f'Success: {success_count}, Errors: {error_count}'
        ))
    
    def list_entity_types(self):
        """
        List all available entity types for synchronization.
        """
        self.stdout.write(self.style.SUCCESS('Available entity types for synchronization:'))
        
        entity_configs = EntityMappingConfig.objects.all().order_by('entity_type')
        
        if not entity_configs:
            self.stdout.write(self.style.WARNING('No entity mapping configurations found'))
            return
        
        for config in entity_configs:
            status = 'ACTIVE' if config.is_active else 'INACTIVE'
            self.stdout.write(f'- {config.entity_type} ({status}): {config.legacy_table} -> {config.new_model}') 