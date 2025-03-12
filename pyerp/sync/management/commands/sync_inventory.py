"""Management command for synchronizing inventory data."""

import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize inventory data from legacy system."""

    help = 'Synchronize inventory data from legacy system'

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--component",
            type=str,
            choices=[
                "storage_locations", 
                "box_types", 
                "boxes", 
                "box_slots", 
                "product_storage"
            ],
            help="Specific inventory component to sync",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified in the last N days",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sync instead of incremental",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_true",
            default=False,
            help="Fail if date filter doesn't work (default: don't fail)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options['debug']:
            logger.setLevel(logging.DEBUG)
            
        # Get component to sync
        component = options['component']
        
        # Get mappings to process
        mappings = self._get_mappings(component)
        
        if not mappings:
            self.stdout.write(
                self.style.WARNING("No active inventory mappings found")
            )
            return
            
        # Build query parameters
        query_params = self._build_query_params(options)
        
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
                    query_params=query_params,
                    fail_on_filter_error=options['fail_on_filter_error']
                )
                
                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds()
                
                # Report results
                if sync_log.status == 'completed':
                    success_msg = (
                        f"Sync completed successfully in {duration:.2f} seconds"
                    )
                    self.stdout.write(self.style.SUCCESS(success_msg))
                elif sync_log.status == 'partial':
                    warning_msg = (
                        f"Sync completed with some errors in {duration:.2f} seconds"
                    )
                    self.stdout.write(self.style.WARNING(warning_msg))
                else:
                    error_msg = f"Sync failed in {duration:.2f} seconds"
                    self.stdout.write(self.style.ERROR(error_msg))
                
                self.stdout.write("\nStatistics:")
                self.stdout.write(f"  Processed: {sync_log.records_processed}")
                self.stdout.write(f"  Succeeded: {sync_log.records_succeeded}")
                self.stdout.write(f"  Failed: {sync_log.records_failed}")
                
                if sync_log.error_message:
                    self.stdout.write(
                        self.style.ERROR(f"\nError: {sync_log.error_message}")
                    )
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Sync failed: {str(e)}"))
                if options['debug']:
                    import traceback
                    traceback.print_exc()
    
    def _get_mappings(self, component=None):
        """Get inventory mappings based on filter criteria."""
        # Start with all active inventory mappings
        mappings = SyncMapping.objects.filter(active=True)
        
        # Filter by entity type if component is specified
        if component:
            mappings = mappings.filter(entity_type=component)
        else:
            # Get all inventory-related mappings
            inventory_components = [
                'storage_locations', 
                'box_types', 
                'boxes', 
                'box_slots', 
                'product_storage'
            ]
            mappings = mappings.filter(entity_type__in=inventory_components)
            
        return list(mappings)
    
    def _build_query_params(self, options):
        """Build query parameters from command options."""
        query_params = {}
        
        # Add date filter if days option is provided
        if options.get('days'):
            days = options['days']
            modified_since = timezone.now() - timedelta(days=days)
            
            # Format date for filter
            date_str = modified_since.strftime('%Y-%m-%d')
            query_params['modified_date'] = {'gt': date_str}
            
            filter_msg = f"Filtering records modified since {date_str}"
            self.stdout.write(f"{filter_msg} ({days} days ago)")
            
        return query_params 