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
        """Orchestrate the multi-stage sync process."""
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

        # --- Step 1: Fetch Parent Record IDs (AbsNr) using initial filters ---
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

        # --- Step 2: Run Full Sales Records Sync (using initial filters) ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 2: Running Parent Sync "
            f"({self.PARENT_ENTITY_TYPE}) ==="
        ))
        logger.info(
            f"{log_prefix} Starting Step 2: {self.PARENT_ENTITY_TYPE} Sync"
        )
        parent_sync_successful = False
        try:
            parent_pipeline = PipelineFactory.create_pipeline(parent_mapping)
            # Note: Cache was potentially cleared in Step 1 if requested.

            self.stdout.write(
                f"{log_prefix} Using query params for parent sync: "
                f"{initial_query_params}"
            )
            with parent_pipeline.extractor:
                parent_source_data = parent_pipeline.extractor.extract(
                    query_params=initial_query_params,  # Use initial params
                    fail_on_filter_error=options.get(
                        "fail_on_filter_error", True
                    )
                )
            self.stdout.write(
                f"{log_prefix} Extracted {len(parent_source_data)} parent "
                f"records for full sync."
            )

            if parent_source_data:
                transformed_parent_data = (
                    parent_pipeline.transformer.transform(parent_source_data)
                )
                self.stdout.write(
                    f"{log_prefix} Transformed {len(transformed_parent_data)} "
                    f"parent records."
                )
                load_result = parent_pipeline.loader.load(
                    transformed_parent_data,
                    update_existing=(
                        options.get("force_update") or options.get("full")
                    ),
                )
                self.stdout.write(self.style.SUCCESS(
                    f"{log_prefix} Parent ({self.PARENT_ENTITY_TYPE}) load finished: "
                    f"{load_result.created} created, "
                    f"{load_result.updated} updated, {load_result.skipped} skipped, "
                    f"{load_result.errors} errors."
                ))
                if load_result.error_details:
                    self.stdout.write(self.style.WARNING(
                        f"{log_prefix} Parent Load Errors:"
                    ))
                    for i, err in enumerate(load_result.error_details):
                        if i < 10:
                            self.stdout.write(f"- {err}")
                        else:
                            self.stdout.write(
                                f"... and {len(load_result.error_details) - 10} "
                                f"more errors."
                            )
                            break
            else:
                self.stdout.write(
                    f"{log_prefix} No parent records extracted, skipping "
                    f"transform and load."
                )

            parent_sync_successful = True  # Mark success if no exceptions
            logger.info(
                f"{log_prefix} Step 2: {self.PARENT_ENTITY_TYPE} Sync finished "
                f"successfully."
            )

        except Exception as e:
            parent_sync_successful = False
            self.stderr.write(self.style.ERROR(
                f"{log_prefix} Step 2 Failed: {self.PARENT_ENTITY_TYPE} sync "
                f"pipeline error: {e}"
            ))
            logger.error(
                f"{log_prefix} Step 2: {self.PARENT_ENTITY_TYPE} Sync failed: {e}",
                exc_info=self.debug
            )
            if self.debug:
                traceback.print_exc()
            # Continue to item sync, log failure.

        # --- Step 3: Run Sales Record Items Sync (using ONLY fetched Parent IDs) ---
        self.stdout.write(self.style.NOTICE(
            f"\n{log_prefix} === Step 3: Running Child Sync "
            f"({self.CHILD_ENTITY_TYPE}) ==="
        ))
        logger.info(
            f"{log_prefix} Starting Step 3: {self.CHILD_ENTITY_TYPE} Sync"
        )
        child_sync_successful = False
        if not parent_record_ids:
            message = (
                f"Skipping child ({self.CHILD_ENTITY_TYPE}) sync as no parent "
                f"IDs were found in Step 1."
            )
            self.stdout.write(self.style.WARNING(f"{log_prefix} {message}"))
            logger.warning(f"{log_prefix} Step 3: {message}")
            child_sync_successful = True  # Mark as successful (nothing to do)
        else:
            try:
                child_pipeline = PipelineFactory.create_pipeline(child_mapping)
                # Prepare filters for items: ONLY use fetched parent IDs
                item_filters = {
                    "parent_record_ids": parent_record_ids,
                    "parent_field": self.CHILD_PARENT_LINK_FIELD
                }
                self.stdout.write(
                    f"{log_prefix} Filtering child sync using "
                    f"{len(parent_record_ids)} parent IDs "
                    f"({self.PARENT_LEGACY_KEY_FIELD}) from Step 1."
                )
                logger.info(
                    f"{log_prefix} Filtering child sync with item_filters: "
                    f"{item_filters}"
                )

                # Do NOT clear cache; Do NOT pass initial query params
                with child_pipeline.extractor:
                    child_source_data = child_pipeline.extractor.extract(
                        query_params=item_filters,  # Use ONLY item-specific filters
                        fail_on_filter_error=options.get(
                            "fail_on_filter_error", True
                        )
                    )
                self.stdout.write(
                    f"{log_prefix} Extracted {len(child_source_data)} "
                    f"child records."
                )

                if child_source_data:
                    transformed_child_data = (
                        child_pipeline.transformer.transform(child_source_data)
                    )
                    self.stdout.write(
                        f"{log_prefix} Transformed {len(transformed_child_data)} "
                        f"child records."
                    )
                    load_result = child_pipeline.loader.load(
                        transformed_child_data,
                        update_existing=(
                           options.get("force_update") or options.get("full")
                        ),
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"{log_prefix} Child ({self.CHILD_ENTITY_TYPE}) load finished: "
                        f"{load_result.created} created, "
                        f"{load_result.updated} updated, {load_result.skipped} skipped, "
                        f"{load_result.errors} errors."
                    ))
                    if load_result.error_details:
                        self.stdout.write(self.style.WARNING(
                            f"{log_prefix} Child Load Errors:"
                        ))
                        for i, err in enumerate(load_result.error_details):
                            if i < 10:
                                self.stdout.write(f"- {err}")
                            else:
                                self.stdout.write(
                                    f"... and {len(load_result.error_details) - 10} "
                                    f"more errors."
                                )
                                break
                else:
                    self.stdout.write(
                        f"{log_prefix} No child records extracted, skipping "
                        f"transform and load."
                    )

                child_sync_successful = True  # Mark success if no exceptions
                logger.info(
                    f"{log_prefix} Step 3: {self.CHILD_ENTITY_TYPE} Sync finished "
                    f"successfully."
                )

            except Exception as e:
                child_sync_successful = False
                self.stderr.write(self.style.ERROR(
                    f"{log_prefix} Step 3 Failed: {self.CHILD_ENTITY_TYPE} sync "
                    f"pipeline error: {e}"
                ))
                logger.error(
                    f"{log_prefix} Step 3: {self.CHILD_ENTITY_TYPE} Sync failed: {e}",
                    exc_info=self.debug
                )
                if self.debug:
                    traceback.print_exc()

        # --- Step 4: Report Overall Status ---
        end_time = timezone.now()
        duration = (end_time - command_start_time).total_seconds()
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
            if not parent_sync_successful:
                self.stdout.write(self.style.WARNING(
                    f"{log_prefix} Note: Parent sync (Step 2) encountered an error."
                ))
            if not child_sync_successful:
                # Only raise CommandError if child sync failed
                raise CommandError(error_msg)
            else:
                # Parent failed, child succeeded/skipped
                self.stdout.write(self.style.WARNING(error_msg))

