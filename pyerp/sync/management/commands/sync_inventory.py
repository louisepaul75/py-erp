"""Management command for synchronizing inventory data."""

import logging
from datetime import timedelta
from typing import Dict, List, Set

from django.core.management.base import BaseCommand
from django.utils import timezone

from pyerp.sync.models import SyncMapping
from pyerp.sync.pipeline import PipelineFactory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Synchronize inventory data from legacy system."""

    help = "Synchronize inventory data from legacy system"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--component",
            type=str,
            choices=[
                "storage_locations",
                "box_types",
                "boxes",
                "box_slots",
                "product_storage",
                "product_storage_artikel_lagerorte",
                "product_storage_lager_schuetten",
                "box_storage",
            ],
            help="Specific inventory component to sync",
        )
        parser.add_argument(
            "--days",
            type=int,
            help="Only sync records modified in the last N days",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Number of records to process in each batch",
        )
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sync instead of incremental",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output",
        )
        parser.add_argument(
            "--fail-on-filter-error",
            action="store_true",
            default=False,
            help="Fail if date filter doesn't work (default: don't fail)",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        # Get component to sync
        component = options["component"]

        # Get mappings to process
        mappings = self._get_mappings(component)

        if not mappings:
            self.stdout.write(self.style.WARNING("No active inventory mappings found"))
            return

        # Build query parameters
        query_params = self._build_query_params(options)

        # Build dependency graph and get ordered components
        dependency_graph = self._build_dependency_graph(mappings)
        ordered_components = self._get_ordered_components(dependency_graph)

        # Process each component in dependency order
        for component_name in ordered_components:
            component_mappings = [m for m in mappings if m.entity_type == component_name]
            if not component_mappings:
                continue

            self.stdout.write(f"\nProcessing {component_name} sync...")
            for mapping in component_mappings:
                self.stdout.write(f"Processing mapping: {mapping}")

                try:
                    # Create and run pipeline
                    pipeline = PipelineFactory.create_pipeline(mapping)

                    start_time = timezone.now()
                    self.stdout.write(f"Starting sync at {start_time}...")

                    sync_log = pipeline.run(
                        incremental=not options["full"],
                        batch_size=options["batch_size"],
                        query_params=query_params,
                        fail_on_filter_error=options["fail_on_filter_error"],
                    )

                    end_time = timezone.now()
                    duration = (end_time - start_time).total_seconds()

                    if sync_log.status == "completed":
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"{component_name} sync completed in {duration:.2f} seconds"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{component_name} sync completed with status {sync_log.status} "
                                f"in {duration:.2f} seconds"
                            )
                        )

                    self.stdout.write(
                        f"Processed {sync_log.records_processed} records, "
                        f"succeeded {sync_log.records_succeeded}, "
                        f"failed {sync_log.records_failed}"
                    )

                    if sync_log.error_message:
                        self.stdout.write(
                            self.style.ERROR(f"Error: {sync_log.error_message}")
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error processing {component_name}: {e}")
                    )

    def _get_mappings(self, component=None):
        """Get inventory mappings based on filter criteria."""
        # Start with all active inventory mappings
        mappings = SyncMapping.objects.filter(active=True)

        # Filter by entity type if component is specified
        if component:
            mappings = mappings.filter(entity_type=component)
        else:
            # Get all inventory-related mappings
            inventory_components = [
                "storage_locations",
                "box_types",
                "boxes",
                "box_slots",
                "product_storage",
                "product_storage_artikel_lagerorte",
                "product_storage_lager_schuetten",
                "box_storage",
            ]
            mappings = mappings.filter(entity_type__in=inventory_components)

        return list(mappings)

    def _build_query_params(self, options):
        """Build query parameters from command options."""
        query_params = {}

        # Add date filter if days option is provided
        if options.get("days"):
            days = options["days"]
            modified_since = timezone.now() - timedelta(days=days)

            # Format date for filter
            date_str = modified_since.strftime("%Y-%m-%d")
            query_params["modified_date"] = {"gt": date_str}

            filter_msg = f"Filtering records modified since {date_str}"
            self.stdout.write(f"{filter_msg} ({days} days ago)")

        return query_params

    def _build_dependency_graph(self, mappings: List[SyncMapping]) -> Dict[str, Set[str]]:
        """Build a dependency graph from mappings.

        Args:
            mappings: List of sync mappings

        Returns:
            Dictionary mapping component names to their dependencies
        """
        graph = {}
        for mapping in mappings:
            component = mapping.entity_type
            if component not in graph:
                graph[component] = set()

            # Add dependencies from mapping config
            dependencies = mapping.mapping_config.get("dependencies", [])
            graph[component].update(dependencies)

        return graph

    def _get_ordered_components(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Get components in dependency order using topological sort.

        Args:
            graph: Dependency graph

        Returns:
            List of components in dependency order
        """
        # Track visited and temporary marks for cycle detection
        visited = set()
        temp = set()
        ordered = []

        def visit(node):
            """Visit a node in the graph."""
            if node in temp:
                raise ValueError(f"Cyclic dependency detected involving {node}")
            if node in visited:
                return

            temp.add(node)

            # Visit dependencies
            for dep in graph.get(node, []):
                visit(dep)

            temp.remove(node)
            visited.add(node)
            ordered.append(node)

        # Visit each node
        for node in graph:
            if node not in visited:
                visit(node)

        return ordered


if __name__ == "__main__":
    import os
    import django

    # Set up Django environment
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
    django.setup()

    # Import argparse to handle command line arguments
    import argparse

    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Synchronize inventory data from legacy system"
    )

    # Add arguments
    parser.add_argument(
        "--component",
        type=str,
        choices=[
            "storage_locations",
            "box_types",
            "boxes",
            "box_slots",
            "product_storage",
            "product_storage_artikel_lagerorte",
            "product_storage_lager_schuetten",
            "box_storage",
        ],
        help="Specific inventory component to sync",
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Only sync records modified in the last N days",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of records to process in each batch",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform full sync instead of incremental",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )
    parser.add_argument(
        "--fail-on-filter-error",
        action="store_true",
        default=False,
        help="Fail if date filter doesn't work (default: don't fail)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Convert namespace to dictionary
    options = vars(args)

    # Create and run command
    command = Command()
    command.handle(**options)
