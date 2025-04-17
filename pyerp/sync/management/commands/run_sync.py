"""Management command for running data synchronization tasks."""

import logging
import json
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run data synchronization tasks."""

    help = "Run data synchronization tasks for specified mappings"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--mapping", type=int, help="ID of specific mapping to sync"
        )
        parser.add_argument(
            "--entity-type", help="Entity type to sync (e.g., product, customer)"
        )
        parser.add_argument("--source", help="Source name to filter mappings")
        parser.add_argument("--target", help="Target name to filter mappings")
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available mappings instead of running sync",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sync instead of incremental",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Batch size for processing records", 
        )
        parser.add_argument("--filters", help="Additional filters in JSON format")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_false",
            dest="fail_on_filter_error",
            default=True,
            help="Don't fail if date filter doesn't work (default: fail)",
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear extractor cache before running",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        # List mappings if requested
        if options["list"]:
            self._list_mappings(
                source_name=options["source"],
                target_name=options["target"],
                entity_type=options["entity_type"],
            )
            return

        # Clear cache if requested
        if options["clear_cache"]:
            self._clear_extractor_caches()

        # Get common options
        incremental = not options["full"]
        batch_size = options["batch_size"]
        fail_on_filter_error = options["fail_on_filter_error"]
        debug = options["debug"]

        # Get query parameters
        query_params = None
        if options["filters"]:
            try:
                query_params = json.loads(options["filters"])
            except json.JSONDecodeError:
                raise CommandError("Invalid JSON format for filters")

        # Get mappings to process
        mappings = self._get_mappings(
            mapping_id=options["mapping"],
            source_name=options["source"],
            target_name=options["target"],
            entity_type=options["entity_type"],
        )

        if not mappings:
            self.stdout.write(
                self.style.WARNING("No active mappings found matching the criteria")
            )
            return

        # Process each mapping
        for mapping in mappings:
            self.stdout.write(
                f"\nProcessing mapping: {mapping} (ID: {mapping.id}, "
                f"Source: {mapping.source.name}, Target: {mapping.target.name})"
            )

            try:
                # Create pipeline first, handle potential creation errors
                try:
                    pipeline = PipelineFactory.create_pipeline(mapping)
                    self.stdout.write(f"Pipeline created successfully for mapping ID {mapping.id}")
                except Exception as creation_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to create pipeline for mapping ID {mapping.id} "
                            f"({mapping.entity_type} from {mapping.source.name} to {mapping.target.name}): "
                            f"{str(creation_error)}"
                        )
                    )
                    if debug:
                        import traceback
                        traceback.print_exc()
                    continue # Skip to the next mapping if pipeline creation fails

                # Now run the successfully created pipeline
                cached_data = None
                sync_log = None
                use_cached_data = False

                # 1. Attempt to fetch data using pipeline's fetch_data method
                if hasattr(pipeline, "fetch_data"):
                    try:
                        self.stdout.write(f"Attempting to pre-fetch data for {mapping.entity_type}...")
                        cached_data = pipeline.fetch_data(
                            query_params=query_params,
                            fail_on_filter_error=fail_on_filter_error
                        )
                        if cached_data is not None:
                            self.stdout.write(self.style.SUCCESS(f"Successfully pre-fetched {len(cached_data)} records."))
                            use_cached_data = True
                        else:
                            self.stdout.write(self.style.NOTICE("fetch_data returned None, proceeding without cache."))
                    except NotImplementedError:
                        self.stdout.write(self.style.NOTICE(f"Pipeline for {mapping.entity_type} does not implement fetch_data."))
                    except Exception as fetch_error:
                        self.stdout.write(self.style.WARNING(f"Pre-fetch failed for {mapping.entity_type}: {fetch_error}. Will attempt standard run."))

                # 2. Determine execution path (run_with_data or run)
                can_run_with_data = hasattr(pipeline, "run_with_data")

                start_time = timezone.now()
                self.stdout.write(f"Starting sync at {start_time}...")

                if use_cached_data and can_run_with_data:
                    self.stdout.write(f"Running pipeline {mapping.id} with pre-fetched data...")
                    sync_log = pipeline.run_with_data(
                        data=cached_data,
                        incremental=incremental,
                        batch_size=batch_size,
                        query_params=query_params,
                    )
                else:
                    if use_cached_data and not can_run_with_data:
                        self.stdout.write(self.style.WARNING(
                            f"Pipeline {mapping.id} fetched data but does not support run_with_data. "
                            f"Falling back to standard run() method."
                        ))
                    elif not use_cached_data:
                        self.stdout.write(f"Running pipeline {mapping.id} using standard run() method...")

                    sync_log = pipeline.run(
                        incremental=incremental,
                        batch_size=batch_size,
                        query_params=query_params,
                        fail_on_filter_error=fail_on_filter_error,
                    )

                end_time = timezone.now()
                duration = (end_time - start_time).total_seconds()

                # Report results
                if sync_log.status == "completed":
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sync completed successfully in {duration:.2f} seconds"
                        )
                    )
                elif sync_log.status == "partial":
                    self.stdout.write(
                        self.style.WARNING(
                            f"Sync completed with some errors in {duration:.2f} seconds"
                        )
                    )
                else: # failed or other status
                    self.stdout.write(
                        self.style.ERROR(f"Sync finished with status '{sync_log.status}' in {duration:.2f} seconds")
                    )

                self.stdout.write("\nStatistics:")
                self.stdout.write(f"  Processed: {sync_log.records_processed}")
                self.stdout.write(f"  Created: {sync_log.records_created}")
                self.stdout.write(f"  Updated: {sync_log.records_updated}")
                self.stdout.write(f"  Failed: {sync_log.records_failed}")

                if sync_log.error_message:
                    self.stdout.write(
                        self.style.ERROR(f"\nError details logged: {sync_log.error_message}")
                    )

            except Exception as e:
                # This catches errors during pipeline.run() or other unexpected issues
                self.stdout.write(
                    self.style.ERROR(f"Sync execution failed unexpectedly for mapping ID {mapping.id}: {str(e)}")
                )
                if debug:
                    import traceback
                    traceback.print_exc()
                # Optionally create a failed SyncLog entry here if needed for tracking

    def _list_mappings(self, source_name=None, target_name=None, entity_type=None):
        """List available mappings."""
        mappings = self._get_mappings(
            source_name=source_name, target_name=target_name, entity_type=entity_type
        )

        if not mappings:
            self.stdout.write(
                self.style.WARNING("No active mappings found matching the criteria")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f"\nFound {len(mappings)} active mapping(s):")
        )

        for mapping in mappings:
            self.stdout.write(
                f"\nID: {mapping.id}"
                f"\nEntity Type: {mapping.entity_type}"
                f"\nSource: {mapping.source.name}"
                f"\nTarget: {mapping.target.name}"
                f"\n{'-' * 40}"
            )

    def _get_mappings(
        self, mapping_id=None, source_name=None, target_name=None, entity_type=None
    ):
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

    def _clear_extractor_caches(self):
        """Clear any caches used by known extractors."""
        self.stdout.write("Attempting to clear extractor caches...")
        cleared_any = False
        try:
            # Attempt to clear LegacyAPIExtractor cache
            # Use settings to make extractor configurable?
            from pyerp.sync.extractors.legacy_api import LegacyAPIExtractor
            if hasattr(LegacyAPIExtractor, 'clear_cache') and callable(LegacyAPIExtractor.clear_cache):
                LegacyAPIExtractor.clear_cache()
                self.stdout.write("- Cleared LegacyAPIExtractor cache.")
                cleared_any = True
            else:
                self.stdout.write("- LegacyAPIExtractor has no clear_cache method.")
        except ImportError:
            self.stdout.write(self.style.NOTICE("- LegacyAPIExtractor not found or import failed."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"- Error clearing LegacyAPIExtractor cache: {e}"))

        # Add other extractors here if needed
        # try:
        #     from other_extractor import OtherExtractor
        #     OtherExtractor.clear_cache()
        #     self.stdout.write("Cleared OtherExtractor cache")
        # except Exception as e:
        #     self.stderr.write(f"Error clearing OtherExtractor cache: {e}")

        if not cleared_any:
            self.stdout.write(self.style.NOTICE("No known extractor caches were cleared."))
