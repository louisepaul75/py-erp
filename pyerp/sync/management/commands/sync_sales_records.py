"""Management command to synchronize sales records from legacy ERP."""

import traceback
import datetime  # Use the datetime module directly
import tempfile
from pathlib import Path
import pandas as pd  # Import pandas

import pyarrow.parquet as pq

from django.core.management.base import CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger
from pyerp.sync.pipeline import PipelineFactory
from .base_sync_command import BaseSyncCommand


logger = get_logger(__name__)


# Helper function to apply date filter
def _apply_date_filter(records, filter_params, target_date_field: str):
    """Apply a date filter (>= threshold) to a list of records.

    Assumes the target_date_field in records contains date/datetime objects
    or None.
    """
    if not filter_params or "filter_query" not in filter_params:
        return records  # No filter to apply

    date_filter = None
    for f in filter_params["filter_query"]:
        # Assuming format [field_name, operator, value] and operator '>='
        # Check if the field matches the target date field for this command
        if len(f) == 3 and f[1] == ">=" and f[0] == target_date_field:
            try:
                # Parse the date string (YYYY-MM-DD) from the filter params
                date_filter = {
                    "field": f[0],
                    "threshold": datetime.datetime.strptime(
                        f[2], "%Y-%m-%d"
                    ).date(),
                    "operator": f[1],
                }
                logger.debug(
                    "Date filter identified for client-side application: %s",
                    date_filter,
                )
                break  # Assuming only one date filter for now
            except ValueError:
                logger.warning(
                    "Could not parse date '%s' for client-side filtering. "
                    "Skipping date filter.",
                    f[2],
                )
                return records  # Cannot apply filter if date is invalid

    if not date_filter:
        return records  # No applicable date filter found

    filtered_records = []
    field = date_filter["field"]
    threshold_date = date_filter["threshold"]

    for record in records:
        record_date_value = record.get(field)
        if not record_date_value:
            continue  # Skip records without the date field

        record_date = None
        try:
            # --- Simplified: Assume date/datetime object or convertible ---
            if isinstance(record_date_value, datetime.datetime):
                record_date = record_date_value.date()
            elif isinstance(record_date_value, datetime.date):
                record_date = record_date_value
            # Handle pd.Timestamp or similar duck-typed objects
            elif (
                hasattr(record_date_value, "year")
                and hasattr(record_date_value, "month")
                and hasattr(record_date_value, "day")
            ):
                try:
                    record_date = datetime.date(
                        record_date_value.year,
                        record_date_value.month,
                        record_date_value.day,
                    )
                except (ValueError, TypeError):
                    # Handle potential issues with year/month/day values
                    logger.warning(
                        "Could not convert object with date attributes to date "
                        "for field '%s'. Value: %s. Skipping record: %s",
                        field,
                        record_date_value,
                        record.get(Command.PARENT_LEGACY_KEY_FIELD, "N/A"),
                    )
                    continue  # Skip records with problematic dates
            else:
                # Log if unexpected type is encountered after pre-parsing
                logger.warning(
                    "Unexpected type '%s' found in date field '%s' during "
                    "filtering. Value: %s. Skipping record: %s",
                    type(record_date_value),
                    field,
                    record_date_value,
                    record.get(Command.PARENT_LEGACY_KEY_FIELD, "N/A"),
                )
                continue
            # --- End Simplified ---

            # Now compare dates
            if record_date and record_date >= threshold_date:
                filtered_records.append(record)

        except (ValueError, TypeError) as e:
            # Catch errors during string parsing or comparison
            logger.warning(
                "Error processing date value '%s' ('%s') in record for "
                "filtering: %s. Skipping record: %s",
                record_date_value,
                type(record_date_value),
                e,
                record.get(Command.PARENT_LEGACY_KEY_FIELD, "N/A"),
            )
            continue  # Skip records with problematic dates

    logger.info(
        "Applied client-side date filter: %d -> %d records.",
        len(records),
        len(filtered_records),
    )

    # --- Add logging for date range of filtered records ---
    if filtered_records and date_filter:  # Ensure filter was active
        min_date_found = None
        max_date_found = None
        field = date_filter["field"]

        for record in filtered_records:
            record_date_value = record.get(field)
            if not record_date_value:
                continue

            record_date = None
            try:
                # --- Simplified conversion logic (repeated from above) ---
                if isinstance(record_date_value, datetime.datetime):
                    record_date = record_date_value.date()
                elif isinstance(record_date_value, datetime.date):
                    record_date = record_date_value
                elif (
                    hasattr(record_date_value, "year")
                    and hasattr(record_date_value, "month")
                    and hasattr(record_date_value, "day")
                ):
                    try:
                        record_date = datetime.date(
                            record_date_value.year,
                            record_date_value.month,
                            record_date_value.day,
                        )
                    except (ValueError, TypeError):
                        continue  # Skip if invalid date components
                else:
                    continue  # Skip unexpected types for range check
                # --- End Simplified ---

                # Update min/max
                if record_date:
                    if min_date_found is None or record_date < min_date_found:
                        min_date_found = record_date
                    if max_date_found is None or record_date > max_date_found:
                        max_date_found = record_date

            except (ValueError, TypeError):
                # Should not happen often if record passed filter
                logger.warning(
                    "Could not re-parse date '%s' for range check. "
                    "Record ID: %s",
                    record_date_value,
                    record.get(Command.PARENT_LEGACY_KEY_FIELD, "N/A"),
                )
                continue  # Skip if invalid date components

        if min_date_found and max_date_found:
            logger.info(
                "Filtered records '%s' date range: %s to %s",
                field,
                min_date_found.strftime("%Y-%m-%d"),
                max_date_found.strftime("%Y-%m-%d"),
            )
        elif min_date_found:  # Handle case with only one valid date
            logger.info(
                "Filtered records '%s' single date found: %s",
                field,
                min_date_found.strftime("%Y-%m-%d"),
            )
    # --- End logging for date range ---

    return filtered_records


