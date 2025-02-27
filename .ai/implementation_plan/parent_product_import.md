# Parent Product Import Implementation Plan

## Overview

This document outlines the implementation plan for importing parent product data from the Art_Kalkulation table in the legacy 4D system. This is Phase 2 of our product import strategy, following the successful import of product variants from the Artikel_Stamm table (Phase 1).

## Current Understanding

From our analysis of the legacy 4D system, we understand that:

1. The `Artikel_Stamm` table contains product variants with fields like:
   - ArtNr (e.g., "745020-BE") - the composite SKU
   - fk_ArtNr (e.g., "745020") - reference to the parent product
   - ArtikelArt (e.g., "BE") - the variant code
   - Various product attributes specific to variants

2. The `Art_Kalkulation` table contains parent products with:
   - Art_Nr - the parent product SKU (matches fk_ArtNr in variants)
   - Parent-level attributes shared across variants
   - Additional metadata about the product family

3. The relationship shows in data like:
   ```
   Artikel_Stamm.fk_ArtNr = "745020" -> Art_Kalkulation.Art_Nr = "745020"
   ```

## Objectives

1. Import parent product data from Art_Kalkulation
2. Establish proper parent-variant relationships
3. Enhance product categorization with full hierarchy
4. Ensure data consistency between parent and variant products

## Implementation Steps

### 1. Create Management Command

Create a new management command `import_parent_products` that:
- Fetches data from the Art_Kalkulation table
- Processes parent product records
- Associates them with existing variant products
- Handles edge cases (orphaned variants, duplicate parents)

```python
# Example command structure
class Command(BaseCommand):
    help = 'Import parent products from the legacy 4D system'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0)
        parser.add_argument('--update', action='store_true')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--debug', action='store_true')

    def handle(self, *args, **options):
        # Command implementation
        pass
```

### 2. Database Schema Updates (if needed)

Determine if any schema changes are needed to fully represent the parent-variant relationship. Potential changes:

- Add a ForeignKey from Product to a new ProductParent model
- Add additional fields needed for parent-specific attributes
- Ensure proper indexing for efficient querying

### 3. Data Mapping

Create comprehensive mapping between Art_Kalkulation fields and our data model:

| Art_Kalkulation Field | pyERP Field | Notes |
|-------------------|-------------|-------|
| Art_Nr | parent_sku | Primary identifier |
| Bezeichnung | name | Parent product name |
| Beschreibung | description | Complete description |
| Kategorie | category.parent | Parent category |
| ... | ... | ... |

### 4. Relationship Handling

Implement logic to handle the parent-variant relationship:

```python
# Pseudocode for relationship handling
def process_parent_product(parent_data):
    parent = create_or_update_parent(parent_data)
    variants = Product.objects.filter(base_sku=parent.sku)
    
    for variant in variants:
        associate_variant_with_parent(variant, parent)
        inherit_attributes_if_needed(variant, parent)
```

### 5. Category Enhancement

Use parent product data to enhance the category structure:

- Create proper category hierarchy
- Move products to the most specific applicable category
- Import category metadata (descriptions, images, etc.)

### 6. Attribute Inheritance Rules

Define rules for attribute inheritance between parent and variants:

- Which attributes should be inherited from parent to variant
- Which variant attributes override parent attributes
- How to handle conflicts
- Special rules for multilingual content

### 7. Testing Strategy

Develop a comprehensive testing strategy:

- Unit tests for the command and mapping logic
- Integration tests for the parent-variant relationship
- End-to-end tests for the complete import process
- Performance tests for large datasets

### 8. Rollout Plan

Plan for a staged rollout:

1. Develop and test with small dataset
2. Run in dry-run mode with full dataset
3. Import parent products to development environment
4. Verify data integrity and relationships
5. Perform in production with careful monitoring

## Timeline

- Week 1: Design and implementation of command structure
- Week 2: Implementation of data mapping and relationship handling
- Week 3: Testing and refinement
- Week 4: Rollout to production

## Resources Required

- Developer familiar with the product data model
- Access to Art_Kalkulation table schema and sample data
- Testing environment with product variants already imported
- Documentation of 4D system's product hierarchy model

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inconsistent data between Art_Kalkulation and Artikel_Stamm | Data integrity issues | Implement validation rules, log discrepancies for review |
| Missing parent records for some variants | Incomplete product hierarchy | Handle orphaned variants gracefully, create placeholder parents if needed |
| Performance issues with large datasets | Slow import process | Optimize queries, implement batch processing, consider asynchronous operation |
| Data loss during migration | Critical business impact | Ensure thorough testing, implement dry-run mode, maintain backups | 