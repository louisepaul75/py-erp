# Product Import User Stories

## Overview
These user stories cover the import of product data from the legacy 4D system to the new pyERP system. The import process is divided into two phases:
1. Import of product variants from the Artikel_Stamm table
2. Import of parent products from the Art_Kalkulation table

## User Stories

### Phase 1: Product Variant Import (In Progress)

#### US-P101: Import Basic Product Variants
**As a** System Administrator
**I want to** import basic product variant data from the legacy 4D system Artikel_Stamm table
**So that** we can start using the new system with our existing product catalog

**Acceptance Criteria:**
- A management command exists to import products with appropriate options (limit, update, dry-run)
- Products are imported with correct SKUs, names, and basic attributes
- The command handles product variants by extracting base SKU and variant code
- Product variants are properly categorized based on ArtGruppe codes
- The import process logs successes, errors, and skipped records

#### US-P102: Map Complex Product Attributes
**As a** System Administrator
**I want to** map all relevant product attributes from the legacy system to the new system
**So that** all product information is preserved during migration

**Acceptance Criteria:**
- Price fields (list_price, wholesale_price, gross_price, cost_price) are correctly mapped
- Inventory fields (stock_quantity, min_stock_quantity, etc.) are imported
- Text fields like descriptions and keywords are preserved
- Special product flags (is_discontinued, has_bom, etc.) are correctly set
- Multi-language support (German/English) for product names and descriptions

#### US-P103: Incremental Product Updates
**As a** System Administrator
**I want to** update existing products with new data from the legacy system
**So that** changes made in the legacy system are reflected in the new system during transition

**Acceptance Criteria:**
- The import command has an update flag to update existing products
- Only changed fields are updated when the update flag is specified
- The system logs which products were updated and what fields changed
- The process can be run safely multiple times without creating duplicates

### Phase 2: Parent Product Import (Planned)

#### US-P201: Import Parent Product Data
**As a** System Administrator
**I want to** import parent product data from the Art_Kalkulation table
**So that** we have a complete product hierarchy in the new system

**Acceptance Criteria:**
- A management command exists to import parent products
- Parent products are imported with their basic attributes
- Parent products are correctly associated with their variants
- The import handles cases where variants exist but parents don't (and vice versa)

#### US-P202: Enhance Product Categorization
**As a** Product Manager
**I want to** have a complete product category hierarchy
**So that** products are properly organized and easy to find

**Acceptance Criteria:**
- Product categories from parent products enhance the placeholder categories
- Category hierarchy (parent-child relationships) is established
- Products are assigned to the most specific category applicable
- Category metadata (descriptions, images) is imported

#### US-P203: Consolidate Product Attributes
**As a** Product Manager
**I want to** intelligently merge attributes from parent and variant products
**So that** product data is consistent and complete

**Acceptance Criteria:**
- Shared attributes are inherited from parent to variants when appropriate
- Variant-specific attributes override parent attributes when both exist
- Conflicts between parent and variant data are logged for review
- Special handling for multilingual content to ensure completeness

## Technical Tasks

### Phase 1 Tasks (Current Focus)
- [x] Create basic import_products command structure
- [x] Add WSZ_API integration for fetching Artikel_Stamm data
- [x] Implement SKU parsing for base_sku and variant_code extraction
- [x] Add mapping for basic product attributes
- [x] Implement automatic category creation from ArtGruppe
- [x] Add debugging and logging functionality
- [x] Implement dry-run mode for safe testing
- [x] Add product creation and update functionality
- [ ] Improve error handling and recovery
- [ ] Add validation rules for imported data
- [ ] Create detailed import reports with statistics

### Phase 2 Tasks (Upcoming)
- [ ] Create import_parent_products command for Art_Kalkulation table
- [ ] Design parent-variant relationship handling
- [ ] Implement category hierarchy integration
- [ ] Develop attribute inheritance/override logic
- [ ] Create conflict resolution mechanisms
- [ ] Add validation for parent-variant consistency
- [ ] Implement full product relationship model
