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

from pyerp.products.models import Product, ProductImage, ImageSyncLog
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
            help='Limit the number of products to process',
        )
        parser.add_argument(
            '--product-sku',
            type=str,
            help='Sync images for a specific product SKU only',
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
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        product_sku = options['product_sku']
        page_size = options['page_size']
        force = options['force']
        
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
            images_deleted = 0
            products_affected = 0
            
            # Initialize API client
            client = ImageAPIClient()
            
            # Get products to sync
            if product_sku:
                products = Product.objects.filter(sku=product_sku)
                self.stdout.write(f"Syncing images for product SKU: {product_sku}")
            else:
                products = Product.objects.filter(is_active=True).order_by('sku')
                if limit:
                    products = products[:limit]
                self.stdout.write(f"Syncing images for {products.count()} products")
            
            # Process products
            for i, product in enumerate(products):
                # Show progress indicator
                if (i + 1) % 10 == 0 or i == 0:
                    self.stdout.write(f"Processing product {i + 1}/{products.count()}")
                
                # Get images for the product from API
                images = client.search_product_images(product.sku)
                
                if not images:
                    continue
                
                product_updated = False
                parsed_images = []
                
                # Process each image
                for image_data in images:
                    parsed_image = client.parse_image(image_data)
                    parsed_images.append(parsed_image)
                
                # Sort images by priority
                parsed_images = sorted(parsed_images, key=lambda x: client.get_image_priority(x))
                
                # Track external IDs to detect deleted images
                external_ids = [img['external_id'] for img in parsed_images]
                
                with transaction.atomic():
                    # Delete images not in the API response
                    if not dry_run and external_ids:
                        deleted_count = product.images.exclude(external_id__in=external_ids).delete()[0]
                        images_deleted += deleted_count
                        if deleted_count > 0:
                            product_updated = True
                    
                    # Create or update images
                    for i, parsed_image in enumerate(parsed_images):
                        # Check if this image exists
                        try:
                            image = ProductImage.objects.get(
                                product=product,
                                external_id=parsed_image['external_id']
                            )
                            is_new = False
                        except ProductImage.DoesNotExist:
                            if dry_run:
                                self.stdout.write(f"  Would create new image for {product.sku}: {parsed_image['image_type']}")
                                continue
                            
                            image = ProductImage(
                                product=product,
                                external_id=parsed_image['external_id']
                            )
                            is_new = True
                        
                        # Set first image as primary if no primary exists
                        is_primary = i == 0 and not product.images.filter(is_primary=True).exists()
                        
                        # Update fields
                        image.image_url = parsed_image['image_url']
                        image.thumbnail_url = parsed_image.get('thumbnail_url')
                        image.image_type = parsed_image['image_type']
                        image.is_front = parsed_image['is_front']
                        image.priority = client.get_image_priority(parsed_image)
                        
                        # Auto-generate alt text if not set
                        if not image.alt_text:
                            image.alt_text = f"{product.name} - {parsed_image['image_type']}"
                        
                        # Store metadata
                        image.metadata = parsed_image['metadata']
                        
                        # Set as primary if this is the first image added
                        if is_primary:
                            image.is_primary = True
                        
                        if not dry_run:
                            image.save()
                            if is_new:
                                images_added += 1
                                product_updated = True
                            else:
                                images_updated += 1
                        else:
                            action = "Create" if is_new else "Update"
                            self.stdout.write(f"  {action} image: {image.image_type} (Priority: {image.priority})")
                
                # Count affected products
                if product_updated:
                    products_affected += 1
            
            # Complete the sync log
            self.stdout.write(self.style.SUCCESS(
                f"Sync completed: {images_added} added, {images_updated} updated, "
                f"{images_deleted} deleted, {products_affected} products affected"
            ))
            
            if not dry_run and sync_log:
                sync_log.status = 'completed'
                sync_log.completed_at = timezone.now()
                sync_log.images_added = images_added
                sync_log.images_updated = images_updated
                sync_log.images_deleted = images_deleted
                sync_log.products_affected = products_affected
                sync_log.save()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during sync: {str(e)}"))
            logger.exception("Error during product image sync")
            
            if not dry_run and sync_log:
                sync_log.status = 'failed'
                sync_log.completed_at = timezone.now()
                sync_log.error_message = str(e)
                sync_log.save() 