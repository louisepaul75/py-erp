# Product Image Synchronization

This document describes the product image synchronization feature that connects the ERP system with an external image database.

## Overview

The product image synchronization feature allows you to fetch and store product images from an external image database API. It creates and updates `ProductImage` records in the local database, linking them to the appropriate products based on their SKUs.

## Models

The feature uses the following models:

### ProductImage

Stores information about product images:

- `product`: The product associated with this image
- `external_id`: Unique identifier from the external system
- `image_url`: URL to the full-size image
- `thumbnail_url`: URL to the thumbnail version
- `image_type`: Type of image (e.g., "Produktfoto", "Markt-Messe-Shop", "Szene", "Illustration")
- `is_primary`: Whether this is the primary image for the product
- `is_front`: Whether this image is marked as a front view
- `priority`: Numeric priority value for sorting
- `alt_text`: Alternative text for the image
- `metadata`: JSON field for additional metadata

### ImageSyncLog

Tracks the history and results of image synchronization runs:

- `status`: Current status of the sync (in_progress, completed, failed)
- `started_at`: When the sync was started
- `completed_at`: When the sync was completed
- `images_added`: Number of new images added
- `images_updated`: Number of existing images updated
- `images_deleted`: Number of images deleted
- `products_affected`: Number of products affected
- `error_message`: Error message if the sync failed

## Management Command

The feature includes a management command `sync_product_images` that synchronizes images from the external API.

### Basic Usage

```bash
python manage.py sync_product_images
```

This will synchronize all product images from the external API.

### Command Options

- `--dry-run`: Simulate the sync process without making changes to the database
- `--limit [N]`: Limit the number of API pages to process
- `--page-size [N]`: Number of API results to fetch per page (default: 500)
- `--force`: Force update all images even if they have been recently synced
- `--skip-pages [N]`: Skip this many pages before starting to process
- `--batch-size [N]`: Number of records to process in each database batch (default: 1000)

### Examples

**Test synchronization without making changes:**
```bash
python manage.py sync_product_images --dry-run
```

**Synchronize a limited number of products:**
```bash
python manage.py sync_product_images --limit 1 --page-size 10
```

**Skip the first 5 pages and process the next 3:**
```bash
python manage.py sync_product_images --skip-pages 5 --limit 3
```

## Product Matching Logic

The synchronization process matches products in the external API with products in the local database using the following logic:

1. It extracts the article number and variant code from the API response
2. It attempts to find the product through multiple matching strategies:
   - First tries to find a product with the exact article number as its SKU (ignoring the variant code)
   - If not found, it tries to find a parent product with that SKU
   - If this is a parent product and we have a variant code, it tries to find the specific variant
   - As a last resort, it tries a prefix match for SKUs with internal suffixes
3. Once a product is found, the image is created or updated
4. If no product is found after all attempts, the image is skipped

This improved matching algorithm handles various SKU formats and ensures that images are matched to products even when:
- The SKU formats differ slightly between systems
- Articles come with suffix codes like "-BE" in the external system
- The product exists as a variant under a parent

## Synchronization Process

The synchronization process follows these steps:

1. Create a sync log record to track the progress and results
2. Fetch the total number of images from the API
3. Process each page of results from the API
4. For each image:
   - Extract the associated articles (products)
   - For each article, find the matching product in the local database
   - Create or update the `ProductImage` record for the product
   - Set the image as primary if it's the first one or marked as front
5. Track the number of images added, updated, and products affected
6. Update the sync log with the results

### Individual Record Processing

The sync process uses individual record creation and updates rather than bulk operations to ensure proper ID generation:

1. For new images:
   - Each image is saved individually using `image.save()`
   - This allows Django's ORM to handle ID generation correctly
   - Error handling is implemented to catch and log any issues with individual records

2. For existing images:
   - Each image is retrieved from the database and updated individually
   - Changes are saved with `image.save()` rather than bulk updates
   - This approach ensures proper database sequence usage

3. Primary flag updates:
   - After processing individual images, primary flags are updated
   - First, all primary flags are reset for affected products
   - Then, primary flags are set for front Produktfotos

This approach ensures database integrity and proper ID sequence usage, preventing potential ID conflicts that could occur with bulk operations.

## Logging

The synchronization process logs detailed information to help with troubleshooting:

- Which products are being checked
- Whether matches are found by SKU or other methods
- Which images are added or updated
- Any errors that occur during the process

## Running via Script

You can also run the synchronization via a Python script:

```python
import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

from django.core.management import call_command

# Call the management command with options
call_command('sync_product_images', limit=1, page_size=10)
```

## Best Practices

- Run with `--dry-run` first to test before making actual changes
- Use the `--limit` option when testing to avoid processing too many images
- Check the sync logs after each run to verify the results
- Schedule regular synchronization to keep images up to date
- Consider using smaller page sizes (10-20) for more frequent updates
- Use larger page sizes (100-500) for initial synchronization or full refreshes
- Monitor database performance during large sync operations
- Review error logs for any issues with individual image processing
