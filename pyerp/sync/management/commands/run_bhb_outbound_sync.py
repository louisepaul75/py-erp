"""
Management command to run the BuchhaltungsButler outbound receipt sync manually.
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError

from pyerp.sync.extractors.buchhaltungsbutler import BuchhaltungsButlerReceiptExtractor
from pyerp.sync.loaders.sales import SalesRecordStatusLoader
from pyerp.sync.pipeline import PipelineFactory
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)

class Command(BaseCommand):
    help = (
        "Runs the sync pipeline for BuchhaltungsButler outbound receipts to update "
        "SalesRecord status."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--page-size',
            type=int,
            default=200,
            help='Number of records to fetch per API page.',
        )
        parser.add_argument(
            '--tolerance',
            type=str,
            default="2.0",
            help='Payment amount tolerance percentage (e.g., "2.0" for 2%).',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE(
                "Starting BuchhaltungsButler outbound receipt sync..."
            )
        )

        page_size = options['page_size']
        tolerance = options['tolerance']

        try:
            # --- Configuration ---
            extractor_config = {
                'list_direction': 'outbound',
                'page_size': page_size
            }
            loader_config = {
                'payment_tolerance_percent': tolerance
                # Add field_mapping here if defaults are not correct
                # 'field_mapping': {
                #   'api_match_field': 'filename',
                #   'api_amount_paid': 'amount_paid',
                #   'api_payment_date': 'payment_date'
                # }
            }

            # --- Instantiate Components ---
            self.stdout.write("Initializing extractor...")
            extractor = BuchhaltungsButlerReceiptExtractor(config=extractor_config)

            self.stdout.write("Initializing loader...")
            loader = SalesRecordStatusLoader(config=loader_config)

            # --- Create and Run Pipeline ---
            # Construct the configuration dictionary for the factory
            pipeline_config = {
                'pipeline_name': 'bhb_outbound_receipt_sync', # Optional name for logging
                'extractor': {
                    'class': 'pyerp.sync.extractors.buchhaltungsbutler.BuchhaltungsButlerReceiptExtractor',
                    'config': extractor_config
                },
                'transformer': {
                    # Using a passthrough transformer as loader handles logic
                    'class': 'pyerp.sync.transformers.base.PassthroughTransformer',
                    'config': {}
                },
                'loader': {
                    'class': 'pyerp.sync.loaders.sales.SalesRecordStatusLoader',
                    'config': loader_config
                }
            }
            
            self.stdout.write("Creating sync pipeline via factory...")
            # Create pipeline using the factory method
            pipeline = PipelineFactory.create_pipeline_from_config(pipeline_config)

            self.stdout.write("Running pipeline...")
            # The run method might return a SyncLog object or a result dict
            sync_result = pipeline.run()

            self.stdout.write(
                self.style.SUCCESS("Pipeline finished.")
            )
            
            # --- Display Results ---
            # Output depends on what pipeline.run() returns
            if isinstance(sync_result, dict):
                self.stdout.write("Sync Results:")
                for key, value in sync_result.items():
                    self.stdout.write(f"  {key.capitalize()}: {value}")
            # If it returns a SyncLog object, print its relevant fields
            # elif hasattr(sync_result, 'status'): 
            #     self.stdout.write(f"Sync Log ID: {sync_result.id}")
            #     self.stdout.write(f"Status: {sync_result.status}")
            #     self.stdout.write(f"Processed: {sync_result.records_processed}")
            #     self.stdout.write(f"Succeeded: {sync_result.records_succeeded}")
            #     self.stdout.write(f"Failed: {sync_result.records_failed}")
            else:
                 self.stdout.write(f"Raw Result: {sync_result}")

        except ImportError as e:
            raise CommandError(f"Failed to import necessary components. Check imports (Pipeline, etc.). Error: {e}")
        except Exception as e:
            logger.error(f"Error during BuchhaltungsButler outbound sync: {e}", exc_info=True)
            raise CommandError(f"Sync failed: {e}") 