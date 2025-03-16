"""Management command to synchronize sales records from legacy ERP."""

import json
import yaml
import os
from pathlib import Path
from datetime import timedelta, datetime
import time
import traceback

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget, SyncLog, SyncLogDetail
from pyerp.sync.pipeline import PipelineFactory
from pyerp.sync.extractors import LegacyAPIExtractor
from pyerp.sync.transformers import SalesRecordTransformer
from pyerp.sync.loaders import DjangoModelLoader


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
        """Command handler."""
        self.debug = options['debug']
        
        # First sync sales records
        self.stdout.write("Syncing sales records...")
        record_result = self._run_sync(
            'sales_records',
            self._build_query_params(options, component='sales_records'),
            options
        )
        
        # Check if we have synced_ids from the record_result
        synced_legacy_ids = []
        if record_result and 'synced_ids' in record_result and record_result['synced_ids']:
            synced_legacy_ids = record_result['synced_ids']
            self.stdout.write(f"Using {len(synced_legacy_ids)} synced legacy IDs for line items")
        else:
            # Fallback: Get all legacy IDs from the database
            from pyerp.business_modules.sales.models import SalesRecord
            synced_legacy_ids = list(SalesRecord.objects.values_list('legacy_id', flat=True))
            self.stdout.write(f"Using all {len(synced_legacy_ids)} legacy IDs from database for line items")
        
        if synced_legacy_ids:
            # Create filter query for line items
            line_items_params = self._build_query_params(options, component='sales_record_items')
            
            # Add the AbsNr filter directly in the format expected by the API client
            if 'filter_query' not in line_items_params:
                line_items_params['filter_query'] = []
            
            # Add the filter directly as a list with the 'in' operator
            line_items_params['filter_query'].append(['AbsNr', 'in', str(synced_legacy_ids)])
            
            self.stdout.write(f"Line items filter query: {line_items_params['filter_query']}")
            
            # Then sync sales record items
            self.stdout.write("Syncing sales record items...")
            self._run_sync(
                'sales_record_items',
                line_items_params,
                options
            )
        else:
            self.stdout.write("No sales records to sync line items for")
        
        self.stdout.write(self.style.SUCCESS("Sync completed"))
        return
    
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
    
    def _build_query_params(self, options, component=None):
        """Build query parameters from command options."""
        query_params = {}
        
        # Parse filters if provided
        if options['filters']:
            try:
                # Just pass the JSON string directly to the query_params
                query_params['filter_query'] = json.loads(options['filters'])
                self.stdout.write(f"Using filter_query: {query_params['filter_query']}")
            except json.JSONDecodeError:
                raise CommandError('Invalid JSON format for filters')
        
        # Add limit to filters if specified, but only for the main sales_records component
        if options['limit'] and (component is None or component == 'sales_records'):
            query_params['$top'] = options['limit']
        
        # Add date filter if days option is provided
        if options['days']:
            days = options['days']
            modified_since = timezone.now() - timedelta(days=days)
            
            # Format date for filter
            date_str = modified_since.strftime('%Y-%m-%d')
            
            # Add to filter_query
            if 'filter_query' not in query_params:
                query_params['filter_query'] = []
            
            # Add date filter directly
            query_params['filter_query'].append(['modified_date', '>', date_str])
            
            self.stdout.write(f"Filtering records modified since {date_str} ({days} days ago)")
        # Add default date filter for incremental sync (last 5 years)
        elif not options['full'] and not ('filter_query' in query_params and any(f[0] == 'Datum' for f in query_params['filter_query'])):
            five_years_ago = timezone.now() - timedelta(days=5*365)
            date_str = five_years_ago.strftime('%Y-%m-%d')
            
            # Add to filter_query
            if 'filter_query' not in query_params:
                query_params['filter_query'] = []
            
            # Add date filter directly
            query_params['filter_query'].append(['Datum', '>', date_str])
            
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
    
    def _run_sync(self, component, query_params, options):
        """Run the sync process for a component."""
        extractor = None
        try:
            # Get sync mapping
            mapping = self._get_sync_mapping(component)
            if not mapping:
                raise CommandError(f"{component} sync mapping not found")
            
            # Set up parameters
            batch_size = options.get('batch_size', 100)
            debug = options.get('debug', False)
            incremental = not options.get('full', False)
            
            # Log sync start
            self.stdout.write(f"Starting sync for {component}")
            self.stdout.write(f"Query params: {query_params}")
            
            # Create sync log
            sync_log = SyncLog.objects.create(
                mapping=mapping,
                status="started",
                is_full_sync=not incremental,
                sync_params=query_params
            )
            
            # Initialize counters
            records_processed = 0
            records_succeeded = 0
            records_failed = 0
            synced_ids = []
            
            # Get extractor
            extractor = LegacyAPIExtractor(
                config={
                    'environment': 'live',
                    'table_name': 'Belege' if component == 'sales_records' else 'Belege_Pos',
                    'page_size': batch_size
                }
            )
            # Establish connection to the legacy API
            extractor.connect()
            
            # Get transformer
            transformer = SalesRecordTransformer(
                config={
                    'field_mappings': mapping.mapping_config.get('transformer', {}).get('config', {}).get('field_mappings', {}),
                    'validation_rules': mapping.mapping_config.get('transformer', {}).get('config', {}).get('validation_rules', [])
                }
            )
            
            # Get loader
            loader = DjangoModelLoader(
                config={
                    'app_name': mapping.mapping_config.get('loader', {}).get('config', {}).get('app_name', 'sales'),
                    'model_name': mapping.mapping_config.get('loader', {}).get('config', {}).get('model_name', 'SalesRecord' if component == 'sales_records' else 'SalesRecordItem'),
                    'unique_field': mapping.mapping_config.get('loader', {}).get('config', {}).get('unique_field', 'legacy_id'),
                    'update_strategy': mapping.mapping_config.get('loader', {}).get('config', {}).get('update_strategy', 'update_or_create'),
                    'model_mapping': mapping.mapping_config.get('model_mapping', {}),
                    'field_mapping': mapping.mapping_config.get('field_mapping', {}),
                    'relation_mapping': mapping.mapping_config.get('relation_mapping', {})
                }
            )
            
            # Process records in batches
            for batch in extractor.extract(query_params=query_params):
                if not batch:
                    self.stdout.write("No records found in batch")
                    continue
                    
                self.stdout.write(f"Processing batch of {len(batch)} records")
                
                # Process each record
                for record in batch:
                    records_processed += 1
                    
                    try:
                        # Transform record
                        if component == 'sales_records':
                            transformed_record = transformer.transform(record)
                        else:
                            # For line items, we need to find the parent record
                            # This is handled differently in the SalesRecordTransformer
                            # We'll skip individual transformation here and handle it after the batch
                            continue
                        
                        if not transformed_record:
                            if debug:
                                self.stdout.write(f"Record {record.get('id', 'unknown')} was not transformed")
                            records_failed += 1
                            
                            # Log detail
                            SyncLogDetail.objects.create(
                                sync_log=sync_log,
                                record_id=record.get('AbsNr', record.get('id', 'unknown')),
                                status="failed",
                                error_message="Record was not transformed",
                                record_data=record
                            )
                            continue
                            
                        # Load record
                        result = loader.load(transformed_record)
                        
                        if result.get('status') == 'success':
                            records_succeeded += 1
                            synced_ids.append(record.get('AbsNr', record.get('id', 'unknown')))
                            
                            # Log detail
                            SyncLogDetail.objects.create(
                                sync_log=sync_log,
                                record_id=record.get('AbsNr', record.get('id', 'unknown')),
                                status="success",
                                record_data={"model": result.get('model', ''), "pk": result.get('pk', '')}
                            )
                        else:
                            records_failed += 1
                            
                            # Log detail
                            SyncLogDetail.objects.create(
                                sync_log=sync_log,
                                record_id=record.get('AbsNr', record.get('id', 'unknown')),
                                status="failed",
                                error_message=result.get('error', ''),
                                record_data=transformed_record
                            )
                            
                    except Exception as e:
                        records_failed += 1
                        
                        # Log detail
                        SyncLogDetail.objects.create(
                            sync_log=sync_log,
                            record_id=record.get('AbsNr', record.get('id', 'unknown')),
                            status="failed",
                            error_message=str(e),
                            record_data=record
                        )
                        
                        if debug:
                            self.stdout.write(f"Error processing record {record.get('id', 'unknown')}: {str(e)}")
                            traceback.print_exc()
            
            # For line items, we need to handle them differently
            if component == 'sales_record_items' and batch:
                # Get the parent sales records for these line items
                from pyerp.business_modules.sales.models import SalesRecord
                
                # Extract AbsNr values from the batch
                abs_nrs = [record.get('AbsNr') for record in batch if record.get('AbsNr')]
                
                if abs_nrs:
                    # Get unique AbsNr values
                    unique_abs_nrs = list(set(abs_nrs))
                    self.stdout.write(f"Processing line items for {len(unique_abs_nrs)} unique sales records")
                    
                    # Get the corresponding SalesRecord objects
                    sales_records = SalesRecord.objects.filter(legacy_id__in=unique_abs_nrs)
                    
                    for sales_record in sales_records:
                        # Filter batch for this sales record
                        record_items = [item for item in batch if item.get('AbsNr') == sales_record.legacy_id]
                        
                        if record_items:
                            self.stdout.write(f"Found {len(record_items)} line items for sales record {sales_record.legacy_id}")
                            
                            # Transform line items
                            transformed_items = transformer.transform_line_items(record_items, sales_record.id)
                            
                            if transformed_items:
                                # Load each transformed item
                                for item in transformed_items:
                                    try:
                                        result = loader.load(item)
                                        
                                        if result.get('status') == 'success':
                                            records_succeeded += 1
                                            
                                            # Log detail
                                            SyncLogDetail.objects.create(
                                                sync_log=sync_log,
                                                record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                                status="success",
                                                record_data={"model": "SalesRecordItem", "pk": result.get('pk', '')}
                                            )
                                        else:
                                            records_failed += 1
                                            
                                            # Log detail
                                            SyncLogDetail.objects.create(
                                                sync_log=sync_log,
                                                record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                                status="failed",
                                                error_message=result.get('error', ''),
                                                record_data=item
                                            )
                                    except Exception as e:
                                        records_failed += 1
                                        
                                        # Log detail
                                        SyncLogDetail.objects.create(
                                            sync_log=sync_log,
                                            record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                            status="failed",
                                            error_message=str(e),
                                            record_data=item
                                        )
                                        
                                        if debug:
                                            self.stdout.write(f"Error processing line item: {str(e)}")
                                            traceback.print_exc()
            
            # Update sync log
            sync_log.mark_completed(records_succeeded, records_failed)
            
            # Log completion
            self.stdout.write(
                f"Sync completed for {component}: {records_succeeded} succeeded, {records_failed} failed"
            )
            
            # Return result
            return {
                "status": "completed" if records_failed == 0 else "partial",
                "records_processed": records_processed,
                "records_succeeded": records_succeeded,
                "records_failed": records_failed,
                "synced_ids": synced_ids
            }
        except Exception as e:
            self.stdout.write(f"Error running sync for {component}: {str(e)}")
            if debug:
                traceback.print_exc()
            
            # Update sync log with error
            if 'sync_log' in locals():
                sync_log.mark_failed(str(e))
            
            # Return error result
            return {
                "status": "failed",
                "error": str(e)
            }
        finally:
            # Ensure connection is closed
            if extractor:
                extractor.close()
    
    def _get_sync_mapping(self, mapping_name):
        """Get a sync mapping by name."""
        try:
            return SyncMapping.objects.get(entity_type=mapping_name)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error getting sync mapping '{mapping_name}': {str(e)}"))
            return None 