"""
Management command to synchronize product images from the external image database.  # noqa: E501

This command fetches images from the external API and creates/updates ProductImage  # noqa: E501
records in the local database, linking them to the appropriate products.
"""

import logging
import time
from typing import Any, Optional

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from tabulate import tabulate

from pyerp.products.image_api import ImageAPIClient
from pyerp.products.models import (
    ImageSyncLog,
    ParentProduct,
    ProductImage,
    VariantProduct,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize product images from the external image database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the sync process without making changes to the database",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of API pages to process",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=500,  # Increased default page size
            help="Number of API results to fetch per page",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force update all images by first deleting all existing images",
        )
        parser.add_argument(
            "--skip-pages",
            type=int,
            default=0,
            help="Skip this many pages before starting to process",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to process in each database batch",
        )

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        dry_run = options["dry_run"]
        limit = options["limit"]
        page_size = options["page_size"]
        force = options["force"]
        skip_pages = options["skip_pages"]
        batch_size = options["batch_size"]

        # Create sync log record (unless in dry-run mode)
        sync_log = None
        if not dry_run:
            sync_log = ImageSyncLog.objects.create(
                status="in_progress",
                started_at=timezone.now(),
            )

            # If force option is used, delete all existing images
            if force:
                self.stdout.write(
                    "Force option used - deleting all existing product images...",
                )
                try:
                    with transaction.atomic():
                        deleted_count = ProductImage.objects.all().delete()[0]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Deleted {deleted_count} existing product images",
                            ),
                        )
                        if sync_log:
                            sync_log.images_deleted = deleted_count
                            sync_log.save()
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error deleting existing images: {e!s}"),
                    )
                    if sync_log:
                        sync_log.status = "failed"
                        sync_log.error_message = (
                            f"Error deleting existing images: {e!s}"
                        )
                        sync_log.completed_at = timezone.now()
                        sync_log.save()
                    return

        try:
            images_added = 0
            images_updated = 0
            orphaned_images_added = 0
            orphaned_images_updated = 0
            products_affected = set()  # Use a set to count unique products

            # Initialize API client
            client = ImageAPIClient()

            # Store client as instance variable for use in helper methods
            self.client = client

            # Get API metadata to know total pages (with retries)
            max_retries = 3
            retry_delay = 5  # seconds

            for attempt in range(max_retries):
                try:
                    first_page = client._make_request(
                        "all-files-and-articles/",
                        params={"page": 1, "page_size": 1},
                    )
                    if first_page:
                        break
                    if attempt < max_retries - 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Failed to connect to API, retrying in {retry_delay} seconds...",
                            ),
                        )
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                "Failed to connect to API after multiple attempts",
                            ),
                        )
                        if not dry_run and sync_log:
                            sync_log.status = "failed"
                            sync_log.error_message = (
                                "Failed to connect to API after multiple attempts"
                            )
                            sync_log.completed_at = timezone.now()
                            sync_log.save()
                        return
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Error connecting to API: {e!s}, retrying in {retry_delay} seconds...",
                            ),
                        )
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error connecting to API after multiple attempts: {e!s}",
                            ),
                        )
                        if not dry_run and sync_log:
                            sync_log.status = "failed"
                            sync_log.error_message = f"Error connecting to API: {e!s}"
                            sync_log.completed_at = timezone.now()
                            sync_log.save()
                        return

            total_records = first_page.get("count", 0)
            total_pages = (total_records + page_size - 1) // page_size

            self.stdout.write(
                f"Found {total_records} total images across {total_pages} pages",
            )

            # Limit pages if requested
            if limit:
                total_pages = min(total_pages, skip_pages + limit)

            # Process each page
            for page in range(skip_pages + 1, total_pages + 1):
                self.stdout.write(f"Processing page {page}/{total_pages}")

                # Get page of results from API
                results = client.get_all_images(page=page, page_size=page_size)
                if not results or "results" not in results:
                    self.stdout.write(
                        self.style.WARNING(f"No results found on page {page}"),
                    )
                    continue

                # Lists to store bulk operations
                images_to_create = []
                images_to_update = []
                products_in_batch = set()

                # Process each image
                for image_data in results["results"]:
                    self.stdout.write("\nRaw image data:")
                    self.stdout.write(str(image_data))

                    # Parse the image data
                    parsed_image = client.parse_image(image_data)
                    if not parsed_image:
                        continue

                    # Print article numbers for debugging
                    articles = parsed_image.get("articles", [])
                    if articles:
                        self.stdout.write("\nFound articles in image:")
                        # Create table for display
                        article_table = [
                            [
                                article.get("article_number", "N/A"),
                                article.get("variant_code", "N/A"),
                                article.get("front", False),
                            ]
                            for article in articles
                        ]
                        self.stdout.write(
                            tabulate(
                                article_table,
                                headers=["Article", "Variant", "Front"],
                            )
                        )

                    # Flag to track if this image was associated with any product
                    image_associated_with_product = False

                    # Get associated articles
                    for article in parsed_image.get("articles", []):
                        article_number = article.get("article_number", "")
                        variant_code = article.get("variant_code", "")

                        # Find matching product
                        product = self._find_product(article_number, variant_code)
                        if not product:
                            continue

                        image_associated_with_product = True

                        if not dry_run:
                            existing_image = None
                            if hasattr(product, "images"):
                                existing_image = ProductImage.objects.filter(
                                    product=product,
                                    external_id=parsed_image["external_id"],
                                ).first()

                            # Prepare image instance
                            if existing_image:
                                existing_image.image_url = parsed_image["image_url"]
                                existing_image.thumbnail_url = parsed_image.get(
                                    "thumbnail_url",
                                )
                                existing_image.image_type = parsed_image["image_type"]
                                existing_image.is_front = parsed_image.get(
                                    "is_front",
                                    False,
                                )
                                images_to_update.append(existing_image)
                                images_updated += 1
                            else:
                                new_image = ProductImage(
                                    product=product,
                                    external_id=parsed_image["external_id"],
                                    image_url=parsed_image["image_url"],
                                    thumbnail_url=parsed_image.get("thumbnail_url"),
                                    image_type=parsed_image["image_type"],
                                    is_front=parsed_image.get("is_front", False),
                                )
                                images_to_create.append(new_image)
                                images_added += 1

                            products_in_batch.add(product.id)
                            products_affected.add(product.id)
                        else:
                            self.stdout.write(
                                f"  Would {'create' if not hasattr(product, 'images') or not product.images.filter(external_id=parsed_image['external_id']).exists() else 'update'} image for {product.sku}: {parsed_image['image_type']}",
                            )

                    # If the image wasn't associated with any product, save it without a product reference
                    if not image_associated_with_product and not dry_run:
                        existing_image = ProductImage.objects.filter(
                            product__isnull=True,
                            external_id=parsed_image["external_id"],
                        ).first()

                        if existing_image:
                            existing_image.image_url = parsed_image["image_url"]
                            existing_image.thumbnail_url = parsed_image.get(
                                "thumbnail_url",
                            )
                            existing_image.image_type = parsed_image["image_type"]
                            existing_image.is_front = parsed_image.get(
                                "is_front",
                                False,
                            )
                            images_to_update.append(existing_image)
                            orphaned_images_updated += 1
                            self.stdout.write(
                                f"  Updating orphaned image: {parsed_image['external_id']} ({parsed_image['image_type']})",
                            )
                        else:
                            new_image = ProductImage(
                                product=None,
                                external_id=parsed_image["external_id"],
                                image_url=parsed_image["image_url"],
                                thumbnail_url=parsed_image.get("thumbnail_url"),
                                image_type=parsed_image["image_type"],
                                is_front=parsed_image.get("is_front", False),
                            )
                            images_to_create.append(new_image)
                            orphaned_images_added += 1
                            self.stdout.write(
                                f"  Creating orphaned image: {parsed_image['external_id']} ({parsed_image['image_type']})",
                            )
                    elif not image_associated_with_product and dry_run:
                        self.stdout.write(
                            f"  Would create orphaned image: {parsed_image['external_id']} ({parsed_image['image_type']})",
                        )

                # Create table for display
                table_data = [
                    [
                        image.product.sku if image.product else "Orphaned",
                        image.image_type,
                        "Yes" if image.is_front else "No",
                        "Create" if image in images_to_create else "Update",
                    ]
                    for image in images_to_create + images_to_update
                ]

                if table_data:
                    self.stdout.write("\nResults for this page:")
                    self.stdout.write(
                        tabulate(
                            table_data,
                            headers=["SKU", "Image Type", "Is Front", "Action"],
                            tablefmt="grid",
                        ),
                    )
                    self.stdout.write("\n")

                # Create/update images individually instead of bulk operations
                if not dry_run and (images_to_create or images_to_update):
                    with transaction.atomic():
                        if images_to_create:
                            for image in images_to_create:
                                try:
                                    image.save()
                                except Exception as e:
                                    product_info = (
                                        f"product {image.product.sku}"
                                        if image.product
                                        else "orphaned image"
                                    )
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f"Error creating image for {product_info}: {e!s}",
                                        ),
                                    )
                                    logger.exception(
                                        f"Error creating product image for {product_info}",
                                    )
                                    continue

                        # Update existing images individually
                        if images_to_update:
                            for image in images_to_update:
                                try:
                                    existing_image = ProductImage.objects.get(
                                        id=image.id,
                                    )
                                    existing_image.image_url = image.image_url
                                    existing_image.thumbnail_url = image.thumbnail_url
                                    existing_image.image_type = image.image_type
                                    existing_image.is_front = image.is_front
                                    existing_image.save()
                                except Exception as e:
                                    product_info = (
                                        f"product {image.product.sku}"
                                        if image.product
                                        else "orphaned image"
                                    )
                                    self.stdout.write(
                                        self.style.ERROR(
                                            f"Error updating image {image.id} for {product_info}: {e!s}",
                                        ),
                                    )
                                    logger.exception(
                                        f"Error updating product image {image.id}",
                                    )
                                    continue

                        # Update primary flags for Produktfoto front images
                        if products_in_batch:
                            try:
                                ProductImage.objects.filter(
                                    product_id__in=products_in_batch,
                                ).update(is_primary=False)

                                # Then set primary for front Produktfotos
                                ProductImage.objects.filter(
                                    product_id__in=products_in_batch,
                                    image_type="Produktfoto",
                                    is_front=True,
                                ).update(is_primary=True)
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f"Error updating primary flags: {e!s}",
                                    ),
                                )
                                logger.exception(
                                    "Error updating primary flags for product images",
                                )
                                continue

            # Complete the sync log
            self.stdout.write(
                self.style.SUCCESS(
                    f"Sync completed: {images_added} added, {images_updated} updated, "
                    f"{orphaned_images_added} orphaned images added, {orphaned_images_updated} orphaned images updated, "
                    f"{len(products_affected)} products affected",
                ),
            )

            if not dry_run and sync_log:
                sync_log.status = "completed"
                sync_log.completed_at = timezone.now()
                sync_log.images_added = images_added + orphaned_images_added
                sync_log.images_updated = images_updated + orphaned_images_updated
                sync_log.products_affected = len(products_affected)
                sync_log.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during sync: {e!s}"))
            logger.exception("Error during product image sync")

            if not dry_run and sync_log:
                sync_log.status = "failed"
                sync_log.completed_at = timezone.now()
                sync_log.error_message = str(e)
                sync_log.save()

    def _find_product(self, article_number: str, variant_code: str) -> Optional[UnifiedProduct]:
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
                variant = VariantProduct.objects.filter(
                    parent=parent,
                    variant_code=variant_code,
                ).first()
                if variant:
                    self.stdout.write(
                        f"    Found variant {variant_code} under parent {article_number}",
                    )
                    return variant
            self.stdout.write(f"    Found parent product: {article_number}")
            return parent

        # Try prefix match for products with internal suffixes
        if "-" in article_number:
            base_sku = article_number.split("-")[0]
            product = VariantProduct.objects.filter(sku__startswith=base_sku).first()
            if product:
                self.stdout.write(f"    Found product by prefix match: {product.sku}")
                return product

        # Not found - just log and return None
        self.stdout.write(f"    No product found for article number: {article_number}")
        return None
