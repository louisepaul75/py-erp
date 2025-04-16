"""Management command to synchronize sales records from legacy ERP."""

import traceback
import datetime  # Use the datetime module directly
import tempfile
from pathlib import Path
import pandas as pd # Import pandas

import pyarrow as pa
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
                        "Could not convert object with date attributes to date for "
                        "field '%s'. Value: %s. Skipping record: %s",
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
                    and f[0] == self.DEFAULT_TIMESTAMP_FIELD  # Check default field
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
            f"{log_prefix} Initial query parameters built: {initial_query_params}"
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
                        f"{log_prefix} Starting Step 1 (Full-Load): Fetch & Filter "
                        f"Parents"
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
                        f"(pre-filter) with params: {id_fetch_params}, API page "
                        f"size: {self.API_PAGE_SIZE}"
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
                        f"{log_prefix} Extractor returned {len(all_parent_data)} raw "
                        f"parent records."
                    )
                    self.stdout.write(
                        f"{log_prefix} Fetched {len(all_parent_data)} raw parent records."
                    )

                    # --- Refactor Parent Pre-processing using Pandas --- #
                    logger.info(
                        f"{log_prefix} Pre-processing '{self.DATE_FILTER_FIELD}' field "
                        f"for {len(all_parent_data)} parents using pandas..."
                    )

                    if all_parent_data:
                        try:
                            parent_df = pd.DataFrame(all_parent_data)
                            original_count = len(parent_df)

                            # Attempt conversion - coerce errors to NaT
                            # Handle potential initial non-string types first
                            parent_df[self.DATE_FILTER_FIELD] = parent_df[self.DATE_FILTER_FIELD].astype(str)
                            # Now parse strings
                            parent_df[self.DATE_FILTER_FIELD] = pd.to_datetime(
                                parent_df[self.DATE_FILTER_FIELD],
                                format="%d!%m!%Y",
                                errors='coerce'
                            )

                            # Check for NaT values (conversion errors)
                            conversion_errors = parent_df[self.DATE_FILTER_FIELD].isna()
                            dropped_count = conversion_errors.sum()

                            if dropped_count > 0:
                                logger.warning(
                                    f"{log_prefix} Dropping {dropped_count} parent records due "
                                    f"to '{self.DATE_FILTER_FIELD}' conversion errors."
                                )
                                # Keep only valid dates
                                parent_df = parent_df.dropna(subset=[self.DATE_FILTER_FIELD])

                            # Convert to date objects (if needed, Parquet might handle datetime)
                            # Let's keep as date objects for consistency with pa.date32()
                            parent_df[self.DATE_FILTER_FIELD] = parent_df[self.DATE_FILTER_FIELD].dt.date

                            # Convert back to list of dicts
                            all_parent_data = parent_df.to_dict('records')
                            logger.info(
                                f"{log_prefix} Finished parent pre-processing. "
                                f"Kept: {len(all_parent_data)}, Dropped: {dropped_count}."
                            )

                        except Exception as e:
                            logger.error(
                                f"{log_prefix} Error during parent data pre-processing with pandas: {e}",
                                exc_info=self.debug
                            )
                            # Depending on severity, maybe raise CommandError or proceed with original data?
                            # For now, raise error as data integrity is compromised.
                            raise CommandError(f"Pandas pre-processing failed for parents: {e}") from e
                    else:
                        logger.info(f"{log_prefix} No parent data to pre-process.")
                    # --- End Pandas Pre-processing ---

                    # Apply Client-Side Date Filter (operates on list of dicts with date objects)
                    filtered_parent_data = _apply_date_filter(
                        all_parent_data, date_filter_params, self.DATE_FILTER_FIELD
                    )
                    logger.info(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} parent "
                        f"records meeting date criteria (post-date-validation)."
                    )
                    self.stdout.write(
                        f"{log_prefix} Filtered to {len(filtered_parent_data)} parent "
                        f"records post-date validation and filter."
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
                            f"{log_prefix} Saving {len(filtered_parent_data)} parents "
                            f"to {parents_file}..."
                        )
                        # Convert list of dicts to Arrow Table
                        try:
                            # --- DETAILED TYPE LOGGING (Parents) --- >
                            if self.debug and filtered_parent_data:
                                logger.debug(f"{log_prefix} DETAILED TYPE CHECK (Parents Sample):")
                                sample_size = min(5, len(filtered_parent_data))
                                keys = filtered_parent_data[0].keys() if filtered_parent_data else []
                                logger.debug(f"  Keys: {list(keys)}")
                                for i in range(sample_size):
                                    record = filtered_parent_data[i]
                                    record_id = record.get(self.PARENT_LEGACY_KEY_FIELD, f'Index_{i}')
                                    types_in_rec = {k: type(v).__name__ for k, v in record.items()}
                                    logger.debug(f"  - Record ID {record_id}: {types_in_rec}")
                            # --- END DETAILED TYPE LOGGING ---

                            # Infer schema, ensure Datum is pa.date32()
                            if not filtered_parent_data:
                                logger.warning(f"{log_prefix} No parent data remains after filtering/dropping. Cannot infer schema.")
                                final_schema = None
                            else:
                                # Use first record to infer, then adjust date field
                                inferred_schema = pa.Table.from_pylist([filtered_parent_data[0]]).schema
                                schema_fields = {name: field.type for name, field in zip(inferred_schema.names, inferred_schema)}
                                if self.DATE_FILTER_FIELD in schema_fields:
                                    logger.debug(f"{log_prefix} Forcing '{self.DATE_FILTER_FIELD}' to pa.date32() in parent schema.")
                                    schema_fields[self.DATE_FILTER_FIELD] = pa.date32()
                                final_schema = pa.schema(list(schema_fields.items()))
                                logger.debug(f"{log_prefix} Using final schema for parents: {final_schema}")

                            # Only proceed if there's data and a schema
                            if filtered_parent_data and final_schema:
                                parent_table = pa.Table.from_pylist(
                                    filtered_parent_data,
                                    schema=final_schema  # Use explicit schema with date32
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
                                    f"{log_prefix} Saved {parent_record_count} parents. Found "
                                    f"{len(parent_ids_to_fetch_children_for)} unique IDs."
                                )
                                logger.info(
                                    f"{log_prefix} Saved {parent_record_count} parents to "
                                    f"Parquet. Found {len(parent_ids_to_fetch_children_for)} "
                                    f"unique IDs."
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
                            f"{log_prefix} No parent records remain after filtering. "
                            f"Skipping child fetch and processing."
                        )
                        parent_ids_to_fetch_children_for = set()  # Ensure empty

                    filtered_parent_data = None  # Free memory


                    # --- Step 1 (Full-Load): Fetch All Child Records ---
                    if parent_ids_to_fetch_children_for:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"{log_prefix} === Step 1 (Full-Load): Fetching ALL "
                                f"Child Records for {len(parent_ids_to_fetch_children_for)} "
                                f"Parents ==="
                            )
                        )
                        logger.info(
                            f"{log_prefix} Starting Step 1 (Full-Load): Fetch Children"
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
                            f"{log_prefix} Querying extractor for ALL child data with "
                            f"{len(parent_ids_to_fetch_children_for)} parent IDs. API "
                            f"page size: {self.API_PAGE_SIZE}"
                        )
                        # No need to clear child cache unless specifically
                        # requested (unlikely)

                        all_child_data = []
                        with child_pipeline.extractor:
                            batches = child_pipeline.extractor.extract_batched(
                                query_params=child_fetch_params,
                                # Use large page size for fetch
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
                            f"{log_prefix} Extractor returned {len(all_child_data)} raw "
                            f"child records."
                        )
                        self.stdout.write(
                            f"{log_prefix} Fetched {len(all_child_data)} raw child records."
                        )

                        # --- Refactor Child Pre-processing using Pandas --- #
                        logger.info(
                            f"{log_prefix} Pre-processing '{self.DATE_FILTER_FIELD}' field "
                            f"for {len(all_child_data)} children using pandas..."
                        )

                        if all_child_data:
                            try:
                                child_df = pd.DataFrame(all_child_data)
                                original_count = len(child_df)
                                child_unique_field = child_pipeline.loader.config.get(
                                    "unique_field", "legacy_id"
                                )

                                # Attempt conversion - coerce errors to NaT
                                # Handle potential initial non-string types first
                                child_df[self.DATE_FILTER_FIELD] = child_df[self.DATE_FILTER_FIELD].astype(str)
                                # Now parse strings
                                child_df[self.DATE_FILTER_FIELD] = pd.to_datetime(
                                    child_df[self.DATE_FILTER_FIELD],
                                    format="%d!%m!%Y",
                                    errors='coerce'
                                )

                                # Check for NaT values (conversion errors)
                                conversion_errors = child_df[self.DATE_FILTER_FIELD].isna()
                                dropped_count = conversion_errors.sum()

                                if dropped_count > 0:
                                    logger.warning(
                                        f"{log_prefix} Dropping {dropped_count} child records due "
                                        f"to '{self.DATE_FILTER_FIELD}' conversion errors."
                                    )
                                    # Keep only valid dates
                                    child_df = child_df.dropna(subset=[self.DATE_FILTER_FIELD])

                                # Convert to date objects
                                child_df[self.DATE_FILTER_FIELD] = child_df[self.DATE_FILTER_FIELD].dt.date

                                # Convert back to list of dicts
                                all_child_data = child_df.to_dict('records')
                                logger.info(
                                    f"{log_prefix} Finished child pre-processing. "
                                    f"Kept: {len(all_child_data)}, Dropped: {dropped_count}."
                                )

                            except Exception as e:
                                logger.error(
                                    f"{log_prefix} Error during child data pre-processing with pandas: {e}",
                                    exc_info=self.debug
                                )
                                raise CommandError(f"Pandas pre-processing failed for children: {e}") from e
                        else:
                            logger.info(f"{log_prefix} No child data to pre-process.")
                        # --- End Pandas Child Pre-processing ---

                        # Save Children to Parquet
                        if all_child_data:
                            self.stdout.write(
                                f"{log_prefix} Saving {len(all_child_data)} children "
                                f"to {children_file}..."
                            )
                            try:
                                # --- DETAILED TYPE LOGGING (Children) --- >
                                if self.debug and all_child_data:
                                    logger.debug(f"{log_prefix} DETAILED TYPE CHECK (Children Sample):")
                                    sample_size = min(5, len(all_child_data))
                                    keys = all_child_data[0].keys() if all_child_data else []
                                    logger.debug(f"  Keys: {list(keys)}")
                                    child_unique_field = child_pipeline.loader.config.get(
                                        "unique_field", "legacy_id"
                                    )
                                    for i in range(sample_size):
                                        record = all_child_data[i]
                                        record_key = record.get(child_unique_field, f'Index_{i}')
                                        types_in_rec = {k: type(v).__name__ for k, v in record.items()}
                                        logger.debug(f"  - Record Key {record_key}: {types_in_rec}")
                                # --- END DETAILED TYPE LOGGING ---

                                # Infer schema, ensure Datum is pa.date32()
                                if not all_child_data:
                                    logger.warning(f"{log_prefix} No child data remains after filtering/dropping. Cannot infer schema.")
                                    final_schema = None
                                else:
                                    # Use first record to infer, then adjust date field
                                    inferred_schema = pa.Table.from_pylist([all_child_data[0]]).schema
                                    schema_fields = {name: field.type for name, field in zip(inferred_schema.names, inferred_schema)}
                                    if self.DATE_FILTER_FIELD in schema_fields:
                                        logger.debug(f"{log_prefix} Forcing '{self.DATE_FILTER_FIELD}' to pa.date32() in child schema.")
                                        schema_fields[self.DATE_FILTER_FIELD] = pa.date32()
                                    final_schema = pa.schema(list(schema_fields.items()))
                                    logger.debug(f"{log_prefix} Using final schema for children: {final_schema}")

                                # Only proceed if there's data and a schema
                                if all_child_data and final_schema:
                                    child_table = pa.Table.from_pylist(
                                        all_child_data,
                                        schema=final_schema  # Use explicit schema with date32
                                    )
                                    pq.write_table(child_table, children_file)
                                    child_record_count = len(all_child_data)
                                    self.stdout.write(
                                        f"{log_prefix} Saved {child_record_count} children."
                                    )
                                    logger.info(
                                        f"{log_prefix} Saved {child_record_count} children "
                                        f"to Parquet."
                                    )
                            except Exception as e:
                                logger.error(
                                    f"{log_prefix} Failed to write children Parquet: {e}",
                                    exc_info=self.debug,
                                )
                                raise CommandError(
                                    f"Failed to write temporary child data: {e}"
                                ) from e
                            finally:
                                child_table = None  # Free memory
                        else:
                            self.stdout.write(
                                f"{log_prefix} No child records found for the fetched "
                                f"parents."
                            )
                            logger.info(f"{log_prefix} No child records found.")

                        all_child_data = None  # Free memory
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent IDs found, skipping child fetch."
                        )

                    # --- Step 2 (Full-Load): Process Parents from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2 (Full-Load): Processing "
                            f"{parent_record_count} Parents from {parents_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2 (Full-Load): Processing Parents"
                    )

                    if parents_file.exists() and parent_record_count > 0:
                        parent_pf = pq.ParquetFile(parents_file)
                        total_parent_batches = (
                            parent_record_count + process_batch_size - 1
                        ) // process_batch_size
                        self.stdout.write(
                            f"{log_prefix} Processing in {total_parent_batches} batches "
                            f"of size {process_batch_size}."
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
                                    f"{log_prefix} Parent Batch {batch_num} is empty, "
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
                                    options.get("force_update") or options.get("full")
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
                                    f"({len(successful_ids_in_batch)} successful loads)"
                                )
                            )
                            if parent_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Parent Errors (Batch {batch_num}):"
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
                            f"{log_prefix} Finished processing all parent batches. "
                            f"Total successful parent loads: "
                            f"{len(successfully_loaded_parent_ids)}"
                        )
                        logger.info(
                            f"{log_prefix} Finished parent processing. "
                            f"{len(successfully_loaded_parent_ids)} successfully loaded."
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent data file found or no records "
                            f"to process."
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
                        f"{log_prefix} Starting Step 2 (Full-Load): Processing Children"
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
                            f"{log_prefix} Processing in {total_child_batches} batches "
                            f"of size {process_batch_size}."
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
                                    f"{log_prefix} Child Batch {batch_num} is empty, "
                                    f"skipping."
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
                                    f"{log_prefix} Filtered out {skipped_count} children "
                                    f"linked to unloaded parents."
                                )
                                logger.info(
                                    f"{log_prefix} Batch {batch_num}: Filtered out "
                                    f"{skipped_count} children."
                                )

                            if not filtered_child_data:
                                self.stdout.write(
                                    f"{log_prefix} No children remaining in Batch {batch_num} "
                                    f"after filtering, skipping."
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
                                    options.get("force_update") or options.get("full")
                                ),
                            )

                            child_stats["created"] += child_load_result.created
                            child_stats["updated"] += child_load_result.updated
                            child_stats["skipped"] += child_load_result.skipped
                            child_stats["errors"] += child_load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Batch {batch_num} finished. Parents: "
                                    f"{parent_load_result.created} C, "
                                    f"{parent_load_result.updated} U, "
                                    f"{parent_load_result.skipped} S, "
                                    f"{parent_load_result.errors} E. | Children: "
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
                                            f"{log_prefix} ... more child errors logged."
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
                            f"{log_prefix} No parents were successfully loaded, skipping "
                            f"child processing."
                        )
                        logger.warning(
                            f"{log_prefix} Skipping child processing as no parents "
                            f"were loaded successfully."
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child data file found or no records to "
                            f"process."
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

                self.stdout.write(
                    self.style.NOTICE(f"{log_prefix} === Step 3: Sync Summary ===")
                )

                # Report parent stats
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{log_prefix} Parent ({self.PARENT_ENTITY_TYPE}) summary: "
                        f"{parent_stats['created']} created, "
                        f"{parent_stats['updated']} updated, "
                        f"{parent_stats['skipped']} skipped, "
                        f"{parent_stats['errors']} errors."
                    )
                )

                # Report child stats
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{log_prefix} Child ({self.CHILD_ENTITY_TYPE}) summary: "
                        f"{child_stats['created']} created, "
                        f"{child_stats['updated']} updated, "
                        f"{child_stats['skipped']} skipped, "
                        f"{child_stats['errors']} errors."
                    )
                )

                logger.info(
                    f"{log_prefix} Orchestrator finished in {duration:.2f} seconds. "
                    f"Mode: {'Full-Load' if is_full_load else 'Batch-Fetch'}. "
                    f"Parents: C={parent_stats['created']}, U={parent_stats['updated']}, "
                    f"S={parent_stats['skipped']}, E={parent_stats['errors']}. "
                    f"Children: C={child_stats['created']}, U={child_stats['updated']}, "
                    f"S={child_stats['skipped']}, E={child_stats['errors']}."
                )
                self.stdout.write(
                    f"{log_prefix} Sales record sync command finished in {duration:.2f} "
                    f"seconds"
                )

                # Determine final status based on sync_successful flag AND errors
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
                        f"{log_prefix} Sync finished with errors. Check logs for "
                        f"details."
                    )
                    logger.error(error_msg)
                    # Raise CommandError to indicate failure
                    raise CommandError(error_msg)


