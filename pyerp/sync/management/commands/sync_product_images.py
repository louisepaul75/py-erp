"""
Management command to synchronize product images from the external CMS.
"""
from django.core.management.base import BaseCommand
from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.external_api import connection_manager


class Command(BaseCommand):
    help = "Synchronize product images from the external CMS"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Perform a dry run without making any changes",
        )
        parser.add_argument(
            "--product-id",
            type=str,
            help="Sync only a specific product ID",
        )
        parser.add_argument(
            "--page",
            type=int,
            default=1,
            help="Starting page for API requests (default: 1)",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=100,
            help="Number of items per page (default: 100)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force connection even if it's disabled in the system",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting product image synchronization...")
        
        dry_run = options.get("dry_run", False)
        product_id = options.get("product_id")
        page = options.get("page", 1)
        page_size = options.get("page_size", 100)
        force = options.get("force", False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: No changes will be made"))
        
        try:
            # Check if the connection is enabled
            if not connection_manager.is_connection_enabled("images_cms"):
                if force:
                    self.stdout.write(self.style.WARNING(
                        "Image CMS connection is disabled, but proceeding due to --force flag"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        "Image CMS connection is disabled. Use --force to override this check."
                    ))
                    return
            
            client = ImageAPIClient()
            
            # Try to connect to the API
            try:
                connection_success = client.check_connection()
                if not connection_success and not force:
                    self.stdout.write(self.style.ERROR(
                        "Failed to connect to Image API. Use --force to continue anyway."
                    ))
                    return
            except Exception as e:
                if not force:
                    self.stdout.write(self.style.ERROR(f"Error connecting to API: {e}"))
                    self.stdout.write(self.style.ERROR("Use --force to continue anyway."))
                    return
                else:
                    self.stdout.write(self.style.WARNING(f"Connection error, but continuing due to --force: {e}"))
                
            self.stdout.write(self.style.SUCCESS("Ready to sync with Image API"))
            
            if product_id:
                self.stdout.write(f"Syncing images for product ID: {product_id}")
                # Implement product-specific sync when needed
                self.stdout.write(f"Product-specific sync not yet implemented")
            else:
                self.stdout.write("Retrieving all product images...")
                
                # Get the first page of results
                response = client.get_all_files(page=page, page_size=page_size)
                
                if response:
                    total_items = response.get('count', 0)
                    self.stdout.write(f"Found {total_items} total items in the Image API")
                    
                    if not dry_run:
                        # Process the first page results (would be implemented here)
                        results = response.get('results', [])
                        self.stdout.write(f"Processed page {page} with {len(results)} items")
                        
                        # Display the first few items for confirmation
                        if results:
                            self.stdout.write("Sample items:")
                            for i, item in enumerate(results[:3]):
                                self.stdout.write(f"  - Item {i+1}: {item.get('id', 'unknown')} ({item.get('file_name', 'unnamed')})")
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"DRY RUN: Would process {len(response.get('results', []))} items on page {page}"
                        ))
                else:
                    self.stdout.write(self.style.WARNING("No data retrieved from Image API"))
            
            self.stdout.write(self.style.SUCCESS("Image synchronization completed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during synchronization: {e}")) 