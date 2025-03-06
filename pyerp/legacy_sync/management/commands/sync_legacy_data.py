"""
Management command to synchronize data from the legacy ERP system.
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.legacy_sync.sync_tasks import (  # noqa: F401
    sync_products, sync_customers, sync_orders, sync_inventory,  # noqa: E128
    sync_variant_products, sync_entity
)
from pyerp.legacy_sync.models import EntityMappingConfig

 # Configure logging
logger = logging.getLogger(__name__)  # noqa: F841


class Command(BaseCommand):
    help = 'Synchronize data from the legacy ERP system'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument(
            '--entity',  # noqa: E128
            type=str,  # noqa: F841
            help='Entity type to synchronize (default: all)'  # noqa: F841
        )
        parser.add_argument(
            '--new-only',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Only synchronize new or modified records'  # noqa: F841
        )
        parser.add_argument(
            '--force',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Force synchronization even if there are errors'  # noqa: F841
        )
        parser.add_argument(
            '--list',  # noqa: E128
            action='store_true',  # noqa: F841
            help='List available entity types for synchronization'  # noqa: F841
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

        self.stdout.write(self.style.SUCCESS(f'Starting synchronization of {entity_type} data'))  # noqa: E501
        self.stdout.write(f'New only: {new_only}, Force: {force}')

        start_time = timezone.now()

        try:
            stats = sync_entity(entity_type, new_only=new_only)
            self.stdout.write(self.style.SUCCESS(
                f'{entity_type.capitalize()} synchronized: {stats["total_fetched"]} fetched, '  # noqa: E501
                f'{stats["created"]} created, {stats["updated"]} updated, '
                f'{stats["errors"]} errors'
            ))

            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            self.stdout.write(self.style.SUCCESS(f'Synchronization completed in {duration:.2f} seconds'))  # noqa: E501

        except Exception as e:
            if force:
                self.stdout.write(self.style.WARNING(f'Error during synchronization: {e}'))  # noqa: E501
                self.stdout.write(self.style.WARNING('Continuing due to --force flag'))  # noqa: E501
            else:
                self.stdout.write(self.style.ERROR(f'Error during synchronization: {e}'))  # noqa: E501
                raise CommandError(f'Synchronization failed: {e}')

    def sync_all(self, new_only, force):
        """
        Synchronize all active entity types.
        """
        self.stdout.write(self.style.SUCCESS('Starting synchronization of all entity types'))  # noqa: E501
        self.stdout.write(f'New only: {new_only}, Force: {force}')

        start_time = timezone.now()

 # Get all active entity types
        entity_types = EntityMappingConfig.objects.filter(is_active=True).values_list('entity_type', flat=True)  # noqa: E501

        if not entity_types:
            self.stdout.write(self.style.WARNING('No active entity types found for synchronization'))  # noqa: E501
            return

        self.stdout.write(f'Found {len(entity_types)} active entity types: {", ".join(entity_types)}')  # noqa: E501

        success_count = 0
        error_count = 0

        for entity_type in entity_types:
            try:
                self.stdout.write(f'Synchronizing {entity_type}...')
                stats = sync_entity(entity_type, new_only=new_only)
                self.stdout.write(self.style.SUCCESS(
                    f'{entity_type.capitalize()} synchronized: {stats["total_fetched"]} fetched, '  # noqa: E501
                    f'{stats["created"]} created, {stats["updated"]} updated, '
                    f'{stats["errors"]} errors'
                ))
                success_count += 1
            except Exception as e:
                error_count += 1
                if force:
                    self.stdout.write(self.style.WARNING(f'Error during {entity_type} synchronization: {e}'))  # noqa: E501
                    self.stdout.write(self.style.WARNING('Continuing due to --force flag'))  # noqa: E501
                else:
                    self.stdout.write(self.style.ERROR(f'Error during {entity_type} synchronization: {e}'))  # noqa: E501
                    raise CommandError(f'Synchronization failed: {e}')

        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        self.stdout.write(self.style.SUCCESS(
            f'Synchronization completed in {duration:.2f} seconds. '  # noqa: E128
            f'Success: {success_count}, Errors: {error_count}'
        ))

    def list_entity_types(self):
        """
        List all available entity types for synchronization.
        """
        self.stdout.write(self.style.SUCCESS('Available entity types for synchronization:'))  # noqa: E501

        entity_configs = EntityMappingConfig.objects.all().order_by('entity_type')  # noqa: E501

        if not entity_configs:
            self.stdout.write(self.style.WARNING('No entity mapping configurations found'))  # noqa: E501
            return

        for config in entity_configs:
            status = 'ACTIVE' if config.is_active else 'INACTIVE'
            self.stdout.write(f'- {config.entity_type} ({status}): {config.legacy_table} -> {config.new_model}')  # noqa: E501
