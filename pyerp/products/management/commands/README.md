# Management Commands

This directory contains management commands for the products app.

## Available Commands

### import_artikel_familie.py

Imports parent products from the Artikel_Familie table in the legacy 4D system.

```bash
python manage.py import_artikel_familie [options]
```

#### Options

- `--dry-run`: Simulate the import process without making changes to the database
- `--limit [N]`: Limit the number of records to import
- `--update-relationships`: Only update parent-child relationships, don't import new records

#### Examples

Test import without making changes:
```bash
python manage.py import_artikel_familie --dry-run
```

Import a limited number of parent products:
```bash
python manage.py import_artikel_familie --limit 10
```

Update parent-child relationships only:
```bash
python manage.py import_artikel_familie --update-relationships
```

### import_artikel_variante.py

Imports variant products from the Artikel_Variante table in the legacy 4D system.

```bash
python manage.py import_artikel_variante [options]
```

#### Options

- `--dry-run`: Simulate the import process without making changes to the database
- `--limit [N]`: Limit the number of records to import
- `--skip [N]`: Skip the first N records
- `--force`: Force update existing records

#### Examples

Test import without making changes:
```bash
python manage.py import_artikel_variante --dry-run
```

Import a limited number of variants:
```bash
python manage.py import_artikel_variante --limit 10
```

Skip the first 100 records and import the next 50:
```bash
python manage.py import_artikel_variante --skip 100 --limit 50
```

### link_variants_to_existing_parents.py

Establishes parent-child relationships between VariantProduct and ParentProduct records.

```bash
python manage.py link_variants_to_existing_parents [options]
```

#### Options

- `--dry-run`: Simulate the process without making changes to the database
- `--limit [N]`: Limit the number of records to process

#### Examples

Link variants to parents without making changes:
```bash
python manage.py link_variants_to_existing_parents --dry-run
```

### fix_variant_parent_relationships.py

Fixes incorrect parent-child relationships between variants and parents.

```bash
python manage.py fix_variant_parent_relationships [options]
```

#### Options

- `--dry-run`: Simulate the process without making changes to the database
- `--limit [N]`: Limit the number of records to process

### fix_missing_variants.py

Identifies and fixes orphaned variant products without parents.

```bash
python manage.py fix_missing_variants [options]
```

#### Options

- `--dry-run`: Simulate the process without making changes to the database
- `--create-placeholders`: Create placeholder parent products for orphaned variants

### create_placeholder_parents.py

Creates placeholder parent products for variants without parents.

```bash
python manage.py create_placeholder_parents [options]
```

#### Options

- `--dry-run`: Simulate the process without making changes to the database
- `--limit [N]`: Limit the number of records to process

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

### Development/Testing Commands

These commands are primarily for development and testing purposes:

#### wipe_and_reload_parents.py

Wipes and reloads all parent products. Use with caution!

```bash
python manage.py wipe_and_reload_parents [options]
```

#### wipe_and_reload_variants.py

Wipes and reloads all variant products. Use with caution!

```bash
python manage.py wipe_and_reload_variants [options]
```

#### migrate_to_split_models.py

Migrates data from the legacy Product model to the split ParentProduct and VariantProduct models.

```bash
python manage.py migrate_to_split_models [options]
```

#### Options

- `--dry-run`: Simulate the process without making changes to the database
- `--limit [N]`: Limit the number of records to process
