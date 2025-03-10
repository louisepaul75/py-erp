"""Management command for running data synchronization tasks."""

import logging
import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.pipeline import PipelineFactory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run data synchronization tasks."""

    help = 'Run data synchronization tasks for specified mappings'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--mapping',
            type=int,
            help='ID of specific mapping to sync'
        )
        parser.add_argument(
            '--entity-type',
            help='Entity type to sync (e.g., product, customer)'
        )
        parser.add_argument(
            '--source',
            help='Source name to filter mappings'
        )
        parser.add_argument(
            '--target',
            help='Target name to filter mappings'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available mappings instead of running sync'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full sync instead of incremental'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Batch size for processing records'
        )
        parser.add_argument(
            '--filters',
            help='Additional filters in JSON format'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options['debug']:
            logger.setLevel(logging.DEBUG)
            
        # List mappings if requested
        if options['list']:
            self._list_mappings(
                source_name=options['source'],
                target_name=options['target'],
                entity_type=options['entity_type']
            )
            return
            
        # Get query parameters
        query_params = None
        if options['filters']:
            try:
                query_params = json.loads(options['filters'])
            except json.JSONDecodeError:
                raise CommandError("Invalid JSON format for filters")
                
        # Get mappings to process
        mappings = self._get_mappings(
            mapping_id=options['mapping'],
            source_name=options['source'],
            target_name=options['target'],
            entity_type=options['entity_type']
        )
        
        if not mappings:
            self.stdout.write(self.style.WARNING(
                "No active mappings found matching the criteria"
            ))
            return
            
        # Process each mapping
        for mapping in mappings:
            self.stdout.write(f"\nProcessing mapping: {mapping}")
            
            try:
                # Create and run pipeline
                pipeline = PipelineFactory.create_pipeline(mapping)
                
                start_time = timezone.now()
                self.stdout.write(f"Starting sync at {start_time}...")
                
                sync_log = pipeline.run(
                    incremental=not options['full'],
                    batch_size=options['batch_size'],
                    query_params=query_params
                )
                
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds()
                
                # Report results
                if sync_log.status == 'completed':
                    self.stdout.write(self.style.SUCCESS(
                        f"Sync completed successfully in {duration:.2f} seconds"
                    ))
                elif sync_log.status == 'partial':
                    self.stdout.write(self.style.WARNING(
                        f"Sync completed with some errors in {duration:.2f} seconds"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f"Sync failed in {duration:.2f} seconds"
                    ))
                
                self.stdout.write("\nStatistics:")
                self.stdout.write(f"  Processed: {sync_log.records_processed}")
                self.stdout.write(f"  Succeeded: {sync_log.records_succeeded}")
                self.stdout.write(f"  Failed: {sync_log.records_failed}")
                
                if sync_log.error_message:
                    self.stdout.write(self.style.ERROR(
                        f"\nError: {sync_log.error_message}"
                    ))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Sync failed: {str(e)}"))
                if options['debug']:
                    import traceback
                    traceback.print_exc()
    
    def _list_mappings(self, source_name=None, target_name=None, entity_type=None):
        """List available mappings."""
        mappings = self._get_mappings(
            source_name=source_name,
            target_name=target_name,
            entity_type=entity_type
        )
        
        if not mappings:
            self.stdout.write(self.style.WARNING(
                "No active mappings found matching the criteria"
            ))
            return
            
        self.stdout.write(self.style.SUCCESS(
            f"\nFound {len(mappings)} active mapping(s):"
        ))
        
        for mapping in mappings:
            self.stdout.write(
                f"\nID: {mapping.id}"
                f"\nEntity Type: {mapping.entity_type}"
                f"\nSource: {mapping.source.name}"
                f"\nTarget: {mapping.target.name}"
                f"\n{'-' * 40}"
            )
    
    def _get_mappings(self, mapping_id=None, source_name=None, 
                     target_name=None, entity_type=None):
        """Get mappings based on filter criteria."""
        mappings = SyncMapping.objects.filter(active=True)
        
        if mapping_id:
            mappings = mappings.filter(id=mapping_id)
            
        if source_name:
            mappings = mappings.filter(source__name=source_name)
            
        if target_name:
            mappings = mappings.filter(target__name=target_name)
            
        if entity_type:
            mappings = mappings.filter(entity_type=entity_type)
            
        return list(mappings) 