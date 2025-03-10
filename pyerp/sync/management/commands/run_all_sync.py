"""Management command for running all data synchronization workflows."""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.management import call_command

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Run all data synchronization workflows."""

    help = 'Run all data synchronization workflows in the correct order'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--full',
            action='store_true',
            help='Perform full sync instead of incremental'
        )
        parser.add_argument(
            '--products-only',
            action='store_true',
            help='Only run product-related sync workflows'
        )
        parser.add_argument(
            '--customers-only',
            action='store_true',
            help='Only run customer-related sync workflows'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Set up logging
        if options['debug']:
            logger.setLevel(logging.DEBUG)
            
        start_time = timezone.now()
        self.stdout.write(f"Starting all sync workflows at {start_time}...")
        
        # Determine which workflows to run
        run_products = not options['customers_only']
        run_customers = not options['products_only']
        
        if not run_products and not run_customers:
            self.stdout.write(self.style.ERROR(
                "No workflows selected to run. "
                "Please specify at least one workflow."
            ))
            return
        
        # Run product-related sync workflows
        if run_products:
            self._run_product_workflows(options)
            
        # Run customer-related sync workflows
        if run_customers:
            self._run_customer_workflows(options)
            
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        self.stdout.write(self.style.SUCCESS(
            f"All sync workflows completed in {duration:.2f} seconds"
        ))
        
    def _run_product_workflows(self, options):
        """Run product-related sync workflows."""
        self.stdout.write("\n=== Running Product Sync Workflows ===")
        
        # Run products sync (includes both parent and variant products)
        self.stdout.write("\nRunning products sync...")
        try:
            call_command(
                'sync_products',
                force_update=options['full'],
                debug=options['debug']
            )
            self.stdout.write(self.style.SUCCESS(
                "Products sync completed successfully"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Products sync failed: {e}"
            ))
            
    def _run_customer_workflows(self, options):
        """Run customer-related sync workflows."""
        self.stdout.write("\n=== Running Customer Sync Workflows ===")
        
        # Run customer and address sync
        self.stdout.write("\nRunning customers sync...")
        try:
            call_command(
                'sync_customers',
                force_update=options['full'],
                debug=options['debug']
            )
            self.stdout.write(self.style.SUCCESS(
                "Customers sync completed successfully"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Customers sync failed: {e}"
            )) 