"""
Management command to synchronize product images from the external CMS.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.external_api import connection_manager
from pyerp.external_api.images_cms.extractors import ImageApiExtractor
from pyerp.external_api.images_cms.transformers import ImageTransformer
from pyerp.external_api.images_cms.loaders import ProductImageLoader
from pyerp.business_modules.products.models import ImageSyncLog

import os
import json
import requests
import time
from urllib.parse import urlparse


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
            "--start-page",
            type=int,
            default=1,
            help="Starting page number for API requests (default: 1)",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=100,
            help="Number of items per page (default: 100)",
        )
        parser.add_argument(
            "--limit-pages",
            type=int,
            default=0,
            help="Maximum number of pages to process (default: 0 = all pages)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force connection even if it's disabled in the system",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print detailed debug information about API responses",
        )
        parser.add_argument(
            "--download",
            action="store_true",
            help="Download images to local media directory",
        )
        parser.add_argument(
            "--format",
            type=str,
            default="jpg_k",
            choices=["jpg_k", "jpg_g", "png", "tiff", "psd"],
            help="Preferred image format to sync (default: jpg_k)",
        )
        parser.add_argument(
            "--pause",
            type=float,
            default=0.5,
            help="Pause between API requests in seconds (default: 0.5)",
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting product image synchronization...")
        
        dry_run = options.get("dry_run", False)
        product_id = options.get("product_id")
        start_page = options.get("start-page", 1)
        page_size = options.get("page_size", 100)
        limit_pages = options.get("limit_pages", 0)
        force = options.get("force", False)
        debug = options.get("debug", False)
        download = options.get("download", False)
        preferred_format = options.get("format", "jpg_k")
        pause_duration = options.get("pause", 0.5)
        
        # Initialize counters for total processing
        total_processed = 0
        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_errors = 0
        
        # Create a sync log record to track progress
        sync_log = None
        if not dry_run:
            sync_log = ImageSyncLog.objects.create(
                status="in_progress",
                started_at=timezone.now()
            )
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE: No changes will be made"))
        
        if debug:
            self.stdout.write(self.style.WARNING("DEBUG MODE: Detailed information will be printed"))
            
        if download:
            self.stdout.write(self.style.WARNING(f"DOWNLOAD MODE: Images will be downloaded in {preferred_format} format"))
        
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
            
            # Create the pipeline components
            extractor = ImageApiExtractor(config={})
            transformer = ImageTransformer(config={})
            loader = ProductImageLoader(config={})
            
            # Connect to the API to get total records
            extractor.connect()
            
            # Process specific product if requested
            if product_id:
                self.stdout.write(f"Syncing images for product ID: {product_id}")
                query_params = {'product_id': product_id}
                
                # Get data for the specific product
                source_data = extractor.extract(query_params=query_params)
                self.stdout.write(self.style.SUCCESS(f"Extracted {len(source_data)} images for product {product_id}"))
                
                # Transform the data
                transformed_data = transformer.transform(source_data)
                self.stdout.write(self.style.SUCCESS(f"Transformed {len(transformed_data)} images"))
                
                # Load if not in dry run
                if not dry_run and transformed_data:
                    result = loader.load(transformed_data, update_existing=True)
                    
                    # Update counters
                    total_processed += len(transformed_data)
                    total_created += result.get('created', 0)
                    total_updated += result.get('updated', 0)
                    total_skipped += result.get('skipped', 0)
                    total_errors += result.get('errors', 0)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Processed {len(transformed_data)} images: "
                        f"{result.get('created', 0)} created, "
                        f"{result.get('updated', 0)} updated, "
                        f"{result.get('skipped', 0)} skipped, "
                        f"{result.get('errors', 0)} errors"
                    ))
                    
                    # Handle downloads if requested
                    if download:
                        self._download_images(transformed_data, preferred_format, debug)
            else:
                # Process all pages (or limited by limit_pages)
                current_page = start_page
                has_more_pages = True
                all_transformed_data = []
                
                # Get initial page to determine total count
                initial_query = {
                    'page': 1,
                    'page_size': 1
                }
                initial_response = extractor.extract(query_params=initial_query)
                
                total_items = extractor.total_count if hasattr(extractor, 'total_count') else 0
                total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
                
                # Apply limit if specified
                if limit_pages > 0:
                    max_pages = min(total_pages, start_page + limit_pages - 1) if total_pages > 0 else limit_pages
                    self.stdout.write(f"Processing {min(limit_pages, max_pages)} pages out of {total_pages} total pages")
                else:
                    max_pages = total_pages if total_pages > 0 else float('inf')
                    self.stdout.write(f"Processing all {total_pages} pages")
                
                # Process each page
                while has_more_pages and current_page <= max_pages:
                    self.stdout.write(f"Processing page {current_page} of {max_pages if max_pages != float('inf') else 'unknown'}")
                    
                    # Set up query parameters for this page
                    query_params = {
                        'page': current_page,
                        'page_size': page_size
                    }
                    
                    # Extract data for this page
                    source_data = extractor.extract(query_params=query_params)
                    
                    # Check if we have more pages
                    has_more_pages = len(source_data) > 0
                    
                    if has_more_pages:
                        self.stdout.write(self.style.SUCCESS(f"Page {current_page}: Extracted {len(source_data)} images"))
                        
                        # Transform the data
                        transformed_data = transformer.transform(source_data)
                        self.stdout.write(self.style.SUCCESS(f"Page {current_page}: Transformed {len(transformed_data)} images"))
                        
                        # Store transformed data for potential download
                        if download:
                            all_transformed_data.extend(transformed_data)
                        
                        # Load if not in dry run
                        if not dry_run and transformed_data:
                            result = loader.load(transformed_data, update_existing=True)
                            
                            # Update counters
                            total_processed += len(transformed_data)
                            total_created += result.get('created', 0)
                            total_updated += result.get('updated', 0)
                            total_skipped += result.get('skipped', 0)
                            total_errors += result.get('errors', 0)
                            
                            self.stdout.write(self.style.SUCCESS(
                                f"Page {current_page}: Processed {len(transformed_data)} images: "
                                f"{result.get('created', 0)} created, "
                                f"{result.get('updated', 0)} updated, "
                                f"{result.get('skipped', 0)} skipped, "
                                f"{result.get('errors', 0)} errors"
                            ))
                    
                    # Move to next page
                    current_page += 1
                    
                    # Pause between API requests to avoid overloading the server
                    if has_more_pages and current_page <= max_pages:
                        time.sleep(pause_duration)
                
                # Download images if requested and not in dry run
                if download and not dry_run and all_transformed_data:
                    downloaded_count = self._download_images(all_transformed_data, preferred_format, debug)
                    self.stdout.write(self.style.SUCCESS(f"Downloaded {downloaded_count} images"))
            
            # Clean up the connection
            try:
                extractor.close()
            except Exception as e:
                if debug:
                    self.stdout.write(self.style.WARNING(f"Error closing connection: {e}"))
            
            # Update sync log with results
            if sync_log:
                sync_log.status = "completed"
                sync_log.completed_at = timezone.now()
                sync_log.images_added = total_created
                sync_log.images_updated = total_updated
                sync_log.products_affected = 0  # We're not tracking this accurately across pages
                sync_log.save()
            
            # Final summary
            self.stdout.write(self.style.SUCCESS(
                f"Image synchronization completed successfully: "
                f"{total_processed} processed, "
                f"{total_created} created, "
                f"{total_updated} updated, "
                f"{total_skipped} skipped, "
                f"{total_errors} errors"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during synchronization: {e}"))
            
            # Update sync log with error
            if sync_log:
                sync_log.status = "failed"
                sync_log.completed_at = timezone.now()
                sync_log.error_message = str(e)
                sync_log.save()
    
    def _download_images(self, transformed_data, preferred_format, debug=False):
        """Download images from transformed data."""
        downloaded_count = 0
        
        # Create the media directory if it doesn't exist
        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', os.path.join(os.getcwd(), 'media'))
        images_dir = os.path.join(media_root, 'product_images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Process each transformed record
        for record in transformed_data:
            try:
                # Get image URL
                image_url = record.get('image_url')
                if not image_url:
                    continue
                
                # Get external ID for filename
                external_id = record.get('external_id', 'unknown')
                
                # Create a sanitized filename
                extension = self._get_extension_from_format(preferred_format)
                filename = f"product_{external_id}.{extension}"
                filepath = os.path.join(images_dir, filename)
                
                if debug:
                    self.stdout.write(f"Downloading {image_url} to {filepath}")
                
                # Skip if file already exists (to avoid unnecessary downloads)
                if os.path.exists(filepath):
                    if debug:
                        self.stdout.write(f"File already exists: {filepath}")
                    downloaded_count += 1
                    continue
                
                # Download the image
                response = requests.get(image_url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    downloaded_count += 1
                    if debug:
                        self.stdout.write(self.style.SUCCESS(f"Downloaded to {filepath}"))
            except Exception as e:
                if debug:
                    self.stdout.write(self.style.ERROR(f"Download error: {e}"))
        
        return downloaded_count
    
    def _get_extension_from_format(self, format_type):
        """Get file extension based on format type."""
        format_map = {
            'jpg_k': 'jpg',
            'jpg_g': 'jpg',
            'png': 'png',
            'tiff': 'tif',
            'psd': 'psd'
        }
        return format_map.get(format_type, 'jpg') 