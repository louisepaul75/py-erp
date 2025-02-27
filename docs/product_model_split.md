# Product Model Split

## Overview

This document describes the migration from a single `Product` model to separate `ParentProduct` and `VariantProduct` models in the pyERP system. This change improves the data model by creating a clearer separation between parent products (product families) and their variants.

## Motivation

The original design used a single `Product` model with an `is_parent` flag and a self-referential `parent` field to distinguish between parent products and variants. While this approach worked, it had several limitations:

1. **Schema Confusion**: Having both parent and variant fields in the same model made the schema less clear.
2. **Validation Challenges**: It was difficult to enforce validation rules specific to parents or variants.
3. **Query Complexity**: Queries often needed to filter by `is_parent` to get the correct set of products.
4. **UI/UX Issues**: Admin interfaces and forms had to handle conditional fields based on the product type.

## New Model Structure

### BaseProduct (Abstract)

An abstract base class that contains all common fields for both parent and variant products:

- Basic identification (sku, legacy_id)
- Names and descriptions
- Physical attributes
- Pricing
- Inventory
- Sales statistics
- Status flags
- Manufacturing flags
- Product-specific flags
- Timestamps
- Category

### ParentProduct

Extends `BaseProduct` and adds:

- `base_sku`: The base SKU for all variants in this family

### VariantProduct

Extends `BaseProduct` and adds:

- `parent`: ForeignKey to ParentProduct
- `variant_code`: The variant identifier
- `legacy_sku`: The legacy SKU from the old system
- `base_sku`: The base SKU without variant (for reference)

## Migration Process

The migration process involves:

1. Creating the new model structure
2. Creating database tables for the new models
3. Migrating data from the old `Product` model to the new models
4. Updating import scripts to work with the new model structure

### Migration Steps

1. **Create New Models**: Define `BaseProduct`, `ParentProduct`, and `VariantProduct` in `models.py`.
2. **Create Migration Files**: Generate migration files to create the new tables.
3. **Data Migration**: Create a data migration script to move data from the old `Product` model to the new models.
4. **Update Import Scripts**: Update the import scripts to work with the new model structure.

### Migration Command

A management command `migrate_to_split_models` has been created to facilitate the migration:

```bash
python manage.py migrate_to_split_models [--dry-run] [--limit N] [--skip-existing]
```

Options:
- `--dry-run`: Perform a dry run without saving to the database
- `--limit N`: Limit the number of products to migrate
- `--skip-existing`: Skip products that already exist in the new models

## Import Commands

The import commands have been updated to work with the new model structure:

### Import Parent Products

```bash
python manage.py import_artikel_familie [--dry-run] [--limit N] [--skip-existing]
```

### Import Variant Products

```bash
python manage.py import_artikel_variante [--dry-run] [--limit N] [--skip-existing]
```

## Admin Interface

The admin interface has been updated to provide separate admin classes for `ParentProduct` and `VariantProduct`, with appropriate fieldsets and inline editing of variants from the parent product admin.

## Backward Compatibility

The original `Product` model is kept for backward compatibility during the migration process. Once all code has been updated to use the new models, the old model can be deprecated and eventually removed. 

## Migration Results

The migration from the single `Product` model to the split `ParentProduct` and `VariantProduct` models has been completed with the following results:

### Migration Statistics
- **Parent Products**: 1,564 parent products successfully migrated (100% completion)
- **Variant Products**: 3,726 variant products successfully migrated (86.27% completion)
- **Missing Variants**: Approximately 14% of variants could not be migrated because their parent products were not found

### Relationship Analysis
- 1,564 total parent products
- 275 parents have no variants (17.6%)
- 1,289 parents have at least one variant (82.4%)
- Average of 2.38 variants per parent product

### Top Parents by Variant Count
The migration identified parents with the most variants:
1. "Monatsbilder sortiert" (SKU: 9410) - 45 variants
2. "Fensterbild/Monate sortiert" (SKU: 9310) - 42 variants
3. "Trachtenmusiker" (SKU: TM) - 21 variants
4. "Filigraneier mit Figürchen" (SKU: 12460) - 18 variants
5. "Glücksbringer Kette" (SKU: 13220) - 16 variants

## Known Issues

### SKU and Legacy ID Mapping Issues

During the initial migration, an issue was identified where the SKU and legacy_id fields were incorrectly mapped in the parent product table. Specifically:

- The `sku` field contained values that should be in the `legacy_id` field (e.g., "1541", "1607")
- The `legacy_id` field contained values that should be in the `sku` field (e.g., "11201", "11202")

This mapping issue affects the parent-variant relationships, as variants typically reference their parent's SKU.

### Fixing Data Issues

To address these issues, two management commands have been created:

#### 1. Fix Parent SKU Mapping

The `fix_parent_sku_mapping` command corrects the SKU and legacy_id fields in the parent product table:

```bash
python manage.py fix_parent_sku_mapping [--dry-run] [--limit N]
```

Options:
- `--dry-run`: Perform a dry run without saving changes to the database
- `--limit N`: Limit the number of parents to process

This command:
1. Identifies parent products where the SKU and legacy_id appear to be swapped
2. Swaps the values to correct the mapping
3. Updates the `base_sku` field to match the corrected SKU
4. Provides detailed logging of changes made

#### 2. Fix Variant-Parent Relationships

After correcting the parent SKU mappings, the `fix_variant_parent_relationships` command updates the relationships between variants and their parents:

```bash
python manage.py fix_variant_parent_relationships [--dry-run] [--limit N] [--orphans-only]
```

Options:
- `--dry-run`: Perform a dry run without saving changes to the database
- `--limit N`: Limit the number of variants to process
- `--orphans-only`: Only process variants without a parent

This command:
1. Extracts the parent SKU from each variant's SKU using pattern matching
2. Finds the corresponding parent product using the corrected SKU
3. Updates the variant's parent relationship
4. Provides detailed logging of changes made

### Recommended Workflow for Data Correction

To fix the data issues, follow this workflow:

1. Run a dry run of the parent SKU mapping fix:
   ```bash
   python manage.py fix_parent_sku_mapping --dry-run
   ```

2. If the results look correct, apply the changes:
   ```bash
   python manage.py fix_parent_sku_mapping
   ```

3. Run a dry run of the variant-parent relationship fix:
   ```bash
   python manage.py fix_variant_parent_relationships --dry-run
   ```

4. If the results look correct, apply the changes:
   ```bash
   python manage.py fix_variant_parent_relationships
   ```

5. For any remaining orphaned variants, use the `fix_missing_variants` command:
   ```bash
   python manage.py fix_missing_variants --create-parents
   ```

6. Verify the changes with the test script:
   ```bash
   python test_product_split.py
   ```

## Conclusion

The product model split has been successfully implemented, with most products migrated to the new structure. The new model provides a clearer separation between parent products and variants, making the data model more intuitive and easier to work with. The remaining issues with missing parent products should be addressed to complete the migration process. 