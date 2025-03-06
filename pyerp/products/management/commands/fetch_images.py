import logging
import sys
from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError
from pyerp.products.image_api import ImageAPIClient
from pyerp.products.models import Product


class Command(BaseCommand):
    help = "Fetch images from the external image API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sku",
            type=str,
            help="Product SKU to fetch images for",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Fetch first page of all images",
        )
        parser.add_argument(
            "--page",
            type=int,
            default=1,
            help="Page number for all images (default: 1)",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=5,
            help="Number of items per page (default: 5)",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )
        parser.add_argument(
            "--skip-db",
            action="store_true",
            help="Skip database lookup for products",
        )

    def handle(self, *args, **options):
        # Set up logging if debug is enabled
        if options["debug"]:
            logging.basicConfig(level=logging.DEBUG)
            logging.getLogger("urllib3").setLevel(logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        # Initialize the API client
        self.stdout.write("Initializing Image API client...")
        client = ImageAPIClient()
        
        # Display API URL information
        self.stdout.write(
            self.style.SUCCESS(f"API Base URL: {client.base_url}")
        )
        auth_str = f"API Authentication: {client.username}:"
        auth_str += "*" * len(client.password)
        self.stdout.write(auth_str)
        self.stdout.write(f"SSL Verification: {client.verify_ssl}")

        # Determine which action to take
        if options["sku"]:
            self.fetch_product_images(
                client, 
                options["sku"], 
                skip_db=options["skip_db"]
            )
        elif options["all"]:
            self.fetch_all_images(
                client, 
                options["page"], 
                options["page_size"],
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Please specify either --sku or --all. "
                    "Use --help for more information."
                )
            )
            sys.exit(1)

    def fetch_product_images(self, client, sku, skip_db=False):
        """Fetch images for a specific product by SKU"""
        self.stdout.write(
            f"Searching for images for product with SKU: {sku}"
        )
        self.stdout.write(
            f"API Endpoint: {client.base_url}all-files-and-articles/"
        )
        
        # First try to find the product in the database if not skipping DB
        product_found = False
        if not skip_db:
            try:
                product = Product.objects.get(sku=sku)
                self.stdout.write(f"Found product: {product.name}")
                
                # Get images using the product object
                self.stdout.write("Fetching images using product object...")
                images = client.get_product_images(product)
                product_found = True
                
                if not images:
                    msg = (
                        f"No images found for product {sku} "
                        f"using product object"
                    )
                    self.stdout.write(
                        self.style.WARNING(msg)
                    )
                    # Fall back to direct SKU search
                    product_found = False
            except (Product.DoesNotExist, ProgrammingError) as e:
                if isinstance(e, ProgrammingError):
                    db_error_msg = (
                        "Database error: Products table may not exist. "
                        "Skipping database lookup."
                    )
                    self.stdout.write(
                        self.style.WARNING(db_error_msg)
                    )
                else:
                    msg = f"Product with SKU {sku} not found in database"
                    self.stdout.write(
                        self.style.WARNING(msg)
                    )
        
        # If product not found or skipping DB, search directly by SKU
        if not product_found:
            self.stdout.write("Searching for images using SKU directly...")
            images = client.search_product_images(sku)
        
        # Display results
        if images:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Found {len(images)} images for SKU {sku}"
                )
            )
            
            # Get the best image
            best_image = client.get_best_image_for_product(sku)
            if best_image:
                self.stdout.write("\nBest image details:")
                ext_id = best_image.get('external_id')
                self.stdout.write(f"External ID: {ext_id}")
                img_type = best_image.get('image_type')
                self.stdout.write(f"Image Type: {img_type}")
                img_url = best_image.get('image_url')
                self.stdout.write(f"Image URL: {img_url}")
                thumb_url = best_image.get('thumbnail_url')
                self.stdout.write(
                    f"Thumbnail URL: {thumb_url}"
                )
                
                # Display associated articles
                if best_image.get('articles'):
                    self.stdout.write("\nAssociated articles:")
                    for article in best_image.get('articles'):
                        art_num = article.get('article_number')
                        var_code = article.get('variant_code')
                        is_front = article.get('front')
                        self.stdout.write(
                            f"  - Article: {art_num}, "
                            f"Variant: {var_code}, "
                            f"Front: {is_front}"
                        )
                
                # Display available image formats
                if best_image.get('images'):
                    self.stdout.write("\nAvailable image formats:")
                    for img in best_image.get('images'):
                        resolution = img.get('resolution')
                        res_str = (
                            f"{resolution[0]}x{resolution[1]}" 
                            if resolution and len(resolution) >= 2 
                            else "N/A"
                        )
                        img_type = img.get('type')
                        img_format = img.get('format')
                        self.stdout.write(
                            f"  - Type: {img_type}, "
                            f"Format: {img_format}, "
                            f"Resolution: {res_str}"
                        )
            else:
                self.stdout.write(
                    self.style.WARNING("Could not parse best image")
                )
        else:
            self.stdout.write(
                self.style.ERROR(f"No images found for SKU {sku}")
            )

    def fetch_all_images(self, client, page, page_size):
        """Fetch a page of all images from the API"""
        msg = (
            f"Fetching page {page} of all images "
            f"(page size: {page_size})..."
        )
        self.stdout.write(msg)
        self.stdout.write(
            f"API Endpoint: {client.base_url}all-files-and-articles/"
            f"?page={page}&page_size={page_size}"
        )
        images = client.get_all_images(page=page, page_size=page_size)

        if images:
            # Check if images is a list or a dict with results
            if isinstance(images, dict) and 'results' in images:
                image_list = images['results']
                total_count = images.get('count', 0)
                msg = (
                    f"Successfully retrieved {len(image_list)} images "
                    f"(total: {total_count})"
                )
            elif isinstance(images, list):
                image_list = images
                msg = f"Successfully retrieved {len(image_list)} images"
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Unexpected response format: {type(images)}"
                    )
                )
                return
                
            self.stdout.write(
                self.style.SUCCESS(msg)
            )
            
            # Display details of the first few images (up to 3)
            display_count = min(3, len(image_list))
            for i, image in enumerate(image_list[:display_count], 1):
                parsed_image = client.parse_image(image)
                self.stdout.write(f"\nImage {i} details:")
                ext_id = parsed_image.get('external_id')
                self.stdout.write(f"External ID: {ext_id}")
                img_type = parsed_image.get('image_type')
                self.stdout.write(f"Image Type: {img_type}")
                img_url = parsed_image.get('image_url')
                self.stdout.write(f"Image URL: {img_url}")
                thumb_url = parsed_image.get('thumbnail_url')
                self.stdout.write(f"Thumbnail URL: {thumb_url}")
                
                # Display associated articles
                if parsed_image.get('articles'):
                    # Just show the first article
                    article = parsed_image.get('articles')[0]
                    art_num = article.get('article_number')
                    var_code = article.get('variant_code')
                    self.stdout.write(
                        f"Associated with article: {art_num}, "
                        f"Variant: {var_code}"
                    )
            
            if len(image_list) > display_count:
                self.stdout.write(
                    f"\n... and {len(image_list) - display_count} more images"
                )
        else:
            self.stdout.write(
                self.style.ERROR("No images found or error occurred")
            ) 