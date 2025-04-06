"""Management command to synchronize sales records from legacy ERP."""

import traceback

from django.core.management.base import CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger
from pyerp.sync.pipeline import PipelineFactory
from .base_sync_command import BaseSyncCommand


logger = get_logger(__name__)


class Command(BaseSyncCommand):
    """Command to sync sales records (Belege) and items (Belege_Pos)."""

    help = "Synchronize sales records (Belege) and items (Belege_Pos)"

    # Define legacy key field names
    PARENT_ENTITY_TYPE = "sales_records"
    PARENT_LEGACY_KEY_FIELD = "AbsNr"  # Key field in Belege
    CHILD_ENTITY_TYPE = "sales_record_items"
    CHILD_PARENT_LINK_FIELD = "AbsNr" # Field in Belege_Pos linking to Belege

    def add_arguments(self, parser):
        """Add command arguments, inheriting from BaseSyncCommand."""
        super().add_arguments(parser)
        # No command-specific arguments needed for now
        # Base class handles: --full, --batch-size, --top, --filters, --debug,
        # --days, --fail-on-filter-error, --clear-cache

    def handle(self, *args, **options):
        """Orchestrate the multi-stage sync process with batch processing."""
        command_start_time = timezone.now()  # Use local variable
        self.debug = options.get("debug", False)
        log_prefix = f"[sync_sales_records - {command_start_time.isoformat()}]"
        logger.info(
            f"{log_prefix} Starting sales record & items sync orchestrator..."
        )
        self.stdout.write(
            f"{log_prefix} Starting sales record sync process at "
            f"{command_start_time}"
        )

        # Fetch mappings first
        try:
            parent_mapping = self.get_mapping(
                entity_type=self.PARENT_ENTITY_TYPE
            )
            child_mapping = self.get_mapping(
                entity_type=self.CHILD_ENTITY_TYPE
            )
        except CommandError as e:
            self.stderr.write(self.style.ERROR(
                f"{log_prefix} Failed to get required sync mappings: {e}"
            ))
            raise CommandError(
                "Sync cannot proceed without required mappings."
            ) from e

        # Build initial query parameters from common args
        initial_query_params = self.build_query_params(options, parent_mapping)
        logger.info(
            f"{log_prefix} Initial query parameters built: {initial_query_params}"
        )
        
        # Get batch size from options
        batch_size = options.get("batch_size", 100)
        self.stdout.write(f"{log_prefix} Using batch size: {batch_size}")
        
        # --- Step 1: Fetch All Parent Record IDs (AbsNr) using initial filters ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 1: Fetching parent record IDs "
            f"({self.PARENT_LEGACY_KEY_FIELD}) ==="
        ))
        logger.info(f"{log_prefix} Starting Step 1: Fetch Parent Record IDs")
        parent_record_ids = []
        fetched_data_for_ids = []
        try:
            parent_pipeline_for_id_fetch = PipelineFactory.create_pipeline(
                parent_mapping
            )
            id_fetch_params = {
                **initial_query_params,  # Include filters like --top, --days
                "select_fields": [self.PARENT_LEGACY_KEY_FIELD],  # Only fetch the key
            }
            logger.info(
                f"{log_prefix} Querying extractor for parent IDs with params: "
                f"{id_fetch_params}"
            )

            # Clear cache if requested (only for this first extractor call)
            if options.get("clear_cache"):
                self.stdout.write(
                    f"{log_prefix} Clearing parent ({self.PARENT_ENTITY_TYPE}) "
                    f"extractor cache..."
                )
                parent_pipeline_for_id_fetch.extractor.clear_cache()

            with parent_pipeline_for_id_fetch.extractor:
                fetched_data_for_ids = (
                    parent_pipeline_for_id_fetch.extractor.extract(
                        query_params=id_fetch_params,
                        fail_on_filter_error=options.get(
                            "fail_on_filter_error", True
                        )
                    )
                )
            logger.info(
                f"{log_prefix} Extractor returned {len(fetched_data_for_ids)} "
                f"potential parent records for ID extraction."
            )

            # Extract the unique parent key values
            parent_record_ids = list(
                set(
                    str(record.get(self.PARENT_LEGACY_KEY_FIELD))
                    for record in fetched_data_for_ids
                    if record.get(self.PARENT_LEGACY_KEY_FIELD) is not None
                )
            )
            self.stdout.write(
                f"{log_prefix} Found {len(parent_record_ids)} unique parent "
                f"record IDs ({self.PARENT_LEGACY_KEY_FIELD})."
            )
            logger.info(
                f"{log_prefix} Step 1: Found {len(parent_record_ids)} unique "
                f"parent IDs."
            )
            if self.debug and parent_record_ids:
                self.stdout.write(
                    f"{log_prefix} Sample Parent IDs: {parent_record_ids[:10]}..."
                )

        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"{log_prefix} Step 1 Failed: Could not fetch parent record IDs "
                f"({self.PARENT_LEGACY_KEY_FIELD}): {e}"
            ))
            logger.error(
                f"{log_prefix} Step 1: Failed to fetch parent IDs: {e}",
                exc_info=self.debug
            )
            if self.debug:
                traceback.print_exc()
            # If we can't get IDs, abort.
            raise CommandError(
                f"Could not fetch parent IDs, aborting sync. Error: {e}"
            )
            
        # --- Step 2: Process Belege and Belege_Pos records in batches ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 2: Processing parent and child records in batches ==="
        ))
        logger.info(f"{log_prefix} Starting Step 2: Batch processing")
        
        # Apply top limit if specified
        if "top" in options and options["top"]:
            top_limit = int(options["top"])
            if len(parent_record_ids) > top_limit:
                parent_record_ids = parent_record_ids[:top_limit]
                self.stdout.write(
                    f"{log_prefix} Applied top limit: Processing only first {top_limit} parent IDs."
                )
                
        # Process records in batches
        total_parent_batches = (len(parent_record_ids) + batch_size - 1) // batch_size
        self.stdout.write(
            f"{log_prefix} Will process {len(parent_record_ids)} parent records "
            f"in {total_parent_batches} batches of ~{batch_size} records each."
        )
        
        # Initialize statistics
        parent_stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
        child_stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
        
        # Initialize success flags
        parent_sync_successful = True
        child_sync_successful = True
        
        # Create parent pipeline
        parent_pipeline = PipelineFactory.create_pipeline(parent_mapping)
        
        # Create child pipeline
        child_pipeline = PipelineFactory.create_pipeline(child_mapping)
        
        # Process records in batches
        for batch_index in range(total_parent_batches):
            start_idx = batch_index * batch_size
            end_idx = min(start_idx + batch_size, len(parent_record_ids))
            batch_parent_ids = parent_record_ids[start_idx:end_idx]
            
            self.stdout.write(self.style.NOTICE(
                f"\n{log_prefix} --- Processing Batch {batch_index + 1}/{total_parent_batches} "
                f"({start_idx+1}-{end_idx} of {len(parent_record_ids)}) ---"
            ))
            
            # ----- Step 2.1: Process parent records (Belege) for this batch -----
            try:
                # Prepare filters for this batch of parent records
                parent_batch_filters = {
                    **initial_query_params,
                    self.PARENT_LEGACY_KEY_FIELD + "__in": batch_parent_ids
                }
                
                self.stdout.write(
                    f"{log_prefix} Extracting {len(batch_parent_ids)} parent records "
                    f"(Batch {batch_index + 1}/{total_parent_batches})..."
                )
                
                # Extract parent records for this batch
                with parent_pipeline.extractor:
                    parent_source_data = parent_pipeline.extractor.extract(
                        query_params=parent_batch_filters,
                        fail_on_filter_error=options.get(
                            "fail_on_filter_error", True
                        )
                    )
                
                self.stdout.write(
                    f"{log_prefix} Extracted {len(parent_source_data)} parent "
                    f"records for batch {batch_index + 1}."
                )
                
                if parent_source_data:
                    # Transform parent records
                    transformed_parent_data = (
                        parent_pipeline.transformer.transform(parent_source_data)
                    )
                    
                    self.stdout.write(
                        f"{log_prefix} Transformed {len(transformed_parent_data)} "
                        f"parent records for batch {batch_index + 1}."
                    )
                    
                    # Load transformed parent records
                    load_result = parent_pipeline.loader.load(
                        transformed_parent_data,
                        update_existing=(
                            options.get("force_update") or options.get("full")
                        ),
                    )
                    
                    # Update statistics
                    parent_stats["created"] += load_result.created
                    parent_stats["updated"] += load_result.updated
                    parent_stats["skipped"] += load_result.skipped
                    parent_stats["errors"] += load_result.errors
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"{log_prefix} Parent load for batch {batch_index + 1} finished: "
                        f"{load_result.created} created, "
                        f"{load_result.updated} updated, {load_result.skipped} skipped, "
                        f"{load_result.errors} errors."
                    ))
                    
                    # Display errors for this batch if any
                    if load_result.error_details:
                        self.stdout.write(self.style.WARNING(
                            f"{log_prefix} Parent Load Errors in batch {batch_index + 1}:"
                        ))
                        for i, err in enumerate(load_result.error_details):
                            if i < 5:  # Show only first 5 errors per batch
                                self.stdout.write(f"- {err}")
                            else:
                                self.stdout.write(
                                    f"... and {len(load_result.error_details) - 5} "
                                    f"more errors."
                                )
                                break
                else:
                    self.stdout.write(
                        f"{log_prefix} No parent records extracted for batch {batch_index + 1}, "
                        f"skipping transform and load."
                    )
                
                # ----- Step 2.2: Process child records (Belege_Pos) for this batch -----
                # Get the actual AbsNr values from this batch's extracted data
                batch_abs_nr_values = [
                    str(record.get(self.PARENT_LEGACY_KEY_FIELD))
                    for record in parent_source_data
                    if record.get(self.PARENT_LEGACY_KEY_FIELD) is not None
                ]
                
                if batch_abs_nr_values:
                    self.stdout.write(
                        f"{log_prefix} Fetching child records for {len(batch_abs_nr_values)} "
                        f"parent AbsNr values from batch {batch_index + 1}..."
                    )
                    
                    # Prepare filters for child records using only this batch's parent IDs
                    child_batch_filters = {
                        "parent_record_ids": batch_abs_nr_values,
                        "parent_field": self.CHILD_PARENT_LINK_FIELD
                    }
                    
                    # Extract child records for this batch
                    with child_pipeline.extractor:
                        child_source_data = child_pipeline.extractor.extract(
                            query_params=child_batch_filters,
                            fail_on_filter_error=options.get(
                                "fail_on_filter_error", True
                            )
                        )
                    
                    self.stdout.write(
                        f"{log_prefix} Extracted {len(child_source_data)} child records "
                        f"for batch {batch_index + 1}."
                    )
                    
                    if child_source_data:
                        # Transform child records
                        transformed_child_data = (
                            child_pipeline.transformer.transform(child_source_data)
                        )
                        
                        self.stdout.write(
                            f"{log_prefix} Transformed {len(transformed_child_data)} "
                            f"child records for batch {batch_index + 1}."
                        )
                        
                        # Load transformed child records
                        load_result = child_pipeline.loader.load(
                            transformed_child_data,
                            update_existing=(
                                options.get("force_update") or options.get("full")
                            ),
                        )
                        
                        # Update statistics
                        child_stats["created"] += load_result.created
                        child_stats["updated"] += load_result.updated
                        child_stats["skipped"] += load_result.skipped
                        child_stats["errors"] += load_result.errors
                        
                        self.stdout.write(self.style.SUCCESS(
                            f"{log_prefix} Child load for batch {batch_index + 1} finished: "
                            f"{load_result.created} created, "
                            f"{load_result.updated} updated, {load_result.skipped} skipped, "
                            f"{load_result.errors} errors."
                        ))
                        
                        # Display errors for this batch if any
                        if load_result.error_details:
                            self.stdout.write(self.style.WARNING(
                                f"{log_prefix} Child Load Errors in batch {batch_index + 1}:"
                            ))
                            for i, err in enumerate(load_result.error_details):
                                if i < 5:  # Show only first 5 errors per batch
                                    self.stdout.write(f"- {err}")
                                else:
                                    self.stdout.write(
                                        f"... and {len(load_result.error_details) - 5} "
                                        f"more errors."
                                    )
                                    break
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child records extracted for batch {batch_index + 1}, "
                            f"skipping transform and load."
                        )
                else:
                    self.stdout.write(
                        f"{log_prefix} No valid parent AbsNr values in batch {batch_index + 1}, "
                        f"skipping child record processing."
                    )
                
            except Exception as e:
                # Handle errors for this batch
                parent_sync_successful = False
                child_sync_successful = False
                self.stderr.write(self.style.ERROR(
                    f"{log_prefix} Error processing batch {batch_index + 1}: {e}"
                ))
                logger.error(
                    f"{log_prefix} Batch {batch_index + 1} processing failed: {e}",
                    exc_info=self.debug
                )
                if self.debug:
                    traceback.print_exc()
                # Continue with next batch despite the error
                continue
        
        # --- Step 3: Report Overall Status ---
        end_time = timezone.now()
        duration = (end_time - command_start_time).total_seconds()
        
        # Log completion of all batches
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 3: Summary of batch processing ==="
        ))
        
        # Report parent stats
        self.stdout.write(self.style.SUCCESS(
            f"{log_prefix} Parent ({self.PARENT_ENTITY_TYPE}) summary: "
            f"{parent_stats['created']} created, "
            f"{parent_stats['updated']} updated, "
            f"{parent_stats['skipped']} skipped, "
            f"{parent_stats['errors']} errors."
        ))
        
        # Report child stats
        self.stdout.write(self.style.SUCCESS(
            f"{log_prefix} Child ({self.CHILD_ENTITY_TYPE}) summary: "
            f"{child_stats['created']} created, "
            f"{child_stats['updated']} updated, "
            f"{child_stats['skipped']} skipped, "
            f"{child_stats['errors']} errors."
        ))
        
        logger.info(
            f"{log_prefix} Orchestrator finished in {duration:.2f} seconds."
        )
        self.stdout.write(
            f"\n{log_prefix} Sales record sync command finished in "
            f"{duration:.2f} seconds"
        )

        if parent_sync_successful and child_sync_successful:
            success_msg = (
                f"{log_prefix} All sales record sync steps completed successfully."
            )
            self.stdout.write(self.style.SUCCESS(success_msg))
            logger.info(success_msg)
        else:
            error_msg = (
                f"{log_prefix} One or more sales record sync steps failed. "
                f"Check logs for details."
            )
            logger.error(error_msg)
            # Only raise CommandError if child sync failed
            if not child_sync_successful:
                raise CommandError(error_msg)
            else:
                # Parent failed, child succeeded/skipped
                self.stdout.write(self.style.WARNING(error_msg))

