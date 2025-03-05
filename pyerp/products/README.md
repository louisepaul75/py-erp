# Products App

This Django app provides product management functionality for the pyERP system.

## Features

- Product catalog management
- Product categorization
- Product image management via external API integration
- Parent-variant product hierarchy management
- Import products from legacy 4D system (Artikel_Familie and Artikel_Variante)
- Advanced product search and filtering

## Models

### BaseProduct (Abstract)

Abstract base class with common product fields:

- Basic identification (SKU, legacy IDs)
- Multilingual names and descriptions
- Physical attributes (dimensions, weight)
- Pricing (list price, wholesale price, gross price, cost price)
- Inventory tracking (stock quantity, backorder quantity)
- Sales statistics (units sold, revenue)
- Status flags (active, discontinued)
- Timestamps (created, updated)

### ParentProduct

Model for parent products (product families):

- All fields from BaseProduct
- Base SKU for variants
- Placeholder flag

### VariantProduct

Model for variant products:

- All fields from BaseProduct
- Reference to parent product
- Variant code
- Legacy SKU
- Base SKU
- Additional physical attributes (color, size, material)
- Additional pricing fields with packaging units

### Product (Legacy)

Legacy model maintained for backward compatibility during migration.

### ProductCategory

Model for organizing products into categories:

- Name
- Code
- Description
- Parent reference (for hierarchical categories)

### ProductImage

Model for caching product images from external API:

- Reference to product
- External ID
- Image URL and thumbnail URL
- Image type
- Primary and front flags
- Display priority
- Metadata

### ImageSyncLog

Model for tracking image synchronization operations:

- Start and completion timestamps
- Status
- Statistics (images added, updated, deleted)
- Products affected
- Error messages

## Views

- Product list views with filtering and pagination
- Product detail views with images and variant selection
- API views for frontend integration

## Management Commands

### import_artikel_familie.py

Imports parent products from the legacy 4D system (Artikel_Familie table):

```
python manage.py import_artikel_familie [--limit N] [--dry-run]
```

### import_artikel_variante.py

Imports variant products from the legacy 4D system (Artikel_Variante table):

```
python manage.py import_artikel_variante [--limit N] [--dry-run]
```

### link_variants_to_existing_parents.py

Establishes parent-child relationships between variants and parent products:

```
python manage.py link_variants_to_existing_parents [--dry-run]
```

### sync_product_images.py

Synchronizes product images with the external image API:

```
python manage.py sync_product_images [--limit N] [--force]
```

### Additional Commands

- `fix_variant_parent_relationships.py`: Fixes incorrect parent-child relationships
- `fix_missing_variants.py`: Handles orphaned variant products
- `create_placeholder_parents.py`: Creates parent products for variants without parents
- `wipe_and_reload_parents.py`: Wipes and reloads all parent products (development use only)
- `wipe_and_reload_variants.py`: Wipes and reloads all variant products (development use only)

## API Integration

The products app integrates with an external image database through the image_api.py module. 
Key features:

- Secure API connection to external Django application
- Cached image data for performance
- Intelligent image prioritization
- Parent-variant aware image selection
- Fallback logic for maximum image coverage

## Frontend Integration

- Product list component (`ProductList.vue`) with filtering and pagination
- Product detail component (`ProductDetail.vue`) with images and variant selection

## Installation

1. Add 'products' to INSTALLED_APPS in settings.py
2. Run migrations: `python manage.py migrate products`
3. Include the app URLs in your project's urls.py:
   ```python
   path('products/', include('products.urls', namespace='products')),
   ```
4. Include the API URLs in your project's api_urls.py:
   ```python
   path('products/', include('products.api_urls', namespace='api_products')),
   ```

## Dependencies

- Pillow: Required for image handling
- Django: 4.2 or higher
- Requests: Required for API integration 