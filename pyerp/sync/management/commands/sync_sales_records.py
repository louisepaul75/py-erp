"""Management command to synchronize sales records from legacy ERP."""

import json
import yaml
import os
from pathlib import Path
from datetime import timedelta, datetime
import time
import traceback
import ast
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q

from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.models import SyncMapping, SyncSource, SyncTarget, SyncLog, SyncLogDetail
from pyerp.sync.pipeline import PipelineFactory
from pyerp.sync.extractors import LegacyAPIExtractor
from pyerp.sync.transformers import SalesRecordTransformer
from pyerp.sync.loaders import DjangoModelLoader
from pyerp.business_modules.sales.models import SalesRecord
from pyerp.business_modules.products.models import VariantProduct


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
            synced_legacy_ids = str(record_result['synced_ids'])
            self.stdout.write(f"Using {len(synced_legacy_ids)} synced legacy IDs for line items")
        else:
            # Only fallback to all records in the database if no limit was specified
            if not options.get('limit'):
                # Fallback: Get all legacy IDs from the database
                from pyerp.business_modules.sales.models import SalesRecord
                synced_legacy_ids = [str(legacy_id) for legacy_id in SalesRecord.objects.values_list('legacy_id', flat=True)]
                self.stdout.write(f"Using all {len(synced_legacy_ids)} legacy IDs from database for line items")
            else:
                self.stdout.write("No records were synced and a limit was specified, skipping line items sync")
        
        if synced_legacy_ids:
            # Create filter query for line items
            line_items_params = self._build_query_params(options, component='sales_record_items')
            
            # Add the AbsNr filter directly in the format expected by the API client
            if 'filter_query' not in line_items_params:
                line_items_params['filter_query'] = []
            
            # Ensure synced_legacy_ids are strings in a list format
            if isinstance(synced_legacy_ids, str):
                # If it's already a string, parse it back to a list
                try:
                    synced_legacy_ids = ast.literal_eval(synced_legacy_ids)
                except (ValueError, SyntaxError):
                    # If parsing fails, treat it as a single ID
                    synced_legacy_ids = [synced_legacy_ids]
            
            # Convert all IDs to strings if they aren't already
            string_ids = [str(id) for id in synced_legacy_ids]
            line_items_params['filter_query'].append(['AbsNr', 'in', string_ids])
            
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
        
        # Only add date filters for the main sales_records component
        if component is None or component == 'sales_records':
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
            elif not options['full'] and not ('filter_query' in query_params and any(f[0] == 'created_date' for f in query_params['filter_query'])):
                five_years_ago = timezone.now() - timedelta(days=5*365)
                date_str = five_years_ago.strftime('%Y-%m-%d')
                
                # Add to filter_query
                if 'filter_query' not in query_params:
                    query_params['filter_query'] = []
                
                # Add date filter directly
                query_params['filter_query'].append(['Datum', '>', date_str])
                
                self.stdout.write(f"Adding default date filter: records from {date_str} (last 5 years)")
        elif component == 'sales_record_items':
            self.stdout.write("Skipping date filters for sales_record_items - using only AbsNr filter")
            
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
            
            # Extract records - this returns a list, not an iterator
            records = extractor.extract(query_params=query_params)
            
            if not records:
                self.stdout.write("No records found")
            else:
                self.stdout.write(f"Processing {len(records)} records")
                
                # Process each record
                for record in records:
                    records_processed += 1
                    
                    try:
                        # Skip if record is not a dictionary
                        if not isinstance(record, dict):
                            self.stdout.write(f"Record {records_processed} is not a dictionary: {type(record)}")
                            records_failed += 1
                            continue
                            
                        # Transform record
                        if component == 'sales_records':
                            transformed_record = transformer.transform(record)
                            
                            # Check if transformation was successful
                            if not transformed_record:
                                if debug:
                                    self.stdout.write(f"Record {record.get('AbsNr', 'unknown')} was not transformed")
                                records_failed += 1
                                
                                # Log detail
                                SyncLogDetail.objects.create(
                                    sync_log=sync_log,
                                    record_id=record.get('AbsNr', record.get('id', 'unknown')),
                                    status="failed",
                                    error_message="Record was not transformed",
                                    record_data=self._sanitize_record_data(record)
                                )
                                continue
                                
                            # Ensure legacy_id is set correctly
                            if 'AbsNr' in record and 'legacy_id' not in transformed_record:
                                transformed_record['legacy_id'] = record['AbsNr']
                                
                            # Load record
                            try:
                                result = loader.load([transformed_record])
                                
                                # Handle LoadResult object
                                if result.created > 0 or result.updated > 0:
                                    records_succeeded += 1
                                    
                                    # Get AbsNr safely
                                    if isinstance(record, dict) and 'AbsNr' in record:
                                        abs_nr = record.get('AbsNr')
                                        synced_ids.append(abs_nr)
                                    
                                    # Log detail
                                    SyncLogDetail.objects.create(
                                        sync_log=sync_log,
                                        record_id=record.get('AbsNr', record.get('id', 'unknown')) if isinstance(record, dict) else f"unknown-{records_processed}",
                                        status="success",
                                        record_data={"model": "SalesRecord", "legacy_id": transformed_record.get('legacy_id', '')}
                                    )
                                else:
                                    records_failed += 1
                                    
                                    # Get error details
                                    error_msg = "Unknown error"
                                    if result.errors > 0 and result.error_details:
                                        error_msg = result.error_details[0].get('error', 'Unknown error')
                                    
                                    # Log detail
                                    SyncLogDetail.objects.create(
                                        sync_log=sync_log,
                                        record_id=record.get('AbsNr', record.get('id', 'unknown')) if isinstance(record, dict) else f"unknown-{records_processed}",
                                        status="failed",
                                        error_message=error_msg,
                                        record_data=self._sanitize_record_data(transformed_record)
                                    )
                            except Exception as e:
                                records_failed += 1
                                
                                # Log detail
                                SyncLogDetail.objects.create(
                                    sync_log=sync_log,
                                    record_id=record.get('AbsNr', record.get('id', 'unknown')) if isinstance(record, dict) else f"unknown-{records_processed}",
                                    status="failed",
                                    error_message=f"Error loading record: {str(e)}",
                                    record_data=self._sanitize_record_data(transformed_record)
                                )
                                
                                if debug:
                                    self.stdout.write(f"Error loading record {record.get('AbsNr', 'unknown')}: {str(e)}")
                                    traceback.print_exc()
                        else:
                            # For line items, we need to find the parent record
                            # This is handled differently in the SalesRecordTransformer
                            # We'll skip individual transformation here and handle it after the batch
                            continue
                            
                    except Exception as e:
                        records_failed += 1
                        
                        # Get record ID safely
                        if isinstance(record, dict):
                            record_id = record.get('AbsNr', record.get('id', 'unknown'))
                        else:
                            record_id = f"unknown-{records_processed}"
                        
                        # Log detail
                        SyncLogDetail.objects.create(
                            sync_log=sync_log,
                            record_id=record_id,
                            status="failed",
                            error_message=str(e),
                            record_data=self._sanitize_record_data(record)
                        )
                        
                        if debug:
                            self.stdout.write(f"Error processing record {record_id}: {str(e)}")
                            traceback.print_exc()
            
            # For line items, we need to handle them differently
            if component == 'sales_record_items' and records:
                # Get the parent sales records for these line items
                from pyerp.business_modules.sales.models import SalesRecord
                
                # Extract AbsNr values from the batch
                abs_nrs = [record.get('AbsNr') for record in records if isinstance(record, dict) and record.get('AbsNr')]
                
                if abs_nrs:
                    # Get unique AbsNr values
                    unique_abs_nrs = list(set(abs_nrs))
                    
                    if debug:
                        self.stdout.write(f"Looking up sales records with legacy_ids: {unique_abs_nrs}")
                    
                    # Get sales records by legacy_id
                    sales_records = SalesRecord.objects.filter(legacy_id__in=unique_abs_nrs)
                    
                    if debug:
                        self.stdout.write(f"Found {sales_records.count()} sales records in database")
                        for sr in sales_records:
                            self.stdout.write(f"  - Sales record DB ID: {sr.id}, legacy_id: {sr.legacy_id}")
                    
                    if not sales_records:
                        self.stdout.write(f"No sales records found for legacy IDs: {unique_abs_nrs}")
                    else:
                        self.stdout.write(f"Found {sales_records.count()} sales records for line items")
                        
                        # Process each sales record
                        for sales_record in sales_records:
                            # Filter batch for this sales record
                            if debug:
                                self.stdout.write(f"Processing sales record ID: {sales_record.id}, legacy_id: {sales_record.legacy_id}")
                            
                            # Cast legacy_id to string for comparison
                            legacy_id_str = str(sales_record.legacy_id)
                            
                            # Filter records that match this sales record's legacy_id
                            record_items = []
                            for item in records:
                                if isinstance(item, dict) and str(item.get('AbsNr', '')) == legacy_id_str:
                                    record_items.append(item)
                                    
                            if debug:
                                self.stdout.write(f"Found {len(record_items)} line items matching legacy_id {legacy_id_str}")
                            
                            if record_items:
                                self.stdout.write(f"Found {len(record_items)} line items for sales record {sales_record.legacy_id}")
                                
                                # Add debug info for transformer
                                if debug:
                                    self.stdout.write(f"First record item: {record_items[0] if record_items else 'None'}")
                                    self.stdout.write(f"First record item AbsNr: {record_items[0].get('AbsNr') if record_items else 'None'}")
                                
                                # Transform line items
                                if debug:
                                    self.stdout.write(f"Calling transformer.transform_line_items with {len(record_items)} items and sales_record.id={sales_record.id}")
                                
                                # Process each line item manually instead of using the transformer
                                transformed_items = []
                                for item in record_items:
                                    if not item or 'AbsNr' not in item or 'PosNr' not in item:
                                        if debug:
                                            self.stdout.write(f"Invalid line item data: {item}")
                                        continue
                                    
                                    try:
                                        # Try to find product by legacy_sku
                                        product = None
                                        product_code = item.get('ArtNr', '')
                                        if product_code:
                                            try:
                                                # First try exact match on legacy_sku
                                                product = VariantProduct.objects.get(legacy_sku=product_code)
                                                if debug:
                                                    self.stdout.write(f"Found product by legacy_sku: {product.id} ({product.name}) for {product_code}")
                                            except VariantProduct.DoesNotExist:
                                                # Try by SKU as fallback
                                                try:
                                                    product = VariantProduct.objects.get(sku=product_code)
                                                    if debug:
                                                        self.stdout.write(f"Found product by SKU: {product.id} ({product.name}) for {product_code}")
                                                except VariantProduct.DoesNotExist:
                                                    if debug:
                                                        self.stdout.write(f"No product found for legacy_sku or SKU {product_code}")
                                            except VariantProduct.MultipleObjectsReturned:
                                                # If multiple found, get the most recently updated one
                                                product = VariantProduct.objects.filter(legacy_sku=product_code).order_by('-modified_date').first()
                                                if debug:
                                                    self.stdout.write(f"Multiple products found for legacy_sku {product_code}, using most recent: {product.id}")

                                        # Calculate line subtotal and tax amount
                                        line_subtotal = self._to_decimal(item.get('Pos_Betrag', 0))
                                        tax_rate = Decimal('19.0')
                                        tax_amount = self._to_decimal((line_subtotal * tax_rate / Decimal('100')))
                                        
                                        # Create transformed item
                                        transformed_item = {
                                            'legacy_id': f"{item.get('AbsNr')}_{item.get('PosNr')}",
                                            'sales_record': sales_record,  # Use actual object, not just ID
                                            'position': item.get('PosNr'),
                                            'legacy_sku': product_code,
                                            'description': item.get('Bezeichnung', ''),
                                            'quantity': self._to_decimal(item.get('Menge', 0)),
                                            'unit_price': self._to_decimal(item.get('Preis', 0)),
                                            'discount_percentage': self._to_decimal(item.get('Rabatt', 0)),
                                            'tax_rate': tax_rate,
                                            'line_total': self._to_decimal(item.get('Pos_Betrag', 0)),
                                            'notes': item.get('Anmerkung', ''),
                                            'line_subtotal': line_subtotal,
                                            'tax_amount': tax_amount,
                                        }
                                        
                                        # Add product reference if found
                                        if product:
                                            transformed_item['product'] = product
                                            if debug:
                                                self.stdout.write(f"Added product reference: ID={product.id}, SKU={product.sku} to item {transformed_item['legacy_id']}")
                                        else:
                                            if debug:
                                                self.stdout.write(f"No product reference added for item {transformed_item['legacy_id']} with legacy_sku {product_code}")
                                        
                                        transformed_items.append(transformed_item)
                                        
                                        if debug:
                                            self.stdout.write(f"Manually transformed item: {transformed_item}")
                                    except Exception as e:
                                        if debug:
                                            self.stdout.write(f"Error manually transforming item: {str(e)}")
                                
                                if debug:
                                    self.stdout.write(f"Manually transformed items count: {len(transformed_items)}")
                                
                                if transformed_items:
                                    self.stdout.write(f"Transformed {len(transformed_items)} line items for sales record {sales_record.legacy_id}")
                                    # Load each transformed item
                                    for item in transformed_items:
                                        try:
                                            # Debug log the item being saved
                                            if debug:
                                                self.stdout.write(f"Saving line item: {item}")
                                                
                                            # Load the item
                                            if debug:
                                                self.stdout.write(f"Calling loader.load with item: {str(item)[:100]}...")
                                                
                                            result = loader.load([item])
                                            
                                            if debug:
                                                self.stdout.write(f"Loader result: created={result.created}, updated={result.updated}, errors={result.errors}")
                                                if result.errors > 0:
                                                    self.stdout.write(f"Error details: {result.error_details}")
                                            
                                            if result.created > 0 or result.updated > 0:
                                                records_succeeded += 1
                                                
                                                # Log detail
                                                SyncLogDetail.objects.create(
                                                    sync_log=sync_log,
                                                    record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                                    status="success",
                                                    record_data={"model": "SalesRecordItem", "legacy_id": item.get('legacy_id', '')}
                                                )
                                            else:
                                                records_failed += 1
                                                
                                                # Get error details
                                                error_msg = "Unknown error"
                                                if result.errors > 0 and result.error_details:
                                                    error_msg = result.error_details[0].get('error', 'Unknown error')
                                                
                                                # Log detail
                                                SyncLogDetail.objects.create(
                                                    sync_log=sync_log,
                                                    record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                                    status="failed",
                                                    error_message=error_msg,
                                                    record_data=self._sanitize_record_data(item)
                                                )
                                        except Exception as e:
                                            records_failed += 1
                                            
                                            # Log detail
                                            SyncLogDetail.objects.create(
                                                sync_log=sync_log,
                                                record_id=f"{sales_record.legacy_id}_{item.get('position')}",
                                                status="failed",
                                                error_message=str(e),
                                                record_data=self._sanitize_record_data(item)
                                            )
                                            
                                            if debug:
                                                self.stdout.write(f"Error processing line item {sales_record.legacy_id}_{item.get('position')}: {str(e)}")
                                                traceback.print_exc()
            
            # Update sync log
            sync_log.status = "completed"
            sync_log.records_processed = records_processed
            sync_log.records_succeeded = records_succeeded
            sync_log.records_failed = records_failed
            sync_log.save()
            
            self.stdout.write(f"Sync completed for {component}: {records_succeeded} succeeded, {records_failed} failed")
            
            return {
                'status': 'success',
                'records_processed': records_processed,
                'records_succeeded': records_succeeded,
                'records_failed': records_failed,
                'synced_ids': synced_ids
            }
            
        except Exception as e:
            self.stdout.write(f"Error running sync for {component}: {str(e)}")
            if debug:
                traceback.print_exc()
                
            # Update sync log if it exists
            if 'sync_log' in locals():
                sync_log.status = "failed"
                sync_log.error_message = str(e)
                sync_log.save()
                
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            # Close extractor connection if it exists
            if extractor:
                try:
                    extractor.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {str(e)}")
    
    def _sanitize_record_data(self, record):
        """Sanitize record data for JSON serialization."""
        if not record:
            return {}
            
        if not isinstance(record, dict):
            return {"raw_data": str(record)[:500]}
            
        # Create a copy to avoid modifying the original
        sanitized = {}
        
        for key, value in record.items():
            # Handle pandas Timestamp objects
            if hasattr(value, 'isoformat'):
                sanitized[key] = value.isoformat()
            # Handle numpy types
            elif hasattr(value, 'item'):
                try:
                    sanitized[key] = value.item()
                except:
                    sanitized[key] = str(value)
            # Handle other non-serializable types
            elif not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                sanitized[key] = str(value)
            # Handle nested dictionaries
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_record_data(value)
            # Handle lists of dictionaries
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sanitized[key] = [self._sanitize_record_data(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
                
        return sanitized
    
    def _get_sync_mapping(self, mapping_name):
        """Get a sync mapping by name."""
        try:
            return SyncMapping.objects.get(entity_type=mapping_name)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error getting sync mapping '{mapping_name}': {str(e)}"))
            return None
    
    def _to_decimal(self, value, decimal_places=2):
        """Convert value to Decimal with specified decimal places."""
        if value is None:
            return Decimal('0')
        if isinstance(value, Decimal):
            return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if isinstance(value, (int, float)):
            return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if isinstance(value, str):
            try:
                return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            except:
                return Decimal('0')
        return Decimal('0') 