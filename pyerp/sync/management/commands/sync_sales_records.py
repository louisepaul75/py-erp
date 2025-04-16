"""Management command to synchronize sales records from legacy ERP."""

import traceback
import datetime  # Use the datetime module directly
import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from django.core.management.base import CommandError
from django.utils import timezone

from pyerp.utils.logging import get_logger
from pyerp.sync.pipeline import PipelineFactory
from .base_sync_command import BaseSyncCommand
from pyerp.sync.loaders.base import LoadResult


logger = get_logger(__name__)


# Helper function to apply date filter
def _apply_date_filter(records, filter_params, target_date_field: str):
    """Applies a date filter (like target_date_field >= X) to a list of records.

    Assumes the target_date_field in records contains date/datetime objects or None.
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
        return records # No applicable date filter found

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
                # Use target_date_field for logging context if needed
                record.get(Command.PARENT_LEGACY_KEY_FIELD, "N/A"),
            )
            continue # Skip records with problematic dates

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
                        continue # Skip if invalid date components
                else:
                    continue # Skip unexpected types for range check
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
                continue

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

    # --- Define the specific date field for --days filtering in this command ---
    DATE_FILTER_FIELD = "Datum"
    # --- API Page Size for extract_batched ---
    API_PAGE_SIZE = 100000  # Increased page size for larger fetches

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

        # If a date filter was generated by the base method using the default
        # field name ('modified_date'), remove it and regenerate it using
        # the correct field name ('Datum').
        if options.get("days") is not None and "filter_query" in query_params:
            original_filter_query = query_params.get("filter_query", [])
            new_filter_query = []
            date_filter_value = None

            # Find and remove the default date filter if present
            for f in original_filter_query:
                if (
                    len(f) == 3
                    and f[1] == ">="
                    and f[0] == self.DEFAULT_TIMESTAMP_FIELD  # Check default base field
                ):
                    date_filter_value = f[2]  # Store the date value
                    logger.debug(
                        f"Removing default date filter based on "
                        f"'{self.DEFAULT_TIMESTAMP_FIELD}' to replace with "
                        f"'{self.DATE_FILTER_FIELD}' filter."
                    )
                else:
                    new_filter_query.append(f)  # Keep other filters

            # If we found and removed the default filter, add the correct one
            if date_filter_value is not None:
                new_filter_query.append(
                    [self.DATE_FILTER_FIELD, ">=", date_filter_value]
                )
                logger.debug(
                    f"Added command-specific date filter: "
                    f"['{self.DATE_FILTER_FIELD}', '>=', '{date_filter_value}']"
                )

            # Update query_params with the modified filter list
            if new_filter_query:
                query_params["filter_query"] = new_filter_query
            elif "filter_query" in query_params:
                # Remove empty filter_query list
                del query_params["filter_query"]

        return query_params
    # --- End Override ---

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

        # --- Check sync mode ---
        is_full_load = options.get("full_load", False)
        if is_full_load:
            self.stdout.write(
                self.style.NOTICE(f"{log_prefix} Running in --full-load mode.")
            )
        else:
            self.stdout.write(
                self.style.NOTICE(
                    f"{log_prefix} Running in standard batch-fetch mode."
                )
            )

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

        # Build initial query parameters from common args (common to both modes)
        initial_query_params = self.build_query_params(options, parent_mapping)
        logger.info(
            f"{log_prefix} Initial query parameters built: "
            f"{initial_query_params}"
        )

        # Get processing batch size from options (used for DB loading in both modes)
        process_batch_size = options.get("batch_size", 100)  # Renamed for clarity
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
                    # --- Step 1 (Full-Load): Fetch All Parent Records & Filter ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 1 (Full-Load): Fetching & "
                            f"Filtering ALL Parent Records "
                            f"({self.PARENT_LEGACY_KEY_FIELD}) ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 1 (Full-Load): Fetch & "
                        f"Filter Parents"
                    )

                    id_fetch_params = {**initial_query_params}
                    date_filter_params = (
                        {"filter_query": initial_query_params.get("filter_query")}
                        if initial_query_params.get("filter_query")
                        else {}
                    )

                    # Remove date filter from API query (applied client-side)
                    if "filter_query" in id_fetch_params:
                        id_fetch_params["filter_query"] = [
                            f
                            for f in id_fetch_params["filter_query"]
                            if not (
                                len(f) == 3
                                and f[1] == ">="
                                and f[0] == self.DATE_FILTER_FIELD
                            )
                        ]
                        if not id_fetch_params["filter_query"]:
                            del id_fetch_params["filter_query"]

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
                            self.stdout.write(
                                f"{log_prefix} Fetched parent batch {i+1}...",
                                ending="",
                            )
                            all_parent_data.extend(batch_data)
                        # Overwrite last message
                        self.stdout.write(
                            f"{log_prefix} Fetched parent batch {i+1}. Done."
                        )
                    logger.info(
                        f"{log_prefix} Extractor returned "
                        f"{len(all_parent_data)} raw parent records."
                    )
                    self.stdout.write(
                        f"{log_prefix} Fetched {len(all_parent_data)} "
                        f"raw parent records."
                    )

                    # Pre-process Date Field
                    logger.info(
                        f"{log_prefix} Pre-processing "
                        f"'{self.DATE_FILTER_FIELD}' field for parents..."
                    )
                    # (Reusing existing pre-processing logic - slightly adapted)
                    parsing_errors = 0
                    processed_count = 0
                    for record in all_parent_data:
                        date_str = record.get(self.DATE_FILTER_FIELD)
                        if isinstance(date_str, str):
                            try:
                                parsed_date = datetime.datetime.strptime(
                                    date_str, "%d!%m!%Y"
                                ).date()
                                record[self.DATE_FILTER_FIELD] = parsed_date
                                processed_count += 1
                            except (ValueError, TypeError):
                                parsing_errors += 1
                                record[self.DATE_FILTER_FIELD] = None
                                if parsing_errors < 10:
                                    logger.warning(
                                        f"{log_prefix} Could not parse parent "
                                        f"date string '{date_str}'. Setting "
                                        f"to None. Record ID: "
                                        f"{record.get(self.PARENT_LEGACY_KEY_FIELD, 'N/A')}"
                                    )
                                elif parsing_errors == 10:
                                    logger.warning(
                                        f"{log_prefix} Further parent date "
                                        f"parsing errors suppressed."
                                    )
                        elif date_str is not None:
                            pass  # Assume correct type or None
                    logger.info(
                        f"{log_prefix} Finished parent pre-processing. "
                        f"{processed_count} parsed, {parsing_errors} errors."
                    )


                    # Apply Client-Side Date Filter
                    filtered_parent_data = _apply_date_filter(
                        all_parent_data, date_filter_params, self.DATE_FILTER_FIELD
                    )
                    logger.info(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                        f"parent records."
                    )
                    self.stdout.write(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                        f"parent records post-date filter."
                    )
                    all_parent_data = None  # Free memory

                    # Apply Top Limit (after filtering)
                    if "top" in options and options["top"]:
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

                    # Save Filtered Parents to Parquet & Collect IDs
                    parent_ids_to_fetch_children_for = set()
                    if filtered_parent_data:
                        self.stdout.write(
                            f"{log_prefix} Saving {len(filtered_parent_data)} "
                            f"parents to {parents_file}..."
                        )
                        # Convert list of dicts to Arrow Table
                        try:
                            parent_table = pa.Table.from_pylist(
                                filtered_parent_data
                            )
                            pq.write_table(parent_table, parents_file)
                            parent_record_count = len(filtered_parent_data)
                            # Extract IDs after saving
                            for record in filtered_parent_data:
                                record_id = record.get(
                                    self.PARENT_LEGACY_KEY_FIELD
                                )
                                if record_id is not None:
                                    parent_ids_to_fetch_children_for.add(
                                        str(record_id)
                                    )
                            self.stdout.write(
                                f"{log_prefix} Saved {parent_record_count} parents. "
                                f"Found {len(parent_ids_to_fetch_children_for)} "
                                f"unique IDs."
                            )
                            logger.info(
                                f"{log_prefix} Saved {parent_record_count} parents "
                                f"to Parquet. Found "
                                f"{len(parent_ids_to_fetch_children_for)} unique IDs."
                            )
                        except Exception as e:
                            logger.error(
                                f"{log_prefix} Failed to write parents Parquet: {e}",
                                exc_info=self.debug,
                            )
                            raise CommandError(
                                f"Failed to write temporary parent data: {e}"
                            ) from e
                        finally:
                            parent_table = None  # Free memory
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent records remain after "
                            f"filtering. Skipping child fetch and processing."
                        )
                        parent_ids_to_fetch_children_for = set()  # Ensure empty

                    filtered_parent_data = None  # Free memory

                    # --- Step 1 (Full-Load): Fetch All Child Records ---
                    if parent_ids_to_fetch_children_for:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"{log_prefix} === Step 1 (Full-Load): "
                                f"Fetching ALL Child Records for "
                                f"{len(parent_ids_to_fetch_children_for)} Parents ==="
                            )
                        )
                        logger.info(
                            f"{log_prefix} Starting Step 1 (Full-Load): "
                            f"Fetch Children"
                        )

                        child_fetch_params = {
                            # Pass IDs
                            "parent_record_ids": list(
                                parent_ids_to_fetch_children_for
                            ),
                            "parent_field": self.CHILD_PARENT_LINK_FIELD,
                        }
                        # Add other non-date, non-top filters from initial
                        if initial_query_params:
                            for key, value in initial_query_params.items():
                                if (
                                    key not in ["$top", "filter_query"]
                                    and key not in child_fetch_params
                                ):
                                    child_fetch_params[key] = value
                                    logger.debug(
                                        f"Adding filter '{key}' to child fetch query."
                                    )

                        logger.info(
                            f"{log_prefix} Querying extractor for ALL child data "
                            f"with {len(parent_ids_to_fetch_children_for)} "
                            f"parent IDs. API page size: {self.API_PAGE_SIZE}"
                        )
                        # No need to clear child cache unless specifically
                        # requested (unlikely)

                        all_child_data = []
                        with child_pipeline.extractor:
                            batches = child_pipeline.extractor.extract_batched(
                                query_params=child_fetch_params,
                                api_page_size=self.API_PAGE_SIZE,
                            )
                            for i, batch_data in enumerate(batches):
                                self.stdout.write(
                                    f"{log_prefix} Fetched child batch {i+1}...",
                                    ending="",
                                )
                                all_child_data.extend(batch_data)
                            self.stdout.write(
                                f"{log_prefix} Fetched child batch {i+1}. Done."
                            )
                        logger.info(
                            f"{log_prefix} Extractor returned "
                            f"{len(all_child_data)} raw child records."
                        )
                        self.stdout.write(
                            f"{log_prefix} Fetched {len(all_child_data)} "
                            f"raw child records."
                        )

                        # Pre-process Date Field for Children
                        logger.info(
                            f"{log_prefix} Pre-processing "
                            f"'{self.DATE_FILTER_FIELD}' field for children..."
                        )
                        parsing_errors = 0
                        processed_count = 0
                        # For logging
                        child_unique_field = child_pipeline.loader.config.get(
                            "unique_field", "legacy_id"
                        )
                        for record in all_child_data:
                            date_str = record.get(self.DATE_FILTER_FIELD)
                            if isinstance(date_str, str):
                                try:
                                    parsed_date = datetime.datetime.strptime(
                                        date_str, "%d!%m!%Y"
                                    ).date()
                                    record[
                                        self.DATE_FILTER_FIELD
                                    ] = parsed_date
                                    processed_count += 1
                                except (ValueError, TypeError):
                                    parsing_errors += 1
                                    record[self.DATE_FILTER_FIELD] = None
                                    if parsing_errors < 10:
                                        logger.warning(
                                            f"{log_prefix} Could not parse child "
                                            f"date string '{date_str}'. Setting "
                                            f"to None. Record Key: "
                                            f"{record.get(child_unique_field, 'N/A')}"
                                        )
                                    elif parsing_errors == 10:
                                        logger.warning(
                                            f"{log_prefix} Further child date "
                                            f"parsing errors suppressed."
                                        )
                            elif date_str is not None:
                                pass
                        logger.info(
                            f"{log_prefix} Finished child pre-processing. "
                            f"{processed_count} parsed, {parsing_errors} errors."
                        )

                        # Save Children to Parquet
                        if all_child_data:
                            self.stdout.write(
                                f"{log_prefix} Saving {len(all_child_data)} "
                                f"children to {children_file}..."
                            )
                            try:
                                child_table = pa.Table.from_pylist(all_child_data)
                                pq.write_table(child_table, children_file)
                                child_record_count = len(all_child_data)
                                self.stdout.write(
                                    f"{log_prefix} Saved {child_record_count} "
                                    f"children."
                                )
                                logger.info(
                                    f"{log_prefix} Saved {child_record_count} "
                                    f"children to Parquet."
                                )
                            except Exception as e:
                                logger.error(
                                    f"{log_prefix} Failed to write children "
                                    f"Parquet: {e}",
                                    exc_info=self.debug,
                                )
                                raise CommandError(
                                    f"Failed to write temporary child data: {e}"
                                ) from e
                            finally:
                                child_table = None  # Free memory
                        else:
                            self.stdout.write(
                                f"{log_prefix} No child records found for the "
                                f"fetched parents."
                            )
                            logger.info(f"{log_prefix} No child records found.")

                        all_child_data = None  # Free memory
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent IDs found, "
                            f"skipping child fetch."
                        )

                    # --- Step 2 (Full-Load): Process Parents from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2 (Full-Load): Processing "
                            f"{parent_record_count} Parents from {parents_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2 (Full-Load): "
                        f"Processing Parents"
                    )

                    if parents_file.exists() and parent_record_count > 0:
                        parent_pf = pq.ParquetFile(parents_file)
                        total_parent_batches = (
                            parent_record_count + process_batch_size - 1
                        ) // process_batch_size
                        self.stdout.write(
                            f"{log_prefix} Processing in {total_parent_batches} "
                            f"batches of size {process_batch_size}."
                        )
                        parent_unique_field = parent_pipeline.loader.config.get(
                            "unique_field", "legacy_id"
                        )

                        for i, batch in enumerate(
                            parent_pf.iter_batches(batch_size=process_batch_size)
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
                                    f"{log_prefix} Parent Batch {batch_num} "
                                    f"is empty, skipping."
                                )
                                continue

                            self.stdout.write(
                                f"{log_prefix} Transforming "
                                f"{len(parent_source_data)} parent records..."
                            )
                            transformed_parent_data = (
                                parent_pipeline.transformer.transform(
                                    parent_source_data
                                )
                            )
                            self.stdout.write(
                                f"{log_prefix} Loading "
                                f"{len(transformed_parent_data)} transformed "
                                f"parents..."
                            )

                            parent_load_result = parent_pipeline.loader.load(
                                transformed_parent_data,
                                update_existing=(
                                    options.get("force_update")
                                    or options.get("full")
                                ),
                            )

                            parent_stats["created"] += parent_load_result.created
                            parent_stats["updated"] += parent_load_result.updated
                            parent_stats["skipped"] += parent_load_result.skipped
                            parent_stats["errors"] += parent_load_result.errors

                            # Collect successfully loaded parent IDs
                            intended_ids = {
                                str(rec.get(parent_unique_field))
                                for rec in transformed_parent_data
                                if rec.get(parent_unique_field) is not None
                            }
                            failed_ids = set()
                            if parent_load_result.error_details:
                                for err_detail in parent_load_result.error_details:
                                    rec = err_detail.get("record")
                                    if rec and parent_unique_field in rec:
                                        failed_ids.add(str(rec[parent_unique_field]))
                            successful_ids_in_batch = intended_ids - failed_ids
                            successfully_loaded_parent_ids.update(
                                successful_ids_in_batch
                            )

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Parent Batch {batch_num} finished: "
                                    f"{parent_load_result.created} created, "
                                    f"{parent_load_result.updated} updated, "
                                    f"{parent_load_result.skipped} skipped, "
                                    f"{parent_load_result.errors} errors. "
                                    f"({len(successful_ids_in_batch)} successful "
                                    f"loads)"
                                )
                            )
                            if parent_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"{log_prefix} Parent Load Errors "
                                        f"(Batch {batch_num}):"
                                    )
                                )
                                for k, err in enumerate(
                                    parent_load_result.error_details
                                ):
                                    if k < 5:
                                        self.stdout.write(f"- {err}")
                                    else:
                                        self.stdout.write(
                                            f"... and "
                                            f"{len(parent_load_result.error_details) - 5} "
                                            f"more."
                                        )
                                        break
                            if parent_load_result.errors > 0:
                                # Mark sync as potentially failed
                                sync_successful = False

                        self.stdout.write(
                            f"{log_prefix} Finished processing all parent "
                            f"batches. Total successful parent loads: "
                            f"{len(successfully_loaded_parent_ids)}"
                        )
                        logger.info(
                            f"{log_prefix} Finished parent processing. "
                            f"{len(successfully_loaded_parent_ids)} successfully "
                            f"loaded."
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent data file found or "
                            f"no records to process."
                        )
                        logger.info(f"{log_prefix} Skipping parent processing step.")


                    # --- Step 2 (Full-Load): Process Children from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2 (Full-Load): Processing "
                            f"{child_record_count} Children from {children_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2 (Full-Load): "
                        f"Processing Children"
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
                            f"{log_prefix} Processing in {total_child_batches} "
                            f"batches of size {process_batch_size}."
                        )
                        child_parent_link_field = self.CHILD_PARENT_LINK_FIELD

                        for i, batch in enumerate(
                            child_pf.iter_batches(batch_size=process_batch_size)
                        ):
                            batch_num = i + 1
                            self.stdout.write(
                                f"{log_prefix} --- Processing Child Batch "
                                f"{batch_num}/{total_child_batches} ---"
                            )
                            child_source_data = batch.to_pylist()

                            if not child_source_data:
                                self.stdout.write(
                                    f"{log_prefix} Child Batch {batch_num} "
                                    f"is empty, skipping."
                                )
                                continue

                            # Filter children based on successfully loaded parents
                            filtered_child_data = [
                                rec
                                for rec in child_source_data
                                if str(rec.get(child_parent_link_field))
                                in successfully_loaded_parent_ids
                            ]
                            skipped_count = len(child_source_data) - len(
                                filtered_child_data
                            )
                            if skipped_count > 0:
                                self.stdout.write(
                                    f"{log_prefix} Filtered out {skipped_count} "
                                    f"children linked to unloaded parents."
                                )
                                logger.info(
                                    f"{log_prefix} Batch {batch_num}: Filtered out "
                                    f"{skipped_count} children."
                                )

                            if not filtered_child_data:
                                self.stdout.write(
                                    f"{log_prefix} No children remaining in Batch "
                                    f"{batch_num} after filtering, skipping."
                                )
                                continue

                            self.stdout.write(
                                f"{log_prefix} Transforming "
                                f"{len(filtered_child_data)} child records..."
                            )
                            transformed_child_data = (
                                child_pipeline.transformer.transform(
                                    filtered_child_data
                                )
                            )
                            self.stdout.write(
                                f"{log_prefix} Loading "
                                f"{len(transformed_child_data)} transformed "
                                f"children..."
                            )

                            child_load_result = child_pipeline.loader.load(
                                transformed_child_data,
                                update_existing=(
                                    options.get("force_update")
                                    or options.get("full")
                                ),
                            )

                            child_stats["created"] += child_load_result.created
                            child_stats["updated"] += child_load_result.updated
                            child_stats["skipped"] += child_load_result.skipped
                            child_stats["errors"] += child_load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Batch {batch_num} finished. "
                                    f"Parents: {parent_load_result.created} C, "
                                    f"{parent_load_result.updated} U, "
                                    f"{parent_load_result.skipped} S, "
                                    f"{parent_load_result.errors} E. | "
                                    f"Children: {child_load_result.created} C, "
                                    f"{child_load_result.updated} U, "
                                    f"{child_load_result.skipped} S, "
                                    f"{child_load_result.errors} E."
                                )
                            )
                            if child_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Child Errors (Batch {batch_num}):"
                                    )
                                )
                                for k, err in enumerate(
                                    child_load_result.error_details
                                ):
                                    if k < 5:
                                        self.stdout.write(f"- {err}")
                                    else:
                                        self.stdout.write(
                                            f"... and "
                                            f"{len(child_load_result.error_details) - 5} "
                                            f"more."
                                        )
                                        break
                            if child_load_result.errors > 0:
                                # Mark sync as potentially failed
                                sync_successful = False

                        self.stdout.write(
                            f"{log_prefix} Finished processing all child batches."
                        )
                        logger.info(f"{log_prefix} Finished child processing.")
                    elif not successfully_loaded_parent_ids:
                        self.stdout.write(
                            f"{log_prefix} No parents were successfully loaded, "
                            f"skipping child processing."
                        )
                        logger.warning(
                            f"{log_prefix} Skipping child processing as no "
                            f"parents were loaded successfully."
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child data file found or "
                            f"no records to process."
                        )
                        logger.info(f"{log_prefix} Skipping child processing step.")

                except Exception as e:
                    sync_successful = False
                    self.stderr.write(
                        self.style.ERROR(f"{log_prefix} Full-Load mode failed: {e}")
                    )
                    logger.error(
                        f"{log_prefix} Full-Load mode failed: {e}",
                        exc_info=self.debug,
                    )
                    if self.debug:
                        traceback.print_exc()
                    # Don't re-raise here, allow summary reporting

                # --- Step 3 (Full-Load): Report Status ---
                end_time = timezone.now()
                duration = (end_time - command_start_time).total_seconds()

                self.stdout.write(self.style.NOTICE(
                    f"{log_prefix} === Step 3: Sync Summary ==="
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
                    f"{log_prefix} Orchestrator finished in {duration:.2f} seconds. "
                    f"Mode: {'Full-Load' if is_full_load else 'Batch-Fetch'}. "
                    f"Parents: C={parent_stats['created']}, U={parent_stats['updated']}, "
                    f"S={parent_stats['skipped']}, E={parent_stats['errors']}. "
                    f"Children: C={child_stats['created']}, U={child_stats['updated']}, "
                    f"S={child_stats['skipped']}, E={child_stats['errors']}."
                )
                self.stdout.write(
                    f"{log_prefix} Sales record sync command finished in "
                    f"{duration:.2f} seconds"
                )

                # Determine final status based on accumulated errors AND sync_successful flag
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
                        f"{log_prefix} Sync finished with errors. Check logs for details."
                    )
                    logger.error(error_msg)
                    # Raise CommandError to indicate failure to the system/caller
                    raise CommandError(error_msg)

        # =====================================================================
        # --- STANDARD BATCH-FETCH MODE ---
        # =====================================================================
        else:
            # --- Step 1 (Batch-Fetch): Fetch Initial Parent Records & Filter --- # noqa E501
            # NOTE: This reuses some variable names from the full-load section,
            # but they are scoped within this 'else' block.
            self.stdout.write(
                self.style.NOTICE(
                    f"{log_prefix} === Step 1 (Batch-Fetch): Fetching & "
                    f"Filtering Initial Parent Records "
                    f"({self.PARENT_LEGACY_KEY_FIELD}) ==="
                )
            )
            logger.info(
                f"{log_prefix} Starting Step 1 (Batch-Fetch): Fetch & Filter "
                f"Parents"
            )
            parent_record_ids = []
            filtered_parent_data_map = {}  # Map ID to record data
            try:
                parent_pipeline_for_id_fetch = parent_pipeline  # Reuse pipeline
                id_fetch_params = {**initial_query_params}
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
                            and f[0] == self.DATE_FILTER_FIELD
                        )
                    ]
                    if not id_fetch_params["filter_query"]:
                        del id_fetch_params["filter_query"]

                logger.info(
                    f"{log_prefix} Querying extractor for initial parent data "
                    f"(pre-filter) with params: {id_fetch_params}"
                )

                if options.get("clear_cache"):
                    self.stdout.write(
                        f"{log_prefix} Clearing parent extractor cache..."
                    )
                    parent_pipeline_for_id_fetch.extractor.clear_cache()

                # --- Use extract_batched for initial fetch ---
                # Use the *processing* batch size for the initial fetch here?
                # No, keep API page size large for efficiency, process_batch_size
                # is for DB load.
                # Use self.API_PAGE_SIZE or a reasonable default? Use constant.
                fetched_data_for_ids = []
                with parent_pipeline_for_id_fetch.extractor:
                    logger.info(
                        f"{log_prefix} Using extract_batched for initial "
                        f"parent data fetch with API page size "
                        f"{self.API_PAGE_SIZE}..."
                    )
                    id_batches = (
                        parent_pipeline_for_id_fetch.extractor.extract_batched(
                            query_params=id_fetch_params,
                            api_page_size=self.API_PAGE_SIZE,
                        )
                    )
                    for i, id_batch_data in enumerate(id_batches):
                        self.stdout.write(
                            f"{log_prefix} Fetched initial parent batch {i+1}...",
                            ending="",
                        )
                        fetched_data_for_ids.extend(id_batch_data)
                    self.stdout.write(
                        f"{log_prefix} Fetched initial parent batch {i+1}. Done."
                    )
                logger.info(
                    f"{log_prefix} Extractor returned "
                    f"{len(fetched_data_for_ids)} raw parent records."
                )
                self.stdout.write(
                    f"{log_prefix} Fetched {len(fetched_data_for_ids)} raw parent "
                    f"records for initial filtering."
                )


                # --- PRE-PROCESS DATE FIELD (Datum) --- # noqa E501
                logger.info(
                    f"{log_prefix} Pre-processing '{self.DATE_FILTER_FIELD}' field..."
                )
                parsing_errors = 0
                processed_count = 0
                for record in fetched_data_for_ids:
                    date_str = record.get(self.DATE_FILTER_FIELD)
                    if isinstance(date_str, str):
                        try:
                            parsed_date = datetime.datetime.strptime(
                                date_str, "%d!%m!%Y"
                            ).date()
                            record[self.DATE_FILTER_FIELD] = parsed_date
                            processed_count += 1
                        except (ValueError, TypeError):
                            parsing_errors += 1
                            record[self.DATE_FILTER_FIELD] = None
                            if parsing_errors < 10:
                                logger.warning(
                                    f"{log_prefix} Could not parse date string "
                                    f"'{date_str}'. Setting to None. Record ID: "
                                    f"{record.get(self.PARENT_LEGACY_KEY_FIELD, 'N/A')}"
                                )
                            elif parsing_errors == 10:
                                logger.warning(
                                    f"{log_prefix} Further date parsing errors "
                                    f"will be suppressed..."
                                )
                    elif date_str is not None:
                        pass

                logger.info(
                    f"{log_prefix} Finished pre-processing "
                    f"'{self.DATE_FILTER_FIELD}'. {processed_count} values parsed, "
                    f"{parsing_errors} errors (set to None)."
                )
                # --- END PRE-PROCESSING ---


                # --- APPLY CLIENT-SIDE DATE FILTER ---
                filtered_parent_data = _apply_date_filter(
                    fetched_data_for_ids,
                    date_filter_params,
                    self.DATE_FILTER_FIELD,  # Pass target field to helper
                )
                logger.info(
                    f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                    f"parent records meeting date criteria."
                )
                self.stdout.write(
                    f"{log_prefix} Filtered to {len(filtered_parent_data)} "
                    f"parent records post-date filter."
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
                    f"record IDs ({self.PARENT_LEGACY_KEY_FIELD}) after filtering."
                )
                logger.info(
                    f"{log_prefix} Step 1 (Batch-Fetch): Found "
                    f"{len(parent_record_ids)} unique parent IDs after filtering."
                )
                if self.debug and parent_record_ids:
                    self.stdout.write(
                        f"{log_prefix} Sample Parent IDs: "
                        f"{parent_record_ids[:10]}..."
                    )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        f"{log_prefix} Step 1 (Batch-Fetch) Failed: Could not "
                        f"fetch and filter parent records "
                        f"({self.PARENT_LEGACY_KEY_FIELD}): {e}"
                    )
                )
                logger.error(
                    f"{log_prefix} Step 1 (Batch-Fetch): Failed to fetch/filter "
                    f"parents: {e}",
                    exc_info=self.debug,
                )
                if self.debug:
                    traceback.print_exc()
                # If we can't get data, abort.
                raise CommandError(
                    f"Could not fetch/filter parent data, aborting sync. "
                    f"Error: {e}"
                )

            # --- Step 2 (Batch-Fetch): Process Belege and Belege_Pos records in batches ---
            self.stdout.write(
                self.style.NOTICE(
                    f"{log_prefix} === Step 2 (Batch-Fetch): Processing "
                    f"parent and child records in batches ==="
                )
            )
            logger.info(
                f"{log_prefix} Starting Step 2 (Batch-Fetch): Batch processing"
            )

            # Apply top limit if specified (to the filtered IDs)
            if "top" in options and options["top"]:
                top_limit = int(options["top"])
                if len(parent_record_ids) > top_limit:
                    parent_record_ids = parent_record_ids[:top_limit]
                    # Also trim the map to keep it consistent
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
                len(parent_record_ids) + process_batch_size - 1
            ) // process_batch_size
            self.stdout.write(
                f"{log_prefix} Will process {len(parent_record_ids)} parent "
                f"records in {total_parent_batches} batches of "
                f"~{process_batch_size} records each."
            )


            # Process records in batches
            for batch_index in range(total_parent_batches):
                start_idx = batch_index * process_batch_size
                end_idx = min(
                    start_idx + process_batch_size, len(parent_record_ids)
                )
                batch_parent_ids = parent_record_ids[start_idx:end_idx]

                self.stdout.write(
                    self.style.NOTICE(
                        f"{log_prefix} --- Processing Batch "
                        f"{batch_index + 1}/{total_parent_batches} "
                        f"({start_idx+1}-{end_idx} of "
                        f"{len(parent_record_ids)}) ---"
                    )
                )

                # ----- Step 2.1: Process parent records (Belege) for this batch ----- # noqa E501
                parent_source_data = []
                missing_ids_in_batch = []
                for parent_id in batch_parent_ids:
                    parent_record = filtered_parent_data_map.get(parent_id)
                    if parent_record:
                        parent_source_data.append(parent_record)
                    else:
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


                try:
                    transformed_parent_data = []
                    failed_parent_legacy_ids = set()
                    # Default result
                    parent_load_result = LoadResult(
                        created=0, updated=0, skipped=0, errors=0, error_details=[]
                    )

                    if parent_source_data:
                        transformed_parent_data = (
                            parent_pipeline.transformer.transform(parent_source_data)
                        )
                        self.stdout.write(
                            f"{log_prefix} Transformed "
                            f"{len(transformed_parent_data)} parent records."
                        )

                        parent_load_result = parent_pipeline.loader.load(
                            transformed_parent_data,
                            update_existing=(
                                options.get("force_update") or options.get("full")
                            ),
                        )

                        parent_stats["created"] += parent_load_result.created
                        parent_stats["updated"] += parent_load_result.updated
                        parent_stats["skipped"] += parent_load_result.skipped
                        parent_stats["errors"] += parent_load_result.errors

                        unique_field = parent_pipeline.loader.config.get(
                            "unique_field", "legacy_id"
                        )
                        if parent_load_result.error_details:
                            for error_detail in parent_load_result.error_details:
                                record_data = error_detail.get("record")
                                if record_data and unique_field in record_data:
                                    failed_parent_legacy_ids.add(
                                        str(record_data[unique_field])
                                    )
                                else:
                                    logger.warning(
                                        f"{log_prefix} Could not extract unique ID "
                                        f"({unique_field}) from parent load error "
                                        f"detail in batch {batch_index + 1}: "
                                        f"{error_detail}"
                                    )

                        # Log parent results - combined with child later
                        self.stdout.write(
                            f"{log_prefix} Parent load (Batch {batch_index + 1}): "
                            f"{parent_load_result.created} C, "
                            f"{parent_load_result.updated} U, "
                            f"{parent_load_result.skipped} S, "
                            f"{parent_load_result.errors} E."
                        )
                        if parent_load_result.error_details:
                            # Display errors compactly
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Parent Errors (Batch {batch_index + 1}): "
                                    f"{len(parent_load_result.error_details)}"
                                )
                            )
                            # Log first few details
                            for i, err in enumerate(parent_load_result.error_details):
                                if i < 2:
                                    logger.warning(
                                        f"{log_prefix} Parent Error Detail: {err}"
                                    )
                                elif i == 2:
                                    logger.warning(
                                        f"{log_prefix} ... more parent errors logged."
                                    )
                                    break

                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent source data for batch "
                            f"{batch_index + 1}."
                        )


                    # ----- Step 2.2: Process child records (Belege_Pos) for this batch ----- # noqa E501
                    intended_parent_ids = [
                        str(record.get(unique_field))
                        for record in transformed_parent_data
                        if record.get(unique_field) is not None
                    ]
                    successful_parent_ids = list(
                        set(intended_parent_ids) - failed_parent_legacy_ids
                    )

                    # Default result
                    child_load_result = LoadResult(
                        created=0, updated=0, skipped=0, errors=0, error_details=[]
                    )

                    if successful_parent_ids:
                        self.stdout.write(
                            f"{log_prefix} Fetching child records for "
                            f"{len(successful_parent_ids)} successful parent IDs..."
                        )
                        child_batch_filters = {
                            "parent_record_ids": successful_parent_ids,
                            "parent_field": self.CHILD_PARENT_LINK_FIELD,
                        }
                        if initial_query_params:
                            for key, value in initial_query_params.items():
                                if (
                                    key not in ["$top", "filter_query"]
                                    and key not in child_batch_filters
                                ):
                                    child_batch_filters[key] = value

                        child_source_data = []
                        with child_pipeline.extractor:
                            try:
                                child_batches = (
                                    child_pipeline.extractor.extract_batched(
                                        query_params=child_batch_filters,
                                        # Use large page size for fetch
                                        api_page_size=self.API_PAGE_SIZE,
                                    )
                                )
                                for batch_data in child_batches:
                                    child_source_data.extend(batch_data)
                            except AttributeError:
                                logger.debug(
                                    "Child extractor missing extract_batched, "
                                    "using extract()."
                                )
                                child_source_data = (
                                    child_pipeline.extractor.extract(
                                        query_params=child_batch_filters
                                    )
                                )

                        self.stdout.write(
                            f"{log_prefix} Extracted {len(child_source_data)} "
                            f"child records."
                        )

                        # --- PRE-PROCESS CHILD DATE FIELD (Datum) --- # noqa E501
                        child_parsing_errors = 0
                        child_processed_count = 0
                        for record in child_source_data:
                            date_str = record.get(self.DATE_FILTER_FIELD)
                            if isinstance(date_str, str):
                                try:
                                    parsed_date = datetime.datetime.strptime(
                                        date_str, "%d!%m!%Y"
                                    ).date()
                                    record[
                                        self.DATE_FILTER_FIELD
                                    ] = parsed_date
                                    child_processed_count += 1
                                except (ValueError, TypeError):
                                    child_parsing_errors += 1
                                    record[self.DATE_FILTER_FIELD] = None
                                    # Less verbose logging here
                                    if child_parsing_errors < 5:
                                        logger.warning(
                                            f"{log_prefix} Could not parse child "
                                            f"date '{date_str}'. Setting None."
                                        )
                                    elif child_parsing_errors == 5:
                                        logger.warning(
                                            f"{log_prefix} Further child date "
                                            f"errors suppressed."
                                        )
                            elif date_str is not None:
                                pass
                        if child_processed_count > 0 or child_parsing_errors > 0:
                            logger.info(
                                f"{log_prefix} Child Date PreProc: "
                                f"{child_processed_count} parsed, "
                                f"{child_parsing_errors} errors."
                            )
                        # --- END CHILD PRE-PROCESSING ---

                        if child_source_data:
                            # No date filtering needed here in batch mode
                            # (already applied to parents)
                            filtered_child_data = child_source_data

                            transformed_child_data = (
                                child_pipeline.transformer.transform(
                                    filtered_child_data
                                )
                            )
                            self.stdout.write(
                                f"{log_prefix} Transformed "
                                f"{len(transformed_child_data)} child records."
                            )

                            child_load_result = child_pipeline.loader.load(
                                transformed_child_data,
                                update_existing=(
                                    options.get("force_update")
                                    or options.get("full")
                                ),
                            )

                            child_stats["created"] += child_load_result.created
                            child_stats["updated"] += child_load_result.updated
                            child_stats["skipped"] += child_load_result.skipped
                            child_stats["errors"] += child_load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Batch {batch_index + 1} finished. "
                                    f"Parents: {parent_load_result.created} C, "
                                    f"{parent_load_result.updated} U, "
                                    f"{parent_load_result.skipped} S, "
                                    f"{parent_load_result.errors} E. | "
                                    f"Children: {child_load_result.created} C, "
                                    f"{child_load_result.updated} U, "
                                    f"{child_load_result.skipped} S, "
                                    f"{child_load_result.errors} E."
                                )
                            )
                            if child_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Child Errors (Batch {batch_index + 1}): "
                                        f"{len(child_load_result.error_details)}"
                                    )
                                )
                                for i, err in enumerate(child_load_result.error_details):
                                    if i < 2:
                                        logger.warning(
                                            f"{log_prefix} Child Error Detail: {err}"
                                        )
                                    elif i == 2:
                                        logger.warning(
                                            f"{log_prefix} ... more child "
                                            f"errors logged."
                                        )
                                        break
                        else:
                            self.stdout.write(
                                f"{log_prefix} No child records "
                                f"extracted/remaining for batch {batch_index + 1}."
                            )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No successfully loaded parent IDs in "
                            f"batch {batch_index + 1}, skipping child processing."
                        )

                except Exception as e:
                    # Handle errors for this batch
                    sync_successful = False  # Mark overall sync as failed
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

        logger.info(
            f"{log_prefix} Orchestrator finished in {duration:.2f} seconds. "
            f"Mode: {'Full-Load' if is_full_load else 'Batch-Fetch'}. "
            f"Parents: C={parent_stats['created']}, U={parent_stats['updated']}, "
            f"S={parent_stats['skipped']}, E={parent_stats['errors']}. "
            f"Children: C={child_stats['created']}, U={child_stats['updated']}, "
            f"S={child_stats['skipped']}, E={child_stats['errors']}."
        )
        self.stdout.write(
            f"{log_prefix} Sales record sync command finished in "
            f"{duration:.2f} seconds"
        )

        # Determine final status based on accumulated errors AND sync_successful flag
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
                f"{log_prefix} Sync finished with errors. Check logs for details."
            )
            logger.error(error_msg)
            # Raise CommandError to indicate failure to the system/caller
            raise CommandError(error_msg)


