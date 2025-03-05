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
from django.db.models import Q

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
            default=500,  # Increased default page size
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
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each database batch',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        page_size = options['page_size']
        force = options['force']
        skip_pages = options['skip_pages']
        batch_size = options['batch_size']
        
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
                
                # Get page of results from API
                results = client.get_all_images(page=page, page_size=page_size)
                if not results or 'results' not in results:
                    self.stdout.write(self.style.WARNING(f"No results found on page {page}"))
                    continue
                
                # Lists to store bulk operations
                images_to_create = []
                images_to_update = []
                products_in_batch = set()
                
                # Process each image
                for image_data in results['results']:
                    # Parse the image data
                    parsed_image = client.parse_image(image_data)
                    if not parsed_image:
                        continue
                    
                    # Get associated articles
                    for article in parsed_image.get('articles', []):
                        article_number = article.get('article_number', '')
                        variant_code = article.get('variant_code', '')
                        
                        # Find matching product
                        product = self._find_product(article_number, variant_code)
                        if not product:
                            continue
                        
                        if not dry_run:
                            # Check if image exists
                            existing_image = None
                            if hasattr(product, 'images'):
                                existing_image = ProductImage.objects.filter(
                                    product=product,
                                    external_id=parsed_image['external_id']
                                ).first()
                            
                            # Prepare image instance
                            if existing_image:
                                # Update existing image
                                existing_image.image_url = parsed_image['image_url']
                                existing_image.thumbnail_url = parsed_image.get('thumbnail_url')
                                existing_image.image_type = parsed_image['image_type']
                                existing_image.is_front = parsed_image.get('is_front', False)
                                images_to_update.append(existing_image)
                                images_updated += 1
                            else:
                                # Create new image
                                new_image = ProductImage(
                                    product=product,
                                    external_id=parsed_image['external_id'],
                                    image_url=parsed_image['image_url'],
                                    thumbnail_url=parsed_image.get('thumbnail_url'),
                                    image_type=parsed_image['image_type'],
                                    is_front=parsed_image.get('is_front', False)
                                )
                                images_to_create.append(new_image)
                                images_added += 1
                            
                            products_in_batch.add(product.id)
                            products_affected.add(product.id)
                        else:
                            self.stdout.write(f"  Would {'create' if not hasattr(product, 'images') or not product.images.filter(external_id=parsed_image['external_id']).exists() else 'update'} image for {product.sku}: {parsed_image['image_type']}")
                            products_affected.add(product.id)
                
                # Bulk create/update in transaction
                if not dry_run and (images_to_create or images_to_update):
                    with transaction.atomic():
                        # Bulk create new images
                        if images_to_create:
                            ProductImage.objects.bulk_create(
                                images_to_create,
                                batch_size=batch_size
                            )
                        
                        # Bulk update existing images
                        if images_to_update:
                            ProductImage.objects.bulk_update(
                                images_to_update,
                                ['image_url', 'thumbnail_url', 'image_type', 'is_front'],
                                batch_size=batch_size
                            )
                        
                        # Update primary flags for Produktfoto front images
                        if products_in_batch:
                            # First, reset all primary flags
                            ProductImage.objects.filter(
                                product_id__in=products_in_batch
                            ).update(is_primary=False)
                            
                            # Then set primary for front Produktfotos
                            ProductImage.objects.filter(
                                product_id__in=products_in_batch,
                                image_type='Produktfoto',
                                is_front=True
                            ).update(is_primary=True)
            
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
        """Find matching product for the given article number and variant code."""
        if not article_number:
            return None
            
        # Try to find exact match first
        product = VariantProduct.objects.filter(sku=article_number).first()
        if product:
            self.stdout.write(f"    Found match by SKU: {article_number}")
            return product
            
        # Try to find parent product
        parent = ParentProduct.objects.filter(sku=article_number).first()
        if parent:
            if variant_code:
                # Try to find specific variant
                variant = VariantProduct.objects.filter(
                    parent=parent,
                    variant_code=variant_code
                ).first()
                if variant:
                    self.stdout.write(f"    Found variant {variant_code} under parent {article_number}")
                    return variant
            self.stdout.write(f"    Found parent product: {article_number}")
            return parent
            
        # Try prefix match for products with internal suffixes
        if '-' in article_number:
            base_sku = article_number.split('-')[0]
            product = VariantProduct.objects.filter(sku__startswith=base_sku).first()
            if product:
                self.stdout.write(f"    Found product by prefix match: {product.sku}")
                return product
        
        # Not found - just log and return None
        self.stdout.write(f"    No product found for article number: {article_number}")
        return None 