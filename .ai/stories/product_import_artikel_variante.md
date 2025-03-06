# Product Import from Artikel_Variante

## Overview

This story covers the implementation of importing product data from the legacy 4D system's `Artikel_Variante` table, which contains all product information including variants. The implementation focuses on correctly extracting product information, establishing parent-child relationships for variants, and handling complex data structures like pricing information.

## Business Context

The legacy 4D system has evolved its product data structure over time. Initially, products were stored in the `Artikel_Stamm` table, but the system later transitioned to using `Artikel_Variante` as the primary product table. This table contains all product data, including variant information, pricing details, and relationships to other entities like product families and categories.

To ensure a successful migration, we need to:
1. Import all products from `Artikel_Variante`
2. Correctly extract SKUs and identify variant relationships
3. Parse complex data structures (pricing, categories, tags)
4. Create appropriate parent-child relationships for variants
5. Ensure data quality and consistency during import

## Implementation Status

### Completed

- [x] Updated `import_products` management command to source data from `Artikel_Variante` instead of `Artikel_Stamm`
- [x] Implemented SKU parsing to extract base SKUs and variant codes
- [x] Added support for parsing complex pricing structure from the `Preise` field
- [x] Created functionality to automatically identify and create parent products for variants
- [x] Implemented dry-run capability for safe testing
- [x] Added detailed error reporting and logging
- [x] Added option to limit the number of products processed for testing
- [x] Implemented proper linking of variants to their parent products
- [x] Added debug output for troubleshooting
- [x] Implemented exception handling for robust error recovery
- [x] Successfully imported parent products from Artikel_Familie (1,571 products created)
- [x] Successfully updated parent-child relationships for 4,078 variant products
- [x] Executed variant import with dry-run mode to verify data

### In Progress

- [ ] Complete full variant import to create all variants in the database
- [ ] Enhance product categorization based on `Familie_` field and legacy categories
- [ ] Extract additional product attributes (dimensions, weights, descriptions)
- [ ] Import product tags and properties from related entities
- [ ] Implement data quality validation checks

### Future Tasks

- [ ] Add incremental sync capability for ongoing updates from legacy system
- [ ] Implement full-text search indexing for improved product discovery
- [ ] Create data quality reports to identify potential issues in imported data
- [ ] Enhance import performance for large datasets
- [ ] Add support for importing product images and related media

## Technical Details

### Command Line Usage

The updated product import commands can be used with the following options:

```bash
# Import parent products from Artikel_Familie
python import_artikel_familie_as_parents.py [options]

# Update parent-child relationships
python import_artikel_familie_as_parents.py --update-relationships

# Import product variants from Artikel_Variante
python manage.py import_artikel_variante [options]
```

Options:
- `--limit N`: Limit import to N products (useful for testing)
- `--update`: Update existing products (if they already exist in the database)
- `--dry-run`: Simulate the import without making changes to the database
- `--debug`: Enable verbose debug output

### Migration Results

1. **Parent Product Import**: Successfully created 1,571 parent products from Artikel_Familie
   - Some products had missing description fields (219 errors)
   - Example parent products created:
     - 'Bosch Green Akku für Tacker' (SKU: 915530)
     - 'Bosch Green Akku Tacker' (SKU: 128052)
     - 'Straßenlaterne' (SKU: 503011)

2. **Parent-Child Relationship Update**: Successfully linked 4,078 variant products to their parents
   - Examples of successful links:
     - Variant 'Straßenlaterne' (SKU: 3411-BL) linked to parent 'Straßenlaterne' (SKU: 503011)
     - Variant 'Tanne schmal im Winter' (SKU: 4108W-BE) linked to parent 'Tanne schmal im Winter' (SKU: 128609)
     - Variant 'Bücherwurm' (SKU: 9305BUE-BE) linked to parent 'Bücherwurm' (SKU: 102867)

### Data Parsing

The implementation handles several complex data structures:

1. **SKU Parsing**: Products with SKUs like "11400-BE" are split into base SKU "11400" and variant code "BE"
2. **Price Structure**: The `Preise` field contains multiple price types in a nested structure:
   ```json
   {
     "Coll": [
       {"Art": "Laden", "Preis": 39.5, "VE": 1},
       {"Art": "Handel", "Preis": 17.8, "VE": 1},
       {"Art": "Empf.", "Preis": 34.5, "VE": 1},
       {"Art": "Einkauf", "Preis": 6.6, "VE": 1}
     ]
   }
   ```
3. **Parent-Child Relationships**: Products with the same base SKU are grouped, with a parent product created automatically

### Key Functions

- `extract_product_data()`: Extracts and transforms product data from Artikel_Variante rows
- `create_parent_products()`: Creates parent products for variants with the same base SKU
- `get_value()`: Safely retrieves values from different row formats (pandas Series or dictionary)

## Next Steps Recommendations

1. **Category Mapping**: Implement mapping from `Familie_` field to product categories
2. **Additional Attributes**: Extract and import dimensions, weights, descriptions, and other metadata
3. **Incremental Updates**: Add capability to only import changes since the last import
4. **Data Quality**: Implement validation rules to ensure imported data meets quality standards
5. **Performance Optimization**: Improve import speed for large datasets using bulk operations

## Related Documentation

- [Product Requirements Document - Section 4.6.1](../.ai/prd.md#461-product-data-migration-strategy)
- [Product Model Documentation](../pyerp/products/models.py)
- [Legacy Data API Documentation](../scripts/analyze_artikel_variante.py)
