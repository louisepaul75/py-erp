"""Management command to synchronize sales records from legacy ERP."""

import traceback
import datetime  # Use the datetime module directly
import tempfile
from pathlib import Path
import pandas as pd  # Import pandas

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
                        parent_table = None  # Ensure var exists for finally block

                        try: # Schema determination and Parquet writing
                            # --- Robust Schema Definition based on Data Scan ---
                            logger.debug(f"{log_prefix} Determining schema by scanning parent data...")
                            field_types = {}
                            all_keys = set()
                            if filtered_parent_data:
                                for record in filtered_parent_data: # Scan all records
                                    all_keys.update(record.keys())
                            else:
                                raise ValueError("Cannot determine schema from empty data.")
                            
                            # Scan data to determine types
                            for record in filtered_parent_data: # Scan all for robustness here
                                for key in all_keys:
                                    value = record.get(key)
                                    current_pa_type = field_types.get(key)

                                    if value is None:
                                        continue # Cannot infer type from None alone

                                    detected_pa_type = None
                                    if isinstance(value, datetime.datetime):
                                        detected_pa_type = pa.timestamp('us')
                                    elif isinstance(value, datetime.date):
                                        detected_pa_type = pa.date32()
                                    elif isinstance(value, bool):
                                        detected_pa_type = pa.bool_()
                                    elif isinstance(value, int):
                                        detected_pa_type = pa.int64()
                                    elif isinstance(value, float):
                                        detected_pa_type = pa.float64()
                                    elif isinstance(value, str):
                                        detected_pa_type = pa.string()
                                    elif isinstance(value, dict):
                                        try:
                                            if current_pa_type is None or not pa.types.is_struct(current_pa_type):
                                                struct_table = pa.Table.from_pylist([value])
                                                detected_pa_type = struct_table.schema.field(0).type
                                        except Exception as struct_err:
                                            logger.warning(f"{log_prefix} Could not infer struct type for key '{key}', defaulting to string. Error: {struct_err}")
                                            detected_pa_type = pa.string()
                                    
                                    if detected_pa_type:
                                        if current_pa_type is None:
                                            field_types[key] = detected_pa_type
                                        elif current_pa_type != detected_pa_type:
                                            # Handle type conflicts (promote to more general type)
                                            if pa.types.is_integer(current_pa_type) and pa.types.is_floating(detected_pa_type):
                                                field_types[key] = pa.float64()
                                            elif pa.types.is_floating(current_pa_type) and pa.types.is_integer(detected_pa_type):
                                                pass # Keep float64
                                            elif pa.types.is_primitive(current_pa_type) and pa.types.is_string(detected_pa_type):
                                                 field_types[key] = pa.string() # Promote primitive to string
                                            elif pa.types.is_string(current_pa_type) and not pa.types.is_string(detected_pa_type):
                                                pass # Keep string if already string
                                            elif current_pa_type == pa.date32() and detected_pa_type == pa.timestamp('us'):
                                                 field_types[key] = pa.timestamp('us') # Promote date to timestamp
                                            elif current_pa_type == pa.timestamp('us') and detected_pa_type == pa.date32():
                                                 pass # Keep timestamp
                                            # Add other conflict resolutions? Defaulting to string might be safest for unhandled mixes
                                            elif current_pa_type != detected_pa_type and not pa.types.is_struct(current_pa_type): # Avoid struct conflicts for now
                                                logger.warning(f"{log_prefix} Field '{key}' has unhandled mixed types: {current_pa_type} and {detected_pa_type}. Promoting to string.")
                                                field_types[key] = pa.string()

                            # Build final schema definition
                            schema_definition = []
                            final_field_types = {} # Store for potential later use in cleaning
                            for key in sorted(list(all_keys)): # Sort for consistent schema order
                                pa_type = field_types.get(key)
                                if pa_type is None:
                                    logger.warning(f"{log_prefix} Field '{key}' was all None or empty in scan, defaulting to null type.")
                                    pa_type = pa.null()
                                
                                # Manual override for DATE_FILTER_FIELD
                                if key == self.DATE_FILTER_FIELD and pa_type != pa.date32():
                                    logger.warning(f"{log_prefix} Overriding schema type for '{key}' from {pa_type} to date32.")
                                    pa_type = pa.date32()
                                
                                schema_definition.append(pa.field(key, pa_type))
                                final_field_types[key] = pa_type

                            final_schema = pa.schema(schema_definition)
                            logger.info(f"{log_prefix} Determined final schema: {final_schema}")
                            # --- End Schema Definition ---

                            # --- Data Cleaning with Pandas (using previous logic for now) ---
                            self.stdout.write(
                                f"{log_prefix} Cleaning parent data types before saving..."
                            )
                            parent_df = pd.DataFrame(filtered_parent_data)

                            # Identify integer cols based on the *new* final_schema
                            integer_fields_final = {
                                field.name for field in final_schema
                                if pa.types.is_integer(field.type)
                            }
                            logger.debug(f"{log_prefix} Integer fields for cleaning: {integer_fields_final}")

                            # 1. Coerce top-level integer columns
                            cleaned_count = 0
                            for col in integer_fields_final: # Use updated list
                                if col in parent_df.columns:
                                    if (
                                        parent_df[col].dtype == object or
                                        pd.api.types.is_string_dtype(parent_df[col].dtype)
                                    ):
                                        logger.debug(
                                            f"{log_prefix} Coercing int column '{col}'..."
                                        )
                                        original_nulls = parent_df[col].isna().sum()
                                        parent_df[col] = pd.to_numeric(parent_df[col], errors='coerce')
                                        if not parent_df[col].isna().all():
                                            try:
                                                parent_df[col] = parent_df[col].astype(pd.Int64Dtype())
                                                coerced_nulls = parent_df[col].isna().sum()
                                                if coerced_nulls > original_nulls:
                                                    logger.info(f"Coerced {coerced_nulls-original_nulls} val->NA in '{col}'")
                                                cleaned_count += 1
                                            except Exception as astype_err:
                                                logger.warning(f"Could not convert '{col}' to Int64: {astype_err}")

                            if cleaned_count > 0:
                                logger.info(f"Applied coercion to {cleaned_count} int columns.")
                            else:
                                logger.debug(f"No top-level int coercion needed.")

                            # 2. Clean nested Waehrungsinfo.Kurs
                            if WAEHRUNGSINFO_FIELD in parent_df.columns:
                                logger.debug(f"Cleaning nested '{WAEHRUNGSINFO_FIELD}.{KURS_FIELD}'")
                                def clean_kurs(info_dict):
                                    # (Using the existing clean_kurs function logic)
                                    if not isinstance(info_dict, dict): return info_dict
                                    new_info_dict = info_dict.copy()
                                    kurs_val = new_info_dict.get(KURS_FIELD)
                                    kurs_changed = False
                                    if kurs_val is None or isinstance(kurs_val, int): pass
                                    elif isinstance(kurs_val, float):
                                        if kurs_val.is_integer(): new_info_dict[KURS_FIELD] = int(kurs_val); kurs_changed = True
                                        else: new_info_dict[KURS_FIELD] = None; kurs_changed = True
                                    elif isinstance(kurs_val, str):
                                        try:
                                            cleaned_val = int(kurs_val) if kurs_val.strip() else None
                                            if kurs_val != cleaned_val: new_info_dict[KURS_FIELD] = cleaned_val; kurs_changed = True
                                        except (ValueError, TypeError): new_info_dict[KURS_FIELD] = None; kurs_changed = True
                                    else: new_info_dict[KURS_FIELD] = None; kurs_changed = True
                                    return new_info_dict if kurs_changed else info_dict
                                parent_df[WAEHRUNGSINFO_FIELD] = parent_df[WAEHRUNGSINFO_FIELD].apply(clean_kurs)
                                logger.info(f"Finished cleaning nested '{WAEHRUNGSINFO_FIELD}.{KURS_FIELD}'")

                            # 3. Convert DataFrame back to list of dicts
                            cleaned_parent_data = parent_df.where(pd.notna(parent_df), None).to_dict('records')
                            parent_df = None  # Free memory
                            # --- End Data Cleaning ---

                            # --- Create Arrow Table with Explicit Schema ---
                            logger.debug(f"{log_prefix} Creating pyarrow Table (inferring schema)...")
                            parent_table = pa.Table.from_pylist(
                                cleaned_parent_data, # Let PyArrow infer schema now
                                safe=False # DIAGNOSTIC: Disable safety checks
                            )
                            inferred_schema = parent_table.schema
                            logger.info(f"{log_prefix} Inferred schema (safe=False): {inferred_schema}") # Log info

                            # --- Cast specific columns AFTER inference ---
                            # --- Write Arrow Table ---
                            logger.debug(
                                f"{log_prefix} Writing final parent table to {parents_file}..."
                            )
                            pq.write_table(parent_table, parents_file)
                            parent_record_count = len(cleaned_parent_data)
                            # --- End Write Table ---

                            # Extract IDs after saving
                            for record in cleaned_parent_data:
                                record_id = record.get(
                                    self.PARENT_LEGACY_KEY_FIELD
                                )
                                if record_id is not None:
                                    parent_ids_to_fetch_children_for.add(
                                        str(record_id)
                                    )
                            self.stdout.write(
                                f"{log_prefix} Saved {parent_record_count} parents. "
                                f"Found {len(parent_ids_to_fetch_children_for)} unique IDs."
                            )
                            logger.info(
                                f"{log_prefix} Saved {parent_record_count} parents to "
                                f"Parquet. Found "
                                f"{len(parent_ids_to_fetch_children_for)} unique IDs."
                            )
                            # --- End Table/ID code ---

                        except Exception as e:  # Catch Parquet processing errors
                            logger.error(
                                f"{log_prefix} Failed during parent Parquet processing "
                                f"(cleaning, inference, casting, or writing): {e}", # Updated message
                                exc_info=self.debug,
                            )
                            if self.debug:
                                traceback.print_exc()
                            raise CommandError(
                                f"Failed during parent Parquet processing: {e}"
                            ) from e
                        finally:
                            parent_table = None  # Free memory
                            # Ensure cleaned data is also cleared if loop breaks
                            cleaned_parent_data = None
                    else:
                        self.stdout.write(
                            f"{log_prefix} No parent records remain after filtering. "
                            f"Skipping child fetch and processing."
                        )
                        parent_ids_to_fetch_children_for = set()

                    filtered_parent_data = None  # Free memory

                    # --- Step 1c: Fetch All Child Records ---
                    if parent_ids_to_fetch_children_for:
                        self.stdout.write(
                            self.style.NOTICE(
                                f"{log_prefix} === Step 1c: Fetching ALL Child "
                                f"Records for {len(parent_ids_to_fetch_children_for)} "
                                f"Parents ==="
                            )
                        )
                        logger.info(
                            f"{log_prefix} Starting Step 1c: Fetch Children"
                        )

                        child_fetch_params = {
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
                            f"{len(parent_ids_to_fetch_children_for)} parent IDs. "
                            f"API page size: {self.API_PAGE_SIZE}"
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
                                    f"\r{log_prefix} Fetched child batch {batch_num}...",
                                    ending="",
                                )
                                all_child_data.extend(batch_data)
                            self.stdout.write( # Overwrite last status
                                f"\r{log_prefix} Fetched {len(all_child_data)} total "
                                f"raw child records. Done."
                            )
                            # Add a newline after finishing the \r updates
                            self.stdout.write("")

                        logger.info(
                            f"{log_prefix} Extractor returned {len(all_child_data)} "
                            f"raw child records."
                        )

                        # --- Assume extractor provides datetime.date objects ---
                        logger.info(
                            f"{log_prefix} Skipping child date pre-processing."
                        )

                        # Save Children to Parquet
                        if all_child_data:
                            self.stdout.write(
                                f"{log_prefix} Saving {len(all_child_data)} children "
                                f"to {children_file}..."
                            )
                            child_table = None # Ensure var exists for finally block

                            # TODO: Add robust schema inference + pandas cleaning for children too?
                            # For now, using the simpler inference for children.
                            try: # Schema inference and Parquet writing for children
                                # --- Simple Schema Inference (Children) ---
                                logger.debug(
                                    f"{log_prefix} Inferring schema for children..."
                                )
                                # Use first record to infer, then adjust date field
                                if not all_child_data:
                                    raise ValueError(
                                        "Cannot infer schema from empty child data."
                                    )

                                inferred_schema = pa.Table.from_pylist(
                                    [all_child_data[0]]
                                ).schema
                                schema_fields = {
                                    name: field.type
                                    for name, field in zip(
                                        inferred_schema.names, inferred_schema
                                    )
                                }
                                # Ensure date field is date32
                                if self.DATE_FILTER_FIELD in schema_fields:
                                    if (
                                        schema_fields[self.DATE_FILTER_FIELD]
                                        != pa.date32()
                                    ):
                                        logger.warning(
                                            f"{log_prefix} Overriding inferred child type "
                                            f"({schema_fields[self.DATE_FILTER_FIELD]}) "
                                            f"for '{self.DATE_FILTER_FIELD}' to pa.date32()."
                                        )
                                        schema_fields[self.DATE_FILTER_FIELD] = (
                                            pa.date32()
                                        )
                                    else:
                                        logger.debug(
                                            f"{log_prefix} Child field "
                                            f"'{self.DATE_FILTER_FIELD}' correctly "
                                            f"inferred as pa.date32()."
                                        )
                                final_child_schema = pa.schema(
                                    list(schema_fields.items())
                                )
                                logger.info(
                                    f"{log_prefix} Using inferred schema for children: "
                                    f"{final_child_schema}"
                                )
                                # --- End Simple Schema Inference ---

                                # --- Create and Write Child Table ---
                                # NOTE: This might fail if child data also has
                                # type inconsistencies!
                                child_table = pa.Table.from_pylist(
                                    all_child_data,
                                    schema=final_child_schema
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
                                # --- End Child Table ---

                            except Exception as e: # Catch child Parquet errors
                                logger.error(
                                    f"{log_prefix} Failed during child Parquet processing "
                                    f"(schema or writing): {e}",
                                    exc_info=self.debug,
                                )
                                if self.debug:
                                    traceback.print_exc()
                                raise CommandError(
                                    f"Failed during child Parquet processing: {e}"
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
                            f"{log_prefix} No parent IDs found, skipping child fetch."
                        )

                    # --- Step 2a: Process Parents from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2a: Processing "
                            f"{parent_record_count} Parents from {parents_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2a: Processing Parents"
                    )

                    if parents_file.exists() and parent_record_count > 0:
                        parent_pf = pq.ParquetFile(parents_file)
                        total_parent_batches = (
                            parent_record_count + process_batch_size - 1
                        ) // process_batch_size
                        self.stdout.write(
                            f"{log_prefix} Processing parents in {total_parent_batches} "
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
                                    f"{log_prefix} Parent Batch {batch_num} finished: "
                                    f"{parent_load_result.created} C, "
                                    f"{parent_load_result.updated} U, "
                                    f"{parent_load_result.skipped} S, "
                                    f"{parent_load_result.errors} E. "
                                    f"({len(successful_ids_in_batch)} successful loads)"
                                )
                            )
                            if parent_load_result.error_details:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Parent Errors (Batch {batch_num}): "
                                        f"{len(parent_load_result.error_details)}"
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
                                        f"{len(parent_load_result.error_details) - 5} "
                                        f"more."
                                    )
                            if parent_load_result.errors > 0:
                                sync_successful = False # Mark sync as failed

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

                    # --- Step 2b: Process Children from File ---
                    self.stdout.write(
                        self.style.NOTICE(
                            f"{log_prefix} === Step 2b: Processing "
                            f"{child_record_count} Children from {children_file} ==="
                        )
                    )
                    logger.info(
                        f"{log_prefix} Starting Step 2b: Processing Children"
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
                            f"{log_prefix} Processing children in {total_child_batches} "
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
                                    f"{log_prefix} Child Batch {batch_num} is empty, "
                                    f"skipping."
                                )
                                continue

                            # Filter children based on successfully loaded parents
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
                                    f"{log_prefix} Batch {batch_num}: Filtered out "
                                    f"{skipped_count} children linked to unloaded parents."
                                )

                            if not filtered_child_data:
                                self.stdout.write(
                                    f"{log_prefix} No children in Batch {batch_num} "
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
                                    options.get("force_update") or options.get("full")
                                ),
                            )

                            child_stats["created"] += child_load_result.created
                            child_stats["updated"] += child_load_result.updated
                            child_stats["skipped"] += child_load_result.skipped
                            child_stats["errors"] += child_load_result.errors

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"{log_prefix} Child Batch {batch_num} finished: "
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
                                # Log first few errors to stdout/log
                                for k, err in enumerate(
                                    child_load_result.error_details[:5]
                                ):
                                    err_msg = f"  - {err}"
                                    self.stdout.write(err_msg)
                                    logger.warning(f"{log_prefix} Child Load Error: {err_msg}")
                                if len(child_load_result.error_details) > 5:
                                    more_msg = (
                                        f"  ... and "
                                        f"{len(child_load_result.error_details) - 5} "
                                        f"more."
                                    )
                                    self.stdout.write(more_msg)
                                    logger.warning(f"{log_prefix} {more_msg}")

                            if child_load_result.errors > 0:
                                sync_successful = False # Mark sync as failed

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
                            f"{log_prefix} Skipping child processing - no parents loaded."
                        )
                    else:
                        self.stdout.write(
                            f"{log_prefix} No child data file found or no records "
                            f"to process."
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

                # --- Step 3: Report Status ---
                end_time = timezone.now()
                duration = (end_time - command_start_time).total_seconds()

                self.stdout.write(
                    self.style.NOTICE(f"{log_prefix} === Step 3: Sync Summary ===")
                )

                # Report parent stats
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{log_prefix} Parent ({self.PARENT_ENTITY_TYPE}) summary: "
                        f"{parent_stats['created']} C, {parent_stats['updated']} U, "
                        f"{parent_stats['skipped']} S, {parent_stats['errors']} E."
                    )
                )

                # Report child stats
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{log_prefix} Child ({self.CHILD_ENTITY_TYPE}) summary: "
                        f"{child_stats['created']} C, {child_stats['updated']} U, "
                        f"{child_stats['skipped']} S, {child_stats['errors']} E."
                    )
                )

                log_summary = (
                    f"{log_prefix} Orchestrator finished in {duration:.2f} seconds. "
                    f"Mode: Full-Load. "
                    f"Parents: C={parent_stats['created']}, U={parent_stats['updated']}, "
                    f"S={parent_stats['skipped']}, E={parent_stats['errors']}. "
                    f"Children: C={child_stats['created']}, U={child_stats['updated']}, "
                    f"S={child_stats['skipped']}, E={child_stats['errors']}."
                )
                logger.info(log_summary)
                self.stdout.write(
                    f"{log_prefix} Sales record sync finished in {duration:.2f} seconds"
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


