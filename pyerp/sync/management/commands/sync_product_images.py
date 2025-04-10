"""
Management command to synchronize product images from the external CMS.
"""
from django.core.management.base import CommandError
from django.utils import timezone
from django.db import transaction

from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.external_api import connection_manager
from pyerp.external_api.images_cms.extractors import ImageApiExtractor
from pyerp.external_api.images_cms.transformers import ImageTransformer
from pyerp.external_api.images_cms.loaders import ProductImageLoader
from pyerp.business_modules.products.models import ImageSyncLog
from pyerp.sync.management.commands.base_sync_command import BaseSyncCommand

import os
import json
import requests
import time
from urllib.parse import urlparse


class Command(BaseSyncCommand):
    """Command to sync product images from the external CMS."""

    help = "Synchronize product images from the external CMS"
    entity_type = "product_images"

    def add_arguments(self, parser):
        """Add command line arguments."""
        # Add base sync arguments first
        super().add_arguments(parser)

        # Add command-specific arguments
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
        """Execute the command."""
        self.stdout.write("Starting product image synchronization...")
        
        dry_run = options.get("dry_run", False)
        product_id = options.get("product_id")
        force = options.get("force_update", False)  # Using base command's force flag
        debug = options.get("debug", False)
        download = options.get("download", False)
        preferred_format = options.get("format", "jpg_k")
        pause_duration = options.get("pause", 0.5)
        batch_size = options.get("batch_size", 100)
        
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
            
            # Build query parameters using base command's method
            query_params = self.build_query_params(options)
            
            # Add product_id to query params if specified
            if product_id:
                query_params['product_id'] = product_id
                self.stdout.write(f"Syncing images for product ID: {product_id}")
            
            # Extract data with pagination
            current_page = 1
            has_more_pages = True
            all_transformed_data = []
            
            while has_more_pages:
                # Add pagination parameters to query
                page_params = {
                    **query_params,
                    'page': current_page,
                    'page_size': batch_size
                }
                
                # Extract data for this page
                source_data = extractor.extract(query_params=page_params)
                
                # Check if we have more pages
                has_more_pages = len(source_data) > 0 and (
                    not options.get("top") or 
                    total_processed < options.get("top")
                )
                
                if source_data:
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
                time.sleep(pause_duration)
                
                # Check if we've hit the --top limit
                if options.get("top") and total_processed >= options.get("top"):
                    self.stdout.write(self.style.SUCCESS(f"Reached --top limit of {options['top']} records"))
                    break
            
            # Handle downloads if requested
            if download and all_transformed_data:
                self._download_images(all_transformed_data, preferred_format, debug)
            
            # Update sync log
            if sync_log:
                sync_log.status = "completed"
                sync_log.completed_at = timezone.now()
                sync_log.total_processed = total_processed
                sync_log.total_created = total_created
                sync_log.total_updated = total_updated
                sync_log.total_skipped = total_skipped
                sync_log.total_errors = total_errors
                sync_log.save()
            
            # Final summary
            self.stdout.write(self.style.SUCCESS(
                f"\nSync completed successfully:\n"
                f"Total processed: {total_processed}\n"
                f"Created: {total_created}\n"
                f"Updated: {total_updated}\n"
                f"Skipped: {total_skipped}\n"
                f"Errors: {total_errors}"
            ))
            
            # Return None instead of True to avoid boolean being passed to stdout.write()
            
        except Exception as e:
            error_msg = f"Error during product image sync: {str(e)}"
            self.stderr.write(self.style.ERROR(error_msg))
            if debug:
                import traceback
                traceback.print_exc()
            
            # Update sync log on error
            if sync_log:
                sync_log.status = "failed"
                sync_log.completed_at = timezone.now()
                sync_log.error_message = error_msg
                sync_log.save()
            
            raise CommandError(error_msg)

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