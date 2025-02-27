# Management Commands

This directory contains management commands for the products app.

## Available Commands

### sync_product_images

Synchronizes product images from the external image database.

```bash
python manage.py sync_product_images [options]
```

#### Options

- `--dry-run`: Simulate the sync process without making changes to the database
- `--limit [N]`: Limit the number of API pages to process
- `--page-size [N]`: Number of API results to fetch per page (default: 100)
- `--force`: Force update all images even if they have been recently synced
- `--skip-pages [N]`: Skip this many pages before starting to process

#### Examples

Test synchronization without making changes:
```bash
python manage.py sync_product_images --dry-run
```

Synchronize a limited number of products:
```bash
python manage.py sync_product_images --limit 1 --page-size 10
```

Skip the first 5 pages and process the next 3:
```bash
python manage.py sync_product_images --skip-pages 5 --limit 3
```

#### Output

The command provides detailed output of the synchronization process:

```
Found 2489 total images across 249 pages
Processing page 1/1
  Checking article: 214808-BE (Number: 214808, Variant: BE)
    Found match by SKU: 214808
  Updated image for 214808: Illustration
  ...
Sync completed: 0 added, 24 updated, 21 products affected
```

#### Logs

The command also creates an `ImageSyncLog` record to track the synchronization history:

- Status of the sync (in_progress, completed, failed)
- When the sync started and completed
- Number of images added, updated, and deleted
- Number of products affected
- Error message if the sync failed

You can query these logs to track the synchronization history:

```python
from pyerp.products.models import ImageSyncLog
logs = ImageSyncLog.objects.all().order_by('-started_at')
```

### Other Commands

[Add documentation for other management commands here...] 