class Command(BaseSyncCommand):
    """Command to sync sales records (Belege) and items (Belege_Pos)."""

    help = "Synchronize sales records (Belege) and items (Belege_Pos)"

    # Define legacy key field names
    PARENT_ENTITY_TYPE = "sales_records"
    PARENT_LEGACY_KEY_FIELD = "AbsNr"  # Key field in Belege
    CHILD_ENTITY_TYPE = "sales_record_items"
    CHILD_PARENT_LINK_FIELD = "AbsNr"  # Field in Belege_Pos linking to Belege

    # Date field for filtering in this command
    DATE_FILTER_FIELD = "Datum"
    # API Page Size for extract_batched
    API_PAGE_SIZE = 100000  # Large page size for full-load fetches

    def add_arguments(self, parser):
        """Add command arguments, inheriting from BaseSyncCommand."""
        super().add_arguments(parser)
        # Add the new full-load argument
        parser.add_argument(
            "--full-load",
            action="store_true",
            help=(
                "Fetch ALL parent and ALL related child records upfront, "
                "save them temporarily, then process/load in batches from "
                "temporary files. Ignores --batch-size during fetch, uses "
                "large API page size."
            ),
        )
        # Base class handles: --full, --batch-size, --top, --filters, --debug,
        # --days, --fail-on-filter-error, --clear-cache

    # --- Override build_query_params to use DATE_FILTER_FIELD ---
    def build_query_params(self, options, mapping=None):
        """Build query params using the command-specific date field."""
        # Call the base method first
        query_params = super().build_query_params(options, mapping)

        # Replace default date filter ('modified_date') with 'Datum' if --days used
        if options.get("days") is not None and "filter_query" in query_params:
            original_filter_query = query_params.get("filter_query", [])
            new_filter_query = []
            date_filter_value = None

            # Find and remove the default date filter if present
            for f in original_filter_query:
                if (
                    len(f) == 3
                    and f[1] == ">="
                    and f[0] == self.DEFAULT_TIMESTAMP_FIELD  # Default field
                ):
                    date_filter_value = f[2]  # Store the date value
                    logger.debug(
                        f"Replacing default date filter "
                        f"'{self.DEFAULT_TIMESTAMP_FIELD}' with "
                        f"'{self.DATE_FILTER_FIELD}'."
                    )
                else:
                    new_filter_query.append(f)  # Keep other filters

            # Add the correct date filter
            if date_filter_value is not None:
                new_filter_query.append(
                    [self.DATE_FILTER_FIELD, ">=", date_filter_value]
                )
                logger.debug(
                    f"Added command date filter: "
                    f"['{self.DATE_FILTER_FIELD}', '>=', '{date_filter_value}']"
                )

            # Update query_params
            if new_filter_query:
                query_params["filter_query"] = new_filter_query
            elif "filter_query" in query_params:
                del query_params["filter_query"]  # Remove empty list

        return query_params
    # --- End Override ---

    def handle(self, *args, **options):
        """Orchestrate the multi-stage sync process with batch processing."""
        command_start_time = timezone.now()
        self.debug = options.get("debug", False)
        log_prefix = f"[sync_sales_records - {command_start_time.isoformat()}]"
        logger.info(
            f"{log_prefix} Starting sales record & items sync orchestrator..."
        )
        self.stdout.write(
            f"{log_prefix} Starting sales record sync process at "
            f"{command_start_time}"
        )

        # --- Check sync mode ---
        is_full_load = options.get("full_load", False)
        if is_full_load:
            self.stdout.write(
                self.style.NOTICE(f"{log_prefix} Running in --full-load mode.")
            )
        else:
            # TODO: Implement standard batch-fetch mode
            raise CommandError(
                f"{log_prefix} Standard batch-fetch mode not yet implemented. "
                f"Please use --full-load."
            )
            # self.stdout.write(
            #     self.style.NOTICE(
            #         f"{log_prefix} Running in standard batch-fetch mode."
            #     )
            # )

        # Fetch mappings first (common to both modes)
        try:
            parent_mapping = self.get_mapping(
                entity_type=self.PARENT_ENTITY_TYPE
            )
            child_mapping = self.get_mapping(
                entity_type=self.CHILD_ENTITY_TYPE
            )
        except CommandError as e:
            self.stderr.write(
                self.style.ERROR(
                    f"{log_prefix} Failed to get required sync mappings: {e}"
                )
            )
            raise CommandError(
                "Sync cannot proceed without required mappings."
            ) from e

        # Build initial query parameters (common to both modes)
        initial_query_params = self.build_query_params(options, parent_mapping)
        logger.info(
            f"{log_prefix} Initial query parameters built: "
            f"{initial_query_params}"
        )

        # Get processing batch size (used for DB loading in both modes)
        process_batch_size = options.get("batch_size", 100)
        self.stdout.write(
            f"{log_prefix} Using DB processing batch size: {process_batch_size}"
        )

        # Initialize statistics (common to both modes)
        parent_stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
        child_stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
        sync_successful = True  # Consolidated success flag

        # Create pipelines (common to both modes)
        parent_pipeline = PipelineFactory.create_pipeline(parent_mapping)
        child_pipeline = PipelineFactory.create_pipeline(child_mapping)

        # =====================================================================
        # --- FULL-LOAD MODE ---
        # =====================================================================
        if is_full_load:
            with tempfile.TemporaryDirectory(
                prefix="pyerp_sync_"
            ) as temp_dir_name:
                temp_dir = Path(temp_dir_name)
                parents_file = temp_dir / "parents.parquet"
                children_file = temp_dir / "children.parquet"
                # Track successful parent loads
                successfully_loaded_parent_ids = set()
                parent_record_count = 0
                child_record_count = 0

                try:
                    # --- Step 1a: Fetch All Parent Records & Filter ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 1a: Fetching & Filtering "
                            f"ALL Parent Records ({self.PARENT_LEGACY_KEY_FIELD}) ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 1a: Fetch & Filter Parents"
                    )

                    id_fetch_params = {**initial_query_params}
                    date_filter_params = (
                        {"filter_query": initial_query_params.get("filter_query")}
                        if initial_query_params.get("filter_query")
                        else {}
                    )

                    # Remove date filter from API query (applied client-side)
                    if "filter_query" in id_fetch_params:
                        original_filters = id_fetch_params["filter_query"]
                        id_fetch_params["filter_query"] = [
                            f for f in original_filters
                            if not (
                                len(f) == 3
                                and f[1] == ">="
                                and f[0] == self.DATE_FILTER_FIELD
                            )
                        ]
                        if not id_fetch_params["filter_query"]: 
                            del id_fetch_params["filter_query"] # Cleanup
                        if len(id_fetch_params.get("filter_query", [])) < len(original_filters):
                            logger.info(
                                f"{log_prefix} Removed date filter for client-side processing."
                            )

                    logger.info(
                        f"{log_prefix} Querying extractor for ALL parent data "
                        f"(pre-filter) with params: {id_fetch_params}, "
                        f"API page size: {self.API_PAGE_SIZE}"
                    )

                    if options.get("clear_cache"):
                        self.stdout.write(
                            f"{log_prefix} Clearing parent extractor cache..."
                        )
                        parent_pipeline.extractor.clear_cache()

                    all_parent_data = []
                    with parent_pipeline.extractor:
                        batches = parent_pipeline.extractor.extract_batched(
                            query_params=id_fetch_params,
                            api_page_size=self.API_PAGE_SIZE,
                        )
                        for i, batch_data in enumerate(batches):
                            batch_num = i + 1
                            self.stdout.write(
                                f"\r{log_prefix} Fetched parent batch {batch_num}...",
                                ending="",
                            )
                            all_parent_data.extend(batch_data)
                        self.stdout.write( # Overwrite last status message
                            f"\r{log_prefix} Fetched {len(all_parent_data)} total "
                            f"raw parent records. Done."
                        )
                        # Add a newline after finishing the \r updates
                        self.stdout.write("")
                    logger.info(
                        f"{log_prefix} Extractor finished. Fetched "
                        f"{len(all_parent_data)} raw parent records."
                    )

                    # --- Assume extractor provides datetime.date objects ---
                    logger.info(
                        f"{log_prefix} Skipping date pre-processing."
                    )

                    # Apply Client-Side Date Filter
                    filtered_parent_data = _apply_date_filter(
                        all_parent_data, date_filter_params, self.DATE_FILTER_FIELD
                    )
                    logger.info(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                        f"parent records meeting date criteria."
                    )
                    self.stdout.write(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                        f"parent records post-date filter."
                    )
                    all_parent_data = None  # Free memory

                    # Apply Top Limit (after filtering)
                    if options.get("top"):
                        top_limit = int(options["top"])
                        if len(filtered_parent_data) > top_limit:
                            self.stdout.write(
                                f"{log_prefix} Applying --top limit: {top_limit}"
                            )
                            filtered_parent_data = filtered_parent_data[:top_limit]
                            logger.info(
                                f"{log_prefix} Applied top limit. Now "
                                f"{len(filtered_parent_data)} parent records."
                            )

                    # --- Step 1b: Save Filtered Parents to Parquet & Collect IDs ---
                    parent_ids_to_fetch_children_for = set()
                    if filtered_parent_data:
                        self.stdout.write(
                            f"{log_prefix} Saving {len(filtered_parent_data)} parents "
                            f"to {parents_file}..."
                        )
                        try:
                            # --- Create Pandas DataFrame ---
                            parent_df = pd.DataFrame(filtered_parent_data)
                            parent_record_count = len(parent_df)

                            # --- Explicitly convert problematic columns to string --- # noqa E501
                            if 'Termin' in parent_df.columns:
                                logger.debug("%s Converting 'Termin' column to string before saving.", log_prefix) # noqa E501
                                # Apply conversion row-wise, handle None explicitly
                                parent_df['Termin'] = parent_df['Termin'].apply(lambda x: x.isoformat() if isinstance(x, (datetime.datetime, datetime.date)) else str(x) if x is not None else None) # noqa E501

                            # --- Write Pandas DataFrame to Parquet ---
                            logger.info(
                                "%s Writing parent DataFrame to %s...",
                                log_prefix, parents_file
                            )
                            parent_df.to_parquet(parents_file, index=False)
                            logger.info("%s Parent data saved to Parquet.", log_prefix) # noqa E501

                            # Extract IDs after saving (using DataFrame)
                            if self.PARENT_LEGACY_KEY_FIELD in parent_df.columns: # noqa E501
                                parent_ids_to_fetch_children_for = set(
                                    parent_df[self.PARENT_LEGACY_KEY_FIELD].dropna().astype(str).unique() # noqa E501
                                )
                            else:
                                logger.warning(
                                    "%s Parent legacy key field '%s' not found " # noqa E501
                                    "in DataFrame columns. Cannot fetch children.", # noqa E501
                                    log_prefix, self.PARENT_LEGACY_KEY_FIELD
                                )
                                parent_ids_to_fetch_children_for = set()

                            self.stdout.write(
                                f"{log_prefix} Saved {parent_record_count} "
                                f"parents. Found "
                                f"{len(parent_ids_to_fetch_children_for)} "
                                f"unique parent IDs."
                            )
                            logger.info(
                                "%s Saved %d parents to Parquet. Found %d "
                                "unique IDs.", log_prefix, parent_record_count,
                                len(parent_ids_to_fetch_children_for)
                            )
                            # --- End Table/ID code ---
                        except Exception as e:
                            # Catch child Parquet errors
                            error_msg = (
                                "Failed during child DataFrame processing "
                                "or Parquet writing"
                            )
                            logger.error(
                                "%s %s: %s", log_prefix, error_msg, e,
                                exc_info=self.debug,
                            )
                            if self.debug:
                                traceback.print_exc()
                            raise CommandError(
                                f"{error_msg}: {e}"
                            ) from e
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent records remain after filtering. "
                            f"Skipping child fetch and processing."
                        )
                        parent_ids_to_fetch_children_for = set()

                    filtered_parent_data = None  # Free memory

                    # --- Step 1c: Fetch All Child Records ---
                    if parent_ids_to_fetch_children_for: # Still check if parents were found, even if not filtering by them # noqa E501
                        num_parents = len(parent_ids_to_fetch_children_for)
                        step1c_msg = (
                            f"=== Step 1c: Fetching ALL Child Records ===" # Updated message # noqa E501
                        )
                        self.stdout.write(
                            self.style.NOTICE(f"{log_prefix} {step1c_msg}")
                        )
                        logger.info(
                            f"{log_prefix} Starting Step 1c: Fetch ALL Children" # noqa E501
                        )

                        # Fetch *all* child records without API filtering
                        child_fetch_params = {}

                        logger.info(
                            f"{log_prefix} Querying extractor for ALL child data (no API filters). " # noqa E501
                            f"API page size: {self.API_PAGE_SIZE}" # noqa E501
                        )

                        all_child_data = []
                        with child_pipeline.extractor:
                            batches = child_pipeline.extractor.extract_batched(
                                query_params=child_fetch_params,
                                api_page_size=self.API_PAGE_SIZE,
                            )
                            for i, batch_data in enumerate(batches):
                                batch_num = i + 1
                                self.stdout.write(
                                    f"\r{log_prefix} Fetched child batch {batch_num}...", # noqa E501
                                    ending="",
                                )
                                all_child_data.extend(batch_data)
                            self.stdout.write( # Overwrite last status
                                f"\r{log_prefix} Fetched {len(all_child_data)} total " # noqa E501
                                f"raw child records. Done."
                            )
                            # Add a newline after finishing the \r updates
                            self.stdout.write("")

                        logger.info(
                            f"{log_prefix} Extractor returned {len(all_child_data)} " # noqa E501
                            f"raw child records."
                        )

                        # --- Assume extractor provides datetime.date objects ---
                        logger.info(
                            f"{log_prefix} Skipping child date pre-processing." # noqa E501
                        )

                        # Save Children to Parquet
                        if all_child_data:
                            self.stdout.write(
                                f"{log_prefix} Saving {len(all_child_data)} children "
                                f"to {children_file}..."
                            )
                            try:
                                # --- Create Pandas DataFrame ---
                                child_df = pd.DataFrame(all_child_data)
                                child_record_count = len(child_df)

                                # --- Explicitly convert problematic columns to string --- # noqa E501
                                if 'Termin' in child_df.columns:
                                    logger.debug("%s Converting child 'Termin' column to string.", log_prefix) # noqa E501
                                    # Apply conversion row-wise, handle None explicitly
                                    child_df['Termin'] = child_df['Termin'].apply(lambda x: x.isoformat() if isinstance(x, (datetime.datetime, datetime.date)) else str(x) if x is not None else None) # noqa E501
                                # Add other potential problematic columns here if needed # noqa E501

                                # --- Write Pandas DataFrame to Parquet ---
                                logger.info(
                                    "%s Writing child DataFrame to %s...",
                                    log_prefix, children_file
                                )
                                child_df.to_parquet(children_file, index=False)
                                logger.info("%s Child data saved to Parquet.", log_prefix) # noqa E501

                                self.stdout.write(
                                    f"{log_prefix} Saved {child_record_count} "
                                    f"children."
                                )
                            except Exception as e:
                                # Catch child Parquet errors
                                error_msg = (
                                    "Failed during child DataFrame processing "
                                    "or Parquet writing"
                                )
                                logger.error(
                                    "%s %s: %s", log_prefix, error_msg, e,
                                    exc_info=self.debug,
                                )
                                if self.debug:
                                    traceback.print_exc()
                                raise CommandError(
                                    f"{error_msg}: {e}"
                                ) from e
                        else:
                            self.stdout.write(
                                f"{log_prefix} No child records found for the "
                                f"fetched parents."
                            )
                            logger.info(
                                "%s No child records found.", log_prefix
                            )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent IDs found, skipping child " # noqa E501
                            f"fetch."
                        )

                    # --- Step 2a: Process Parents from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2a: Processing "
                            f"{parent_record_count} Parents from {parents_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2a: Processing Parents" # noqa E501
                    )

                    if parents_file.exists() and parent_record_count > 0:
                        parent_pf = pq.ParquetFile(parents_file)
                        total_parent_batches = (
                            parent_record_count + process_batch_size - 1
                        ) // process_batch_size
                        self.stdout.write(
                            f"{log_prefix} Processing parents in {total_parent_batches} " # noqa E501
                            f"batches of size {process_batch_size}."
                        )
                        parent_unique_field = parent_pipeline.loader.config.get( # noqa E501
                            "unique_field", "legacy_id"
                        )

                        for i, batch in enumerate(
                            parent_pf.iter_batches(batch_size=process_batch_size) # noqa E501
                        ):
                            batch_num = i + 1
                            self.stdout.write(
                                f"{log_prefix} --- Processing Parent Batch "
                                f"{batch_num}/{total_parent_batches} ---"
                            )
                            # Convert Arrow batch to list of dicts
                            parent_source_data = batch.to_pylist()

                            if not parent_source_data:
                                self.stdout.write(
                                    f"{log_prefix} Parent Batch {batch_num} is empty, " # noqa E501
                                    f"skipping."
                                )
                                continue

                            self.stdout.write(
                                f"{log_prefix} Transforming {len(parent_source_data)} "
                                f"parent records..."
                            )
                            transformed_parent_data = (
                                parent_pipeline.transformer.transform(
                                    parent_source_data
                                )
                            )
                            self.stdout.write(
                                f"{log_prefix} Loading {len(transformed_parent_data)} "
                                f"transformed parents..."
                            )

                            parent_load_result = parent_pipeline.loader.load(
                                transformed_parent_data,
                                update_existing=(
                                    options.get("force_update") or options.get("full") # noqa E501
                                ),
                            )

                            parent_stats["created"] += parent_load_result.created # noqa E501
                            parent_stats["updated"] += parent_load_result.updated # noqa E501
                            parent_stats["skipped"] += parent_load_result.skipped # noqa E501
                            parent_stats["errors"] += parent_load_result.errors

                            # Collect successfully loaded parent IDs
                            intended_ids = {
                                str(rec.get(parent_unique_field))
                                for rec in transformed_parent_data
                                if rec.get(parent_unique_field) is not None
                            }
                            failed_ids = set()
                            if parent_load_result.error_details:
                                for err_detail in parent_load_result.error_details: # noqa E501
                                    rec = err_detail.get("record")
                                    if rec and parent_unique_field in rec:
                                        # Ensure value exists before casting
                                        rec_id = rec.get(parent_unique_field)
                                        if rec_id is not None:
                                            failed_ids.add(str(rec_id))
                            successful_ids_in_batch = intended_ids - failed_ids
                            successfully_loaded_parent_ids.update(
                                successful_ids_in_batch
                            )

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Parent Batch {batch_num} finished: " # noqa E501
                                    f"{parent_load_result.created} C, "
                                    f"{parent_load_result.updated} U, "
                                    f"{parent_load_result.skipped} S, "
                                    f"{parent_load_result.errors} E. "
                                    f"({len(successful_ids_in_batch)} successful loads)" # noqa E501
                                )
                            )
                            if parent_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Parent Errors (Batch {batch_num}): "
                                        f"{len(parent_load_result.error_details)}" # noqa E501
                                    )
                                )
                                # Log first few errors
                                for k, err in enumerate(
                                    parent_load_result.error_details[:5]
                                ):
                                    self.stdout.write(f"  - {err}")
                                if len(parent_load_result.error_details) > 5:
                                    self.stdout.write(
                                        f"  ... and "
                                        f"{len(parent_load_result.error_details) - 5} " # noqa E501
                                        f"more."
                                    )
                            if parent_load_result.errors > 0:
                                sync_successful = False # Mark sync as failed

                        self.stdout.write(
                            f"{log_prefix} Finished processing all parent batches. " # noqa E501
                            f"Total successful parent loads: "
                            f"{len(successfully_loaded_parent_ids)}"
                        )
                        logger.info(
                            f"{log_prefix} Finished parent processing. "
                            f"{len(successfully_loaded_parent_ids)} successfully loaded." # noqa E501
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent data file found or no records " # noqa E501
                            f"to process."
                        )
                        logger.info(f"{log_prefix} Skipping parent processing step.") # noqa E501

                    # --- Step 2b: Process Children from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2b: Processing "
                            f"{child_record_count} Children from {children_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2b: Processing Children" # noqa E501
                    )

                    if (
                        children_file.exists()
                        and child_record_count > 0
                        and successfully_loaded_parent_ids
                    ):
                        child_pf = pq.ParquetFile(children_file)
                        total_child_batches = (
                            child_record_count + process_batch_size - 1
                        ) // process_batch_size
                        self.stdout.write(
                            f"{log_prefix} Processing children in "
                            f"{total_child_batches} batches of size "
                            f"{process_batch_size}."
                        )
                        child_parent_link_field = self.CHILD_PARENT_LINK_FIELD

                        for i, batch in enumerate(
                            child_pf.iter_batches(batch_size=process_batch_size) # noqa E501
                        ):
                            batch_num = i + 1
                            self.stdout.write(
                                f"{log_prefix} --- Processing Child Batch "
                                f"{batch_num}/{total_child_batches} ---"
                            )
                            child_source_data = batch.to_pylist()

                            if not child_source_data:
                                self.stdout.write(
                                    f"{log_prefix} Child Batch {batch_num} is empty, " # noqa E501
                                    f"skipping."
                                )
                                continue

                            # Filter children based on successfully loaded parents # noqa E501
                            filtered_child_data = [
                                rec for rec in child_source_data
                                if str(rec.get(child_parent_link_field))
                                in successfully_loaded_parent_ids
                            ]
                            skipped_count = len(child_source_data) - len(
                                filtered_child_data
                            )
                            if skipped_count > 0:
                                logger.info(
                                    f"{log_prefix} Batch {batch_num}: Filtered out " # noqa E501
                                    f"{skipped_count} children linked to unloaded parents." # noqa E501
                                )

                            if not filtered_child_data:
                                self.stdout.write(
                                    f"{log_prefix} No children in Batch {batch_num} " # noqa E501
                                    f"remain after filtering, skipping."
                                )
                                continue

                            self.stdout.write(
                                f"{log_prefix} Transforming {len(filtered_child_data)} "
                                f"child records..."
                            )
                            transformed_child_data = (
                                child_pipeline.transformer.transform(
                                    filtered_child_data
                                )
                            )
                            self.stdout.write(
                                f"{log_prefix} Loading {len(transformed_child_data)} "
                                f"transformed children..."
                            )

                            child_load_result = child_pipeline.loader.load(
                                transformed_child_data,
                                update_existing=(
                                    options.get("force_update") or options.get("full") # noqa E501
                                ),
                            )

                            child_stats["created"] += child_load_result.created # noqa E501
                            child_stats["updated"] += child_load_result.updated # noqa E501
                            child_stats["skipped"] += child_load_result.skipped # noqa E501
                            child_stats["errors"] += child_load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Child Batch {batch_num} finished: " # noqa E501
                                    f"{child_load_result.created} C, "
                                    f"{child_load_result.updated} U, "
                                    f"{child_load_result.skipped} S, "
                                    f"{child_load_result.errors} E."
                                )
                            )
                            if child_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Child Errors (Batch {batch_num}): "
                                        f"{len(child_load_result.error_details)}" # noqa E501
                                    )
                                )
                                # Log first few errors to stdout/log
                                for k, err in enumerate(
                                    child_load_result.error_details[:5]
                                ):
                                    err_msg = f"  - {err}"
                                    self.stdout.write(err_msg)
                                    logger.warning(f"{log_prefix} Child Load Error: {err_msg}") # noqa E501
                                if len(child_load_result.error_details) > 5:
                                    more_msg = (
                                        f"  ... and "
                                        f"{len(child_load_result.error_details) - 5} " # noqa E501
                                        f"more."
                                    )
                                    self.stdout.write(more_msg)
                                    logger.warning(f"{log_prefix} {more_msg}")

                            if child_load_result.errors > 0:
                                sync_successful = False # Mark sync as failed

                        self.stdout.write(
                            f"{log_prefix} Finished processing all child batches." # noqa E501
                        )
                        logger.info(f"{log_prefix} Finished child processing.")
                    elif not successfully_loaded_parent_ids:
                        self.stdout.write(
                            f"{log_prefix} No parents were successfully loaded, " # noqa E501
                            f"skipping child processing."
                        )
                        logger.warning(
                            f"{log_prefix} Skipping child processing - no parents loaded." # noqa E501
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child data file found or no records " # noqa E501
                            f"to process."
                        )
                        logger.info(f"{log_prefix} Skipping child processing step.") # noqa E501

                except Exception as e:
                    sync_successful = False
                    self.stderr.write(
                        self.style.ERROR(f"{log_prefix} Full-Load mode failed: {e}") # noqa E501
                    )
                    logger.error(
                        f"{log_prefix} Full-Load mode failed: {e}",
                        exc_info=self.debug,
                    )
                    if self.debug:
                        traceback.print_exc()
                    # Don't re-raise here, allow summary reporting

                # --- Step 3: Report Status ---
                end_time = timezone.now()
                duration = (end_time - command_start_time).total_seconds()

                self.stdout.write(
                    self.style.NOTICE(f"{log_prefix} === Step 3: Sync Summary ===") # noqa E501
                )

                # Report parent stats
                parent_summary = (
                    f"Parent ({self.PARENT_ENTITY_TYPE}) summary: "
                    f"{parent_stats['created']} C, {parent_stats['updated']} U, " # noqa E501
                    f"{parent_stats['skipped']} S, {parent_stats['errors']} E." # noqa E501
                )
                self.stdout.write(
                    self.style.SUCCESS(f"{log_prefix} {parent_summary}")
                )

                # Report child stats
                child_summary = (
                    f"Child ({self.CHILD_ENTITY_TYPE}) summary: "
                    f"{child_stats['created']} C, {child_stats['updated']} U, " # noqa E501
                    f"{child_stats['skipped']} S, {child_stats['errors']} E." # noqa E501
                )
                self.stdout.write(
                    self.style.SUCCESS(f"{log_prefix} {child_summary}")
                )

                log_summary = (
                    f"{log_prefix} Orchestrator finished in {duration:.2f} " # noqa E501
                    f"seconds. Mode: Full-Load. "
                    f"Parents: C={parent_stats['created']}, "
                    f"U={parent_stats['updated']}, S={parent_stats['skipped']}, " # noqa E501
                    f"E={parent_stats['errors']}. "
                    f"Children: C={child_stats['created']}, "
                    f"U={child_stats['updated']}, S={child_stats['skipped']}, " # noqa E501
                    f"E={child_stats['errors']}."
                )
                logger.info(log_summary)
                self.stdout.write(
                    f"{log_prefix} Sales record sync finished in "
                    f"{duration:.2f} seconds"
                )

                # Determine final status
                final_success = (
                    sync_successful
                    and parent_stats["errors"] == 0
                    and child_stats["errors"] == 0
                )

                if final_success:
                    success_msg = f"{log_prefix} Sync completed successfully."
                    self.stdout.write(self.style.SUCCESS(success_msg))
                    logger.info(success_msg)
                else:
                    error_msg = (
                        f"{log_prefix} Sync finished with errors. Check logs "
                        f"for details."
                    )
                    logger.error(error_msg)
                    # Raise CommandError to indicate failure to the OS/caller
                    raise CommandError(error_msg)


