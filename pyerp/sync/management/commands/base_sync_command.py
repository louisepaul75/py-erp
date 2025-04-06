from argparse import ArgumentParser
import json
from datetime import timedelta
from typing import Any, Dict, Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from pyerp.utils.logging import get_logger

from pyerp.sync.models import SyncMapping # Assuming SyncMapping might be needed later


logger = get_logger(__name__)

class BaseSyncCommand(BaseCommand):
    """
    Base command for data synchronization tasks, providing common arguments
    and filter handling logic.
    """
    help = "Base command for sync operations" # Specific commands should override

    # Define field names expected by extractors (can be overridden by subclasses or config)
    DEFAULT_TIMESTAMP_FIELD = "modified_date"  # Aligned with test_legacy_erp_filters.py

    def add_arguments(self, parser: ArgumentParser):
        """Add common command arguments."""
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform a full sync instead of incremental.",
        )
        parser.add_argument(
            "--force-update", # Added for compatibility with run_all_sync.sh
            action="store_true",
            help="Alias for --full. Perform a full sync.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch.",
        )
        parser.add_argument(
            "--top",
            type=int,
            help="Limit the number of records to sync (processed by extractor).",
        )
        parser.add_argument(
            "--days",
            type=int,
            help=(
                "Sync records modified/created in the last N days "
                "(uses timestamp field)."
            ),
        )
        parser.add_argument(
            "--filters",
            type=str,
            help=(
                'JSON string with additional extractor-specific filters '
                '(e.g., {"field": "value"}).'
            ),
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with additional logging.",
        )
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_false", # Default is True (fail)
            dest="fail_on_filter_error",
            default=True,
            help=(
                "Don't fail if date filter query causes an error in the extractor "
                "(default: fail)."
            ),
        )
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear relevant extractor cache before running.",
        )
        # Add specific arguments in subclasses if needed
        # super().add_arguments(parser)


    def build_query_params(self, options: Dict[str, Any], mapping: Optional[SyncMapping] = None) -> Dict[str, Any]:
        """
        Builds a dictionary of query parameters for the extractor based on
        common command-line options.

        Args:
            options: Dictionary of command-line options from handle().
            mapping: Optional SyncMapping instance to potentially get config like timestamp field.

        Returns:
            Dictionary of query parameters to be passed to the extractor.
        """
        query_params = {}
        filter_query_list = []  # Initialize the list at the start
        command_start_time = timezone.now()  # Consistent time reference

        # 1. Handle --filters (direct extractor filters)
        raw_custom_filters = options.get("filters")
        if raw_custom_filters:
            try:
                custom_filters_parsed = json.loads(raw_custom_filters)
                if not isinstance(custom_filters_parsed, dict):
                    logger.warning(
                        "Ignoring --filters argument: Expected JSON dictionary, "
                        f"got: {raw_custom_filters}"
                    )
                    custom_filters_parsed = {}  # Reset if not a dict
                else:
                    logger.info(
                        f"Parsed custom filters from --filters: {custom_filters_parsed}"
                    )
                    query_params.update(custom_filters_parsed)
            except json.JSONDecodeError as e:
                logger.error(
                    f"Invalid JSON format for --filters option: {e}. Ignoring."
                )

        # 2. Handle --top
        if options.get("top"):
            query_params["$top"] = options["top"]
            logger.info(f"Applied $top filter: {options['top']}")

        # 3. Handle --days (Timestamp Filtering)
        timestamp_field = self.DEFAULT_TIMESTAMP_FIELD  # Always use modified_date
        # Note: Not allowing override of timestamp_field to ensure consistency
        
        if options.get("days") is not None:
            try:
                days = int(options["days"])
                if days >= 0:
                    modified_since = command_start_time - timedelta(days=days)
                    # Format date as YYYY-MM-DD to match test_legacy_erp_filters.py
                    date_str = modified_since.strftime("%Y-%m-%d")
                    # Add to filter_query list in the format used by test_legacy_erp_filters.py
                    filter_query_list.append([timestamp_field, ">=", date_str])
                    logger.info(
                        f"Applied --days filter: records modified since {date_str} "
                        f"({days} days ago) using field '{timestamp_field}'."
                    )
                else:
                    logger.warning(
                        f"Ignoring --days argument: Value must be non-negative, "
                        f"got {days}."
                    )
            except ValueError:
                logger.error(
                    f"Invalid value for --days: {options['days']}. "
                    f"Must be an integer."
                )

        # Add the filter_query_list to query_params if it has any filters
        if filter_query_list:
            query_params["filter_query"] = filter_query_list
            logger.debug(f"Added filter_query to params: {filter_query_list}")

        logger.debug(f"Built query_params: {query_params}")
        return query_params

    def handle(self, *args, **options):
        """Main command handler. Subclasses should implement their specific logic."""
        raise NotImplementedError(
            "Subclasses must implement the handle() method."
        )

    def get_mapping(self, entity_type: str) -> SyncMapping:
        """Helper to get the active SyncMapping for a given entity type."""
        try:
            mapping = SyncMapping.objects.get(entity_type=entity_type, active=True)
            logger.info(f"Found active mapping for entity_type='{entity_type}' (ID: {mapping.id})")
            return mapping
        except SyncMapping.DoesNotExist:
            raise CommandError(f"No active SyncMapping found for entity_type='{entity_type}'. Please configure it in the admin.")
        except SyncMapping.MultipleObjectsReturned:
             raise CommandError(f"Multiple active SyncMappings found for entity_type='{entity_type}'. Deactivate duplicates.")

    def run_sync_via_command(self, entity_type: str, options: Dict[str, Any], query_params: Optional[Dict[str, Any]] = None):
        """
        Calls the 'run_sync' management command with appropriate arguments
        derived from the base command options and provided query_params.

        Args:
            entity_type: The entity type to sync (e.g., 'customer', 'product_variant').
            options: The dictionary of parsed arguments from the command line.
            query_params: Specific query parameters for this run_sync call (optional).
                          If None, it defaults to building params from base options.
        """
        if query_params is None:
            # Build query params based on standard options if specific ones aren't provided
            # We might need the mapping here if build_query_params requires it
            mapping = self.get_mapping(entity_type) # Fetch mapping if needed
            query_params = self.build_query_params(options, mapping)

        # --- Prepare filters for run_sync ---
        filters_for_command = {}
        filter_query_list = []

        # Extract standard/known params and build the filter_query list
        if query_params:
            for key, value in query_params.items():
                if key == "$top":
                    # Pass $top directly if extractor handles it
                    filters_for_command["$top"] = value
                    # *** DO NOT add $top to filter_query list ***
                    continue # Skip to next item
                elif key == "modified_since":
                    # Assuming extractor handles 'modified_since' directly or
                    # via date logic
                    filters_for_command[key] = value
                    # *** DO NOT add modified_since to filter_query list ***
                    continue # Skip to next item
                # Handle parent record filtering specifically if needed by extractor
                elif key == "parent_record_ids":
                    filters_for_command[key] = value
                    # Ensure parent_field is also included if present in original query_params
                    if "parent_field" in query_params:
                        filters_for_command["parent_field"] = query_params["parent_field"]
                    # These keys are handled directly by the extractor, skip adding to filter_query
                    continue # Skip to next item after handling parent filters
                elif key == "parent_field":
                    # If parent_field is encountered but parent_record_ids wasn't, include it.
                    # If parent_record_ids was present, this elif is skipped by the continue above.
                    if "parent_record_ids" not in filters_for_command:
                        filters_for_command[key] = value
                    # In either case, don't let it fall through to filter_query list
                    continue # Skip to next item

                # --- Handle other keys as filter_query items --- 
                # Basic handling for __in, exact match, etc.
                field_name = key
                operator = "=" # Default operator

                if key.endswith("__in") and isinstance(value, list):
                    field_name = key[:-4]
                    # OData doesn't directly support 'IN'. We create multiple
                    # 'OR' conditions.
                    # [[field, '=', val1], [field, '=', val2], ...]
                    # connected by OR implicitly
                    # This structure is expected by LegacyAPIExtractor's
                    # parent_filter logic
                    # Let's reuse that structure for __in filters.

                    # *** Special case: Map legacy_id__in to __KEY for filtering ***
                    if field_name == "legacy_id":
                        logger.debug(
                            "Mapping filter field 'legacy_id' to '__KEY' for API query."
                        )
                        field_name = "__KEY"

                    if value:  # Only add if list is not empty
                        filter_query_list.extend(
                            [[field_name, "=", item] for item in value]
                        )
                        # Skip adding single filter below for __in
                        continue # Skip to next item after handling __in
                elif isinstance(
                    value, (str, int, float, bool)
                ):  # Basic exact match
                    # *** Special case: Map legacy_id exact match to __KEY ***
                    if field_name == "legacy_id":
                        logger.debug(
                            "Mapping filter field 'legacy_id' to '__KEY' for API query."
                        )
                        field_name = "__KEY"
                    # Assume exact match if no operator specified
                    filter_query_list.append([field_name, operator, value])
                # TODO: Add more sophisticated filter mapping
                #       (e.g., __gt, __lt, __contains) if needed
                else:
                    logger.warning(f"Skipping query_param key '{key}' with non-basic value type: {type(value)}")

        # Add the constructed filter_query list to the command filters
        if filter_query_list:
            # Use the key expected by LegacyAPIExtractor
            filters_for_command["filter_query"] = filter_query_list

        filters_json = json.dumps(filters_for_command) if filters_for_command else None
        # --- End filter preparation ---

        # Prepare options for call_command, only passing what run_sync expects
        run_sync_options = {
            "entity_type": entity_type,
            "full": options.get("full") or options.get("force_update", False),
            "batch_size": options["batch_size"],
            "filters": filters_json,
            "debug": options["debug"],
            "fail_on_filter_error": options["fail_on_filter_error"],
            # Clear cache only on the *first* call within a multi-step command sequence
            # Subclass handle method needs to manage this correctly if calling run_sync multiple times.
            "clear_cache": options.get("clear_cache", False), # Default to False here, let handle() control
        }

        # Remove None values to avoid passing them explicitly if not set
        run_sync_options = {k: v for k, v in run_sync_options.items() if v is not None}

        logger.info(f"Calling run_sync for '{entity_type}' with options: {run_sync_options}")

        try:
            from django.core.management import call_command
            call_command(
                "run_sync",
                **run_sync_options
            )
            self.stdout.write(self.style.SUCCESS(f"run_sync for '{entity_type}' finished successfully."))
            return True # Indicate success
        except CommandError as e:
            # CommandError from run_sync might indicate no mapping found, etc.
            self.stderr.write(self.style.ERROR(f"run_sync command for '{entity_type}' failed: {e}"))
            # Re-raise specific CommandErrors if needed for script exit codes
            raise e
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred during run_sync for '{entity_type}': {e}"))
            # Consider logging traceback if debug is enabled
            if options.get("debug"):
                import traceback
                traceback.print_exc()
            return False # Indicate failure 