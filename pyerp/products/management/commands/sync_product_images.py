"""
Management command to synchronize product images from the external image database.

This command fetches images from the external API and creates/updates ProductImage
records in the local database, linking them to the appropriate products.
"""

import time
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from pyerp.products.models import VariantProduct, ParentProduct, ProductImage, ImageSyncLog
from pyerp.products.image_api import ImageAPIClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Synchronize product images from the external image database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the sync process without making changes to the database',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of API pages to process',
        )
        parser.add_argument(
            '--page-size',
            type=int,
            default=100,
            help='Number of API results to fetch per page',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all images even if they have been recently synced',
        )
        parser.add_argument(
            '--skip-pages',
            type=int,
            default=0,
            help='Skip this many pages before starting to process',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        page_size = options['page_size']
        force = options['force']
        skip_pages = options['skip_pages']
        
        # Create sync log record (unless in dry-run mode)
        sync_log = None
        if not dry_run:
            sync_log = ImageSyncLog.objects.create(
                status='in_progress',
                started_at=timezone.now()
            )
        
        try:
            # Initialize counter variables
            images_added = 0
            images_updated = 0
            products_affected = set()  # Use a set to count unique products
            processed_images = {}  # Track which images we've processed by product
            
            # Initialize API client
            client = ImageAPIClient()
            
            # Store client as instance variable for use in helper methods
            self.client = client
            
            # Get API metadata to know total pages
            first_page = client._make_request("all-files-and-articles/", params={"page": 1, "page_size": 1})
            if not first_page:
                self.stdout.write(self.style.ERROR("Failed to connect to API"))
                return
                
            total_records = first_page.get('count', 0)
            total_pages = (total_records + page_size - 1) // page_size
            
            self.stdout.write(f"Found {total_records} total images across {total_pages} pages")
            
            # Limit pages if requested
            if limit:
                total_pages = min(total_pages, skip_pages + limit)
                
            # Process each page
            for page in range(skip_pages + 1, total_pages + 1):
                self.stdout.write(f"Processing page {page}/{total_pages}")
                
                # Get images for this page
                data = client._make_request("all-files-and-articles/", params={"page": page, "page_size": page_size})
                if not data:
                    self.stdout.write(self.style.WARNING(f"Failed to fetch page {page}"))
                    continue
                
                # Process each image
                for image_data in data.get('results', []):
                    # Skip if no articles associated with this image
                    articles = image_data.get('articles', [])
                    if not articles:
                        continue
                    
                    # Parse the image into a more usable format
                    parsed_image = client.parse_image(image_data)
                    
                    # Process each article (product) associated with this image
                    for article in articles:
                        article_number = article.get('number')
                        variant_code = article.get('variant')
                        is_front = article.get('front', False)
                        
                        if not article_number:
                            continue
                            
                        # Create a composite key for the article (SKU + variant)
                        if variant_code:
                            full_sku = f"{article_number}-{variant_code}"
                        else:
                            full_sku = article_number
                        
                        # Debug info
                        self.stdout.write(f"  Checking article: {article_number} (Variant: {variant_code})")
                            
                        # Try to find corresponding product - pass ONLY the article_number 
                        # (not the full_sku with -BE suffix)
                        product = self._find_product(article_number, variant_code)
                        if not product:
                            self.stdout.write(f"  No product found for {article_number}")
                            continue
                            
                        # Set front flag based on article data
                        parsed_image['is_front'] = is_front
                        
                        # Check if this product already has this image
                        if not dry_run:
                            try:
                                with transaction.atomic():
                                    # Create or update the image
                                    image, created = self._create_or_update_image(
                                        product, 
                                        parsed_image,
                                        processed_images.get(product.id, [])
                                    )
                                    
                                    # Update counters
                                    if created:
                                        images_added += 1
                                        self.stdout.write(f"  Added image for {product.sku}: {parsed_image['image_type']}")
                                    else:
                                        images_updated += 1
                                        self.stdout.write(f"  Updated image for {product.sku}: {parsed_image['image_type']}")
                                    
                                    # Track this product as affected
                                    products_affected.add(product.id)
                                    
                                    # Track that we've processed this image for this product
                                    if product.id not in processed_images:
                                        processed_images[product.id] = []
                                    processed_images[product.id].append(parsed_image['external_id'])
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"  Error processing image for {product.sku}: {str(e)}"))
                        else:
                            self.stdout.write(f"  Would {'create' if not hasattr(product, 'images') or not product.images.filter(external_id=parsed_image['external_id']).exists() else 'update'} image for {product.sku}: {parsed_image['image_type']}")
                            
                            # Track this product as affected even in dry run
                            products_affected.add(product.id)
            
            # Complete the sync log
            self.stdout.write(self.style.SUCCESS(
                f"Sync completed: {images_added} added, {images_updated} updated, "
                f"{len(products_affected)} products affected"
            ))
            
            if not dry_run and sync_log:
                sync_log.status = 'completed'
                sync_log.completed_at = timezone.now()
                sync_log.images_added = images_added
                sync_log.images_updated = images_updated
                sync_log.products_affected = len(products_affected)
                sync_log.save()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during sync: {str(e)}"))
            logger.exception("Error during product image sync")
            
            if not dry_run and sync_log:
                sync_log.status = 'failed'
                sync_log.completed_at = timezone.now()
                sync_log.error_message = str(e)
                sync_log.save()
                
    def _find_product(self, article_number, variant_code):
        """
        Find a product matching the article number without variant.
        
        Args:
            article_number: The base article number (e.g. "123456")
            variant_code: The variant code (e.g. "BE")
        
        Returns:
            A Product model instance or None if not found.
        """
        product = None
        
        # First try: exact match on article_number
        try:
            product = VariantProduct.objects.get(sku=article_number)
            self.stdout.write(f"    Found match by SKU: {article_number}")
            return product
        except VariantProduct.DoesNotExist:
            self.stdout.write(f"    No match by SKU: {article_number}")
        
        # Second try: match by article_number as parent product
        try:
            product = ParentProduct.objects.get(sku=article_number)
            self.stdout.write(f"    Found match as parent product: {article_number}")
            
            # If this is a parent and we have a variant code, try to find the variant
            if variant_code:
                try:
                    variant = VariantProduct.objects.filter(parent=product, variant_code=variant_code).first()
                    if variant:
                        self.stdout.write(f"    Found variant with code {variant_code} under parent {article_number}")
                        return variant
                except Exception:
                    pass
                    
            return product
        except ParentProduct.DoesNotExist:
            pass
        
        # Last attempt: startswith match (for SKUs with internal suffixes)
        try:
            products = VariantProduct.objects.filter(sku__startswith=f"{article_number}")
            if products.exists():
                product = products.first()
                self.stdout.write(f"    Found match by prefix: {article_number} -> {product.sku}")
                return product
        except Exception:
            pass
        
        # Not found - just log and return None
        self.stdout.write(f"    No product found for article number: {article_number}")
        return None
        
    def _create_or_update_image(self, product, parsed_image, existing_image_ids):
        """
        Create or update a ProductImage for the given product and image data.
        
        Args:
            product: The Product model instance
            parsed_image: Parsed image data dictionary
            existing_image_ids: List of image IDs already processed for this product
            
        Returns:
            Tuple of (image, created) where image is the ProductImage instance and
            created is a boolean indicating if it was newly created.
        """
        # Try to find existing image for this product and external ID
        image = None
        created = False
        
        # Only search for existing image if the product has an images relation
        if hasattr(product, 'images'):
            try:
                image = ProductImage.objects.get(
                    product=product,
                    external_id=parsed_image['external_id']
                )
                created = False
            except ProductImage.DoesNotExist:
                image = ProductImage(
                    product=product,
                    external_id=parsed_image['external_id']
                )
                created = True
        else:
            # For parent products or other cases without direct relationship
            image = ProductImage(
                product=product,
                external_id=parsed_image['external_id']
            )
            created = True
        
        # Update fields
        image.image_url = parsed_image['image_url']
        image.thumbnail_url = parsed_image.get('thumbnail_url')
        image.image_type = parsed_image['image_type']
        image.is_front = parsed_image.get('is_front', False)
        image.priority = self.client.get_image_priority(parsed_image)
        
        # Auto-generate alt text if not set
        if not image.alt_text:
            image.alt_text = f"{product.name} - {parsed_image['image_type']}"
        
        # Store metadata
        image.metadata = parsed_image.get('metadata', {})
        
        # Set as primary if this is the first image added or marked as front
        if not existing_image_ids:  # If this is the first image for this product
            image.is_primary = True
        elif parsed_image.get('is_front') and not image.is_primary:
            # If this is a front image and not already primary, make it primary
            # and remove primary flag from other images
            if hasattr(product, 'images'):
                product.images.update(is_primary=False)
            image.is_primary = True
        
        # Save the image
        image.save()
        
        return image, created 