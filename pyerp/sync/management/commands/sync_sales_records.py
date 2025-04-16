"""Management command to synchronize sales records from legacy ERP."""

import traceback
from datetime import datetime # Added for date parsing

from django.core.management.base import CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger
from pyerp.sync.pipeline import PipelineFactory
from .base_sync_command import BaseSyncCommand


logger = get_logger(__name__)

# Helper function to apply date filter
def _apply_date_filter(records, filter_params):
    """Applies a date filter (like modified_date >= X) to a list of records."""
    if not filter_params or "filter_query" not in filter_params:
        return records # No filter to apply

    date_filter = None
    for f in filter_params["filter_query"]:
        # Assuming format [field_name, operator, value] and operator '>='
        # And the field is 'modified_date'
        if len(f) == 3 and f[1] == ">=" and f[0] == BaseSyncCommand.DEFAULT_TIMESTAMP_FIELD:
            try:
                # Parse the date string (YYYY-MM-DD)
                date_filter = {
                    "field": f[0],
                    "threshold": datetime.strptime(f[2], "%Y-%m-%d").date(),
                    "operator": f[1]
                }
                logger.debug(f"Date filter identified for client-side application: {date_filter}")
                break # Assuming only one date filter for now
            except ValueError:
                logger.warning(f"Could not parse date '{f[2]}' for client-side filtering. Skipping date filter.")
                return records # Cannot apply filter if date is invalid

    if not date_filter:
        return records # No applicable date filter found

    filtered_records = []
    field = date_filter["field"]
    threshold_date = date_filter["threshold"]

    for record in records:
        record_date_str = record.get(field)
        if not record_date_str:
            continue # Skip records without the date field

        try:
            # Assuming date format in record is like 'YYYY-MM-DD...'
            record_date = datetime.strptime(record_date_str.split('T')[0], "%Y-%m-%d").date()
            if record_date >= threshold_date:
                filtered_records.append(record)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date '{record_date_str}' in record for filtering. Skipping record: {record.get(Command.PARENT_LEGACY_KEY_FIELD, 'N/A')}")
            continue # Skip records with unparseable dates

    logger.info(f"Applied client-side date filter: {len(records)} -> {len(filtered_records)} records.")
    return filtered_records


