"""Management command for running all data synchronization workflows."""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run all data synchronization workflows."""

    help = "Run all data synchronization workflows in the correct order"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--full",
            action="store_true",
            help="Perform full sync instead of incremental",
        )
        parser.add_argument(
            "--employees-only",
            action="store_true",
            help="Only run employee-related sync workflows",
        )
        parser.add_argument(
            "--customers-only",
            action="store_true",
            help="Only run customer-related sync workflows",
        )
        parser.add_argument(
            "--products-only",
            action="store_true",
            help="Only run product-related sync workflows",
        )
        parser.add_argument(
            "--inventory-only",
            action="store_true",
            help="Only run inventory-related sync workflows",
        )
        parser.add_argument(
            "--sales-only",
            action="store_true",
            help="Only run sales-related sync workflows",
        )
        parser.add_argument(
            "--production-only",
            action="store_true",
            help="Only run production-related sync workflows",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options["debug"]:
            logger.setLevel(logging.DEBUG)

        start_time = timezone.now()
        self.stdout.write(f"Starting all sync workflows at {start_time}...")

        # Determine which workflows to run
        only_flags = [
            options["employees_only"],
            options["customers_only"],
            options["products_only"],
            options["inventory_only"],
            options["sales_only"],
            options["production_only"],
        ]

        # If no specific workflow is selected, run all
        run_all = not any(only_flags)

        # Run workflows in dependency order
        if run_all or options["employees_only"]:
            self._run_employee_workflows(options)

        if run_all or options["customers_only"]:
            self._run_customer_workflows(options)

        if run_all or options["products_only"]:
            self._run_product_workflows(options)

        if run_all or options["inventory_only"]:
            self._run_inventory_workflows(options)

        if run_all or options["sales_only"]:
            self._run_sales_workflows(options)

        if run_all or options["production_only"]:
            self._run_production_workflows(options)

        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()

        self.stdout.write(
            self.style.SUCCESS(
                f"All sync workflows completed in {duration:.2f} seconds"
            )
        )

    def _run_employee_workflows(self, options):
        """Run employee-related sync workflows."""
        self.stdout.write("\n=== Running Employee Sync Workflows ===")

        # Run employees sync
        self.stdout.write("\nRunning employees sync...")
        try:
            call_command(
                "run_sync",
                entity_type="employee",
                full=options["full"],
                debug=options["debug"],
            )
            self.stdout.write(
                self.style.SUCCESS("Employees sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Employees sync failed: {e}"))

    def _run_customer_workflows(self, options):
        """Run customer-related sync workflows."""
        self.stdout.write("\n=== Running Customer Sync Workflows ===")

        # Run customers sync
        self.stdout.write("\nRunning customers sync...")
        try:
            call_command(
                "run_sync",
                entity_type="customer",
                full=options["full"],
                debug=options["debug"],
            )
            self.stdout.write(
                self.style.SUCCESS("Customers sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Customers sync failed: {e}"))

    def _run_product_workflows(self, options):
        """Run product-related sync workflows."""
        self.stdout.write("\n=== Running Product Sync Workflows ===")

        # Run products sync (includes both parent and variant products)
        self.stdout.write("\nRunning products sync...")
        try:
            call_command(
                "sync_products", force_update=options["full"], debug=options["debug"]
            )
            self.stdout.write(
                self.style.SUCCESS("Products sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Products sync failed: {e}"))

    def _run_inventory_workflows(self, options):
        """Run inventory-related sync workflows."""
        self.stdout.write("\n=== Running Inventory Sync Workflows ===")

        # Run inventory sync
        self.stdout.write("\nRunning inventory sync...")
        try:
            call_command("sync_inventory", full=options["full"], debug=options["debug"])
            self.stdout.write(
                self.style.SUCCESS("Inventory sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Inventory sync failed: {e}"))

    def _run_sales_workflows(self, options):
        """Run sales-related sync workflows."""
        self.stdout.write("\n=== Running Sales Sync Workflows ===")

        # Run sales records sync
        self.stdout.write("\nRunning sales records sync...")
        try:
            call_command(
                "sync_sales_records", force_update=options["full"], debug=options["debug"]
            )
            self.stdout.write(
                self.style.SUCCESS("Sales records sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Sales records sync failed: {e}"))

    def _run_production_workflows(self, options):
        """Run production-related sync workflows."""
        self.stdout.write("\n=== Running Production Sync Workflows ===")

        # Run production orders sync
        self.stdout.write("\nRunning production orders sync...")
        try:
            call_command(
                "sync_production", force_update=options["full"], debug=options["debug"]
            )
            self.stdout.write(
                self.style.SUCCESS("Production sync completed successfully")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Production sync failed: {e}"))
