"""Management command to synchronize sales records from legacy ERP."""

import json
import yaml
import os
from pathlib import Path
from datetime import timedelta, datetime
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger
from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget
from pyerp.sync.pipeline import PipelineFactory


logger = get_logger(__name__)


class Command(BaseCommand):
    """Command to synchronize sales records from legacy ERP."""
    
    help = 'Synchronize sales records from legacy ERP'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = time.time()
        self.config = None
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--component',
            type=str,
            choices=['sales_records', 'sales_record_items', 'sales_record_sync'],
            help='Specific sales component to sync',
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform a full sync instead of incremental',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of records to sync',
        )
        parser.add_argument(
            '--filters',
            type=str,
            help='JSON string with additional filters to apply',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug mode with additional logging',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Only sync records modified in the last N days',
        )
    
    def handle(self, *args, **options):
        """Handle the sync_sales_records command."""
        try:
            # Load configuration
            self.config = self._load_config()
            
            # Get debug flag
            debug = options.get('debug', False)
            
            # Get components to sync
            components = self.config.get('sales_record_sync', {}).get('components', [])
            if not components:
                raise CommandError("No components found in configuration")
            
            # Add default date filter for records from last 5 years
            default_date = datetime.now() - timedelta(days=365 * 5)
            self.stdout.write(f"Adding default date filter: records from {default_date.date()} (last 5 years)")
            
            # Sync each component
            for component_name in components:
                self.stdout.write(f"Syncing {component_name}...")
                
                # Get or create mapping
                mapping = self._get_or_create_mapping(component_name)
                
                # Run sync
                self._run_sync(mapping, debug=debug)
                
            self.stdout.write(f"Sales record sync completed in {time.time() - self.start_time:.2f} seconds")
            
        except Exception as e:
            self.stderr.write(f"Error running sync: {str(e)}")
            if options.get('debug'):
                import traceback
                traceback.print_exc()
            raise
    
    def _load_config(self):
        """Load the sync configuration from YAML."""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'sales_record_sync.yaml'
        if not os.path.exists(config_path):
            raise CommandError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise CommandError(f"Error loading configuration: {e}")
    
    def _build_query_params(self, options):
        """Build query parameters from command options."""
        query_params = {}
        
        # Parse filters if provided
        if options['filters']:
            try:
                filters = json.loads(options['filters'])
                query_params.update(filters)
            except json.JSONDecodeError:
                raise CommandError('Invalid JSON format for filters')
        
        # Add limit to filters if specified
        if options['limit']:
            query_params['$top'] = options['limit']
        
        # Add date filter if days option is provided
        if options['days']:
            days = options['days']
            modified_since = timezone.now() - timedelta(days=days)
            
            # Format date for filter
            date_str = modified_since.strftime('%Y-%m-%d')
            query_params['modified_date'] = {'gt': date_str}
            
            self.stdout.write(f"Filtering records modified since {date_str} ({days} days ago)")
        # Add default date filter for incremental sync (last 5 years)
        elif not options['full'] and 'Datum' not in query_params:
            five_years_ago = timezone.now() - timedelta(days=5*365)
            date_str = five_years_ago.strftime('%Y-%m-%d')
            query_params['Datum'] = {'gt': date_str}
            self.stdout.write(f"Adding default date filter: records from {date_str} (last 5 years)")
            
        return query_params
    
    def _get_or_create_mapping(self, mapping_name: str) -> SyncMapping:
        """Get or create a sync mapping for the given name."""
        try:
            # Get mapping configuration from YAML
            mapping_config = self.config.get(mapping_name)
            if not mapping_config:
                raise CommandError(f"No configuration found for mapping {mapping_name}")

            # Get source configuration
            source_config = mapping_config.get('source', {})
            source_config['table_name'] = source_config.get('config', {}).get('table_name')

            # Get transformer configuration
            transformer_config = mapping_config.get('transformer', {})
            transformer_config.update(transformer_config.get('config', {}))

            # Get target configuration
            target_config = mapping_config.get('loader', {})
            target_config.update(target_config.get('config', {}))

            # Debug output
            self.stdout.write(f"Transformer class: {transformer_config.get('class')}")
            self.stdout.write(f"Mapping config: {mapping_config}")

            # Create or get source
            source_defaults = {
                'description': f"Source for {mapping_name}",
                'config': {
                    'type': source_config.get('type', 'legacy_api'),
                    'page_size': source_config.get('config', {}).get('page_size', 100),
                    'table_name': source_config.get('table_name'),
                    'environment': source_config.get('config', {}).get('environment', 'live'),
                    'extractor_class': source_config.get('extractor_class')
                }
            }
            source, _ = SyncSource.objects.get_or_create(
                name=source_config.get('type', 'legacy_api'),
                defaults=source_defaults
            )
            if not _:
                source.config.update(source_defaults['config'])
                source.save()

            # Create or get target
            target_defaults = {
                'description': f"Target for {mapping_name}",
                'config': {
                    'app_name': target_config.get('app_name'),
                    'model_name': target_config.get('model_name'),
                    'parent_field': target_config.get('parent_field'),
                    'unique_field': target_config.get('unique_field'),
                    'parent_mapping': target_config.get('parent_mapping'),
                    'update_strategy': target_config.get('update_strategy'),
                    'loader_class': target_config.get('class')
                }
            }
            target, _ = SyncTarget.objects.get_or_create(
                name=target_config.get('type', 'django_model'),
                defaults=target_defaults
            )
            if not _:
                target.config.update(target_defaults['config'])
                target.save()

            # Create or get mapping
            mapping_defaults = {
                'active': True,
                'mapping_config': {
                    'transformer_class': transformer_config.get('class'),
                    'transform_method': transformer_config.get('transform_method'),
                    'model_path': f"pyerp.business_modules.{target_config.get('app_name')}.models.{target_config.get('model_name')}",
                    'source_table': source_config.get('table_name'),
                    'field_mappings': transformer_config.get('field_mappings', {}),
                    'lookups': transformer_config.get('lookups', {}),
                    'composite_key': transformer_config.get('composite_key')
                }
            }
            mapping, created = SyncMapping.objects.get_or_create(
                entity_type=mapping_name,
                source=source,
                target=target,
                defaults=mapping_defaults
            )
            if not created:
                mapping.mapping_config.update(mapping_defaults['mapping_config'])
                mapping.save()

            return mapping

        except Exception as e:
            raise CommandError(f"Error creating mapping for {mapping_name}: {str(e)}")
    
    def _run_sync(self, mapping, incremental=True, batch_size=100, query_params=None, debug=False):
        """Run sync for a specific mapping."""
        try:
            # Create pipeline
            pipeline = PipelineFactory.create_pipeline(mapping)
            
            # Run sync
            sync_log = pipeline.run(
                incremental=incremental,
                batch_size=batch_size,
                query_params=query_params,
            )
            
            # Output results
            if sync_log.status == 'completed':
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully synced {sync_log.records_succeeded} records'
                    )
                )
            elif sync_log.status == 'partial':
                self.stdout.write(
                    self.style.WARNING(
                        f'Partially synced records: {sync_log.records_succeeded} succeeded, '
                        f'{sync_log.records_failed} failed'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to sync records: {sync_log.error_message}'
                    )
                )
                if debug:
                    self.stdout.write(sync_log.trace)
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error running sync: {e}")
            )
            if debug:
                import traceback
                self.stdout.write(traceback.format_exc()) 