class Command(BaseSyncCommand):
    """Command to sync sales records (Belege) and items (Belege_Pos)."""

    help = "Synchronize sales records (Belege) and items (Belege_Pos)"

    # Define legacy key field names
    PARENT_ENTITY_TYPE = "sales_records"
    PARENT_LEGACY_KEY_FIELD = "AbsNr"  # Key field in Belege
    CHILD_ENTITY_TYPE = "sales_record_items"
    CHILD_PARENT_LINK_FIELD = "AbsNr"  # Field in Belege_Pos linking to Belege

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
            f"{log_prefix} Initial query parameters built: "
            f"{initial_query_params}"
        )
        
        # Get batch size from options
        batch_size = options.get("batch_size", 100)
        self.stdout.write(f"{log_prefix} Using batch size: {batch_size}")
        
        # --- Step 1: Fetch All Parent Records (Belege) & Filter --- # noqa E501
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 1: Fetching & Filtering Parent "
            f"Records ({self.PARENT_LEGACY_KEY_FIELD}) ==="
        ))
        logger.info(
            f"{log_prefix} Starting Step 1: Fetch & Filter Parent Records"
        )
        parent_record_ids = []
        filtered_parent_data_map = {}  # Map ID to record data
        try:
            parent_pipeline_for_id_fetch = PipelineFactory.create_pipeline(
                parent_mapping
            )
            id_fetch_params = {
                **initial_query_params,  # Include base filters like --top
                # Date filter removed below, applied client-side
            }
            # Separate date filter for client-side use
            date_filter_params = (
                {"filter_query": initial_query_params.get("filter_query")}
                if initial_query_params.get("filter_query")
                else {}
            )

            # Remove date filter from the params passed to the extractor
            if "filter_query" in id_fetch_params:
                id_fetch_params["filter_query"] = [
                    f
                    for f in id_fetch_params["filter_query"]
                    if not (
                        len(f) == 3
                        and f[1] == ">="
                        and f[0] == self.DEFAULT_TIMESTAMP_FIELD
                    )
                ]
                # If filter_query becomes empty, remove it
                if not id_fetch_params["filter_query"]:
                    del id_fetch_params["filter_query"]

            logger.info(
                f"{log_prefix} Querying extractor for initial parent data "
                f"(pre-filter) with params: {id_fetch_params}"
            )

            # Clear cache if requested
            if options.get("clear_cache"):
                self.stdout.write(
                    f"{log_prefix} Clearing parent "
                    f"({self.PARENT_ENTITY_TYPE}) extractor cache..."
                )
                parent_pipeline_for_id_fetch.extractor.clear_cache()

            # --- Use extract_batched for initial fetch ---
            fetched_data_for_ids = []  # Initialize list to store results
            with parent_pipeline_for_id_fetch.extractor:  # Keep connection open
                logger.info(
                    f"{log_prefix} Using extract_batched for initial "
                    f"parent data fetch..."
                )
                id_batches = (
                    parent_pipeline_for_id_fetch.extractor.extract_batched(
                        query_params=id_fetch_params,
                        api_page_size=10000,  # Use fixed large API page size
                    )
                )
                # Aggregate results from the generator *inside* the with block
                logger.debug(
                    f"{log_prefix} Starting aggregation of parent data batches..."
                )
                for i, id_batch_data in enumerate(id_batches):
                    logger.debug(
                        f"{log_prefix} Aggregating parent data batch {i+1}..."
                    )
                    fetched_data_for_ids.extend(id_batch_data)
                logger.debug(
                    f"{log_prefix} Finished parent data aggregation."
                )
            # --- End extract_batched ---
            logger.info(
                f"{log_prefix} Extractor returned "
                f"{len(fetched_data_for_ids)} raw parent records."
            )

            # --- APPLY CLIENT-SIDE DATE FILTER ---
            filtered_parent_data = _apply_date_filter(
                fetched_data_for_ids, date_filter_params
            )
            logger.info(
                f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                f"parent records meeting date criteria."
            )
            # --- END CLIENT-SIDE FILTER ---

            # Store filtered data in a map and extract unique IDs
            parent_record_ids = []
            filtered_parent_data_map = {}
            for record in filtered_parent_data:
                record_id = record.get(self.PARENT_LEGACY_KEY_FIELD)
                if record_id is not None:
                    record_id_str = str(record_id)
                    if record_id_str not in filtered_parent_data_map:
                        parent_record_ids.append(record_id_str)
                        filtered_parent_data_map[record_id_str] = record

            # Ensure IDs are unique (should be due to map logic)
            parent_record_ids = list(set(parent_record_ids))

            self.stdout.write(
                f"{log_prefix} Found {len(parent_record_ids)} unique parent "
                f"record IDs ({self.PARENT_LEGACY_KEY_FIELD}) after "
                f"filtering."
            )
            logger.info(
                f"{log_prefix} Step 1: Found {len(parent_record_ids)} unique "
                f"parent IDs after filtering."
            )
            if self.debug and parent_record_ids:
                self.stdout.write(
                    f"{log_prefix} Sample Parent IDs: "
                    f"{parent_record_ids[:10]}..."
                )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"{log_prefix} Step 1 Failed: Could not fetch and filter "
                    f"parent records ({self.PARENT_LEGACY_KEY_FIELD}): {e}"
                )
            )
            logger.error(
                f"{log_prefix} Step 1: Failed to fetch/filter parents: {e}",
                exc_info=self.debug,
            )
            if self.debug:
                traceback.print_exc()
            # If we can't get data, abort.
            raise CommandError(
                f"Could not fetch/filter parent data, aborting sync. Error: {e}"
            )
            
        # --- Step 2: Process Belege and Belege_Pos records in batches ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 2: Processing parent and child "
            f"records in batches ==="
        ))
        logger.info(f"{log_prefix} Starting Step 2: Batch processing")
        
        # Apply top limit if specified (to the filtered IDs)
        if "top" in options and options["top"]:
            top_limit = int(options["top"])
            if len(parent_record_ids) > top_limit:
                parent_record_ids = parent_record_ids[:top_limit]
                # Also trim the map to keep it consistent (though not strictly needed) # noqa E501
                filtered_parent_data_map = {
                    k: v
                    for k, v in filtered_parent_data_map.items()
                    if k in parent_record_ids
                }
                self.stdout.write(
                    f"{log_prefix} Applied top limit: Processing only first "
                    f"{top_limit} parent IDs."
                )
                
        # Calculate batches based on filtered & limited IDs
        total_parent_batches = (
            len(parent_record_ids) + batch_size - 1
        ) // batch_size
        self.stdout.write(
            f"{log_prefix} Will process {len(parent_record_ids)} parent "
            f"records in {total_parent_batches} batches of ~{batch_size} "
            f"records each."
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
                f"\n{log_prefix} --- Processing Batch "
                f"{batch_index + 1}/{total_parent_batches} "
                f"({start_idx+1}-{end_idx} of "
                f"{len(parent_record_ids)}) ---"
            ))
            
            # ----- Step 2.1: Process parent records (Belege) for this batch ----- # noqa E501
            # --- REUSE DATA FROM STEP 1 ---
            parent_source_data = []
            missing_ids_in_batch = []
            for parent_id in batch_parent_ids:
                parent_record = filtered_parent_data_map.get(parent_id)
                if parent_record:
                    parent_source_data.append(parent_record)
                else:
                    # This should ideally not happen if Step 1 logic is correct
                    missing_ids_in_batch.append(parent_id)
                    logger.warning(
                        f"{log_prefix} Parent ID {parent_id} from batch "
                        f"{batch_index + 1} not found in filtered data map. "
                        f"Skipping."
                    )
            if missing_ids_in_batch:
                self.stdout.write(
                    self.style.WARNING(
                        f"{log_prefix} {len(missing_ids_in_batch)} parent "
                        f"IDs from batch {batch_index + 1} were missing "
                        f"from Step 1 results. Check logs."
                    )
                )

            self.stdout.write(
                f"{log_prefix} Using {len(parent_source_data)} pre-fetched "
                f"parent records for batch {batch_index + 1}."
            )
            # --- END REUSE DATA FROM STEP 1 ---

            try:
                # REMOVED: Redundant parent data extraction call

                # Initialize transformed_parent_data to ensure it exists
                transformed_parent_data = []

                if parent_source_data:
                    # Transform parent records
                    transformed_parent_data = (
                        parent_pipeline.transformer.transform(
                            parent_source_data
                        )
                    )

                    self.stdout.write(
                        f"{log_prefix} Transformed "
                        f"{len(transformed_parent_data)} parent records for "
                        f"batch {batch_index + 1}."
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

                    # Identify legacy IDs of parents that failed to load
                    failed_parent_legacy_ids = set()
                    unique_field = parent_pipeline.loader.config.get(
                        "unique_field", "legacy_id"
                    )
                    if load_result.error_details:
                        for error_detail in load_result.error_details:
                            record_data = error_detail.get("record")
                            if record_data and unique_field in record_data:
                                failed_parent_legacy_ids.add(
                                    str(record_data[unique_field])
                                )
                            else:
                                logger.warning(
                                    f"{log_prefix} Could not extract unique "
                                    f"ID ({unique_field}) from parent load "
                                    f"error detail in batch "
                                    f"{batch_index + 1}: {error_detail}"
                                )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{log_prefix} Parent load for batch "
                            f"{batch_index + 1} finished: "
                            f"{load_result.created} created, "
                            f"{load_result.updated} updated, "
                            f"{load_result.skipped} skipped, "
                            f"{load_result.errors} errors."
                        )
                    )

                    # Display errors for this batch if any
                    if load_result.error_details:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{log_prefix} Parent Load Errors in "
                                f"batch {batch_index + 1}:"
                            )
                        )
                        for i, err in enumerate(load_result.error_details):
                            if i < 5:  # Show only first 5 errors per batch
                                self.stdout.write(f"- {err}")
                            else:
                                self.stdout.write(
                                    f"... and "
                                    f"{len(load_result.error_details) - 5}" # noqa E501
                                    f" more errors."
                                )
                                break
                else:
                    self.stdout.write(
                        f"{log_prefix} No parent records obtained for batch "
                        f"{batch_index + 1} from Step 1 data, skipping "
                        f"parent transform and load."
                    )

                # ----- Step 2.2: Process child records (Belege_Pos) for this batch ----- # noqa E501
                # Get legacy IDs from successfully transformed parent records
                intended_parent_ids = [
                    str(record.get(unique_field))
                    for record in transformed_parent_data
                    if record.get(unique_field) is not None
                ]

                # Determine IDs of successfully loaded parents
                successful_parent_ids = list(
                    set(intended_parent_ids) - failed_parent_legacy_ids
                )

                if successful_parent_ids:
                    self.stdout.write(
                        f"{log_prefix} Fetching child records for "
                        f"{len(successful_parent_ids)} successful parent "
                        f"AbsNr values from batch {batch_index + 1}..."
                    )

                    # Prepare filters for child records
                    child_batch_filters = {
                        "parent_record_ids": successful_parent_ids,
                        "parent_field": self.CHILD_PARENT_LINK_FIELD,
                    }
                    # Add back any *other* non-date filters from initial
                    if initial_query_params:
                        for key, value in initial_query_params.items():
                            if key not in ["$top", "filter_query"] and \
                               key not in child_batch_filters:
                                child_batch_filters[key] = value
                                logger.debug(
                                    f"Adding non-date filter '{key}' to "
                                    f"child batch query."
                                )

                    # Extract child records for this batch
                    child_source_data = []
                    with child_pipeline.extractor:
                        # Assuming child extractor *might* support batching
                        # If not, .extract() is likely fine here too
                        try:
                            child_batches = (
                                child_pipeline.extractor.extract_batched(
                                    query_params=child_batch_filters,
                                    api_page_size=10000,
                                    fail_on_filter_error=options.get(
                                        "fail_on_filter_error", True
                                    ),
                                )
                            )
                            for batch_data in child_batches:
                                child_source_data.extend(batch_data)
                        except AttributeError:
                            # Fallback if extractor doesn't have extract_batched
                            logger.debug(
                                "Child extractor does not support "
                                "extract_batched, using extract()."
                            )
                            child_source_data = (
                                child_pipeline.extractor.extract(
                                    query_params=child_batch_filters,
                                    fail_on_filter_error=options.get(
                                        "fail_on_filter_error", True
                                    ),
                                )
                            )

                    self.stdout.write(
                        f"{log_prefix} Extracted {len(child_source_data)} "
                        f"child records for batch {batch_index + 1}."
                    )

                    if child_source_data:
                        # --- Filter child records by date as well ---
                        # Use the same date_filter_params derived earlier
                        filtered_child_data = _apply_date_filter(
                            child_source_data, date_filter_params
                        )
                        logger.info(
                            f"{log_prefix} Filtered "
                            f"{len(child_source_data)} -> "
                            f"{len(filtered_child_data)} child records "
                            f"meeting date criteria for batch "
                            f"{batch_index + 1}."
                        )
                        # --- END CHILD FILTER ---

                        if (
                            filtered_child_data
                        ):  # Only process if children remain after filtering
                            # Transform child records
                            transformed_child_data = (
                                child_pipeline.transformer.transform(
                                    filtered_child_data  # Use filtered data
                                )
                            )

                            self.stdout.write(
                                f"{log_prefix} Transformed "
                                f"{len(transformed_child_data)} child records "
                                f"for batch {batch_index + 1}."
                            )

                            # Load transformed child records
                            load_result = child_pipeline.loader.load(
                                transformed_child_data,
                                update_existing=(
                                    options.get("force_update")
                                    or options.get("full")
                                ),
                            )

                            # Update statistics
                            child_stats["created"] += load_result.created
                            child_stats["updated"] += load_result.updated
                            child_stats["skipped"] += load_result.skipped
                            child_stats["errors"] += load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Child load for batch "
                                    f"{batch_index + 1} finished: "
                                    f"{load_result.created} created, "
                                    f"{load_result.updated} updated, "
                                    f"{load_result.skipped} skipped, "
                                    f"{load_result.errors} errors."
                                )
                            )

                            # Display errors for this batch if any
                            if load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"{log_prefix} Child Load Errors in "
                                        f"batch {batch_index + 1}:"
                                    )
                                )
                                for i, err in enumerate(
                                    load_result.error_details
                                ):
                                    if (
                                        i < 5
                                    ):  # Show only first 5 errors per batch
                                        self.stdout.write(f"- {err}")
                                    else:
                                        self.stdout.write(
                                            f"... and "
                                            f"{len(load_result.error_details) - 5}" # noqa E501
                                            f" more errors."
                                        )
                                        break
                        else:
                            self.stdout.write(
                                f"{log_prefix} No child records remained "
                                f"after date filtering for batch "
                                f"{batch_index + 1}, skipping child transform "
                                f"and load."
                            )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child records extracted for "
                            f"batch {batch_index + 1}, skipping transform "
                            f"and load."
                        )
                else:
                    self.stdout.write(
                        f"{log_prefix} No successfully loaded parent "
                        f"AbsNr values in batch {batch_index + 1}, skipping "
                        f"child record processing."
                    )

            except Exception as e:
                # Handle errors for this batch
                parent_sync_successful = False
                child_sync_successful = False
                self.stderr.write(
                    self.style.ERROR(
                        f"{log_prefix} Error processing batch "
                        f"{batch_index + 1}: {e}"
                    )
                )
                logger.error(
                    f"{log_prefix} Batch {batch_index + 1} processing "
                    f"failed: {e}",
                    exc_info=self.debug,
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
                f"{log_prefix} All sales record sync steps completed "
                f"successfully."
            )
            self.stdout.write(self.style.SUCCESS(success_msg))
            logger.info(success_msg)
        else:
            error_msg = (
                f"{log_prefix} One or more sales record sync steps failed. "
                f"Check logs for details."
            )
            logger.error(error_msg)
            # Decide how to report overall failure. Example: raise error if
            # either step had issues leading to data inconsistency.
            # For now, raising error if any errors occurred.
            if parent_stats["errors"] > 0 or child_stats["errors"] > 0:
                raise CommandError(error_msg)
            else:
                # No errors, but steps might have been skipped due to batch errors
                self.stdout.write(self.style.WARNING(error_msg))

