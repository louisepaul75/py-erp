# Products App

This Django app provides product management functionality for the pyERP system.

## Features

- Product catalog management
- Product categorization
- Product image management
- Import products from legacy 4D system
- Advanced product search and filtering

## Models

### Product

The main model for storing product information, including:

- Basic information (name, SKU, slug, category, manufacturer)
- Descriptions (short description, full description, features, keywords)
- Physical attributes (weight, dimensions)
- Pricing (cost, list price, sale price)
- Inventory (stock quantity, min/max stock levels, reorder point)
- Sales statistics (units sold, revenue, last sold date)
- Flags (active, featured, on sale)
- SEO metadata (meta keywords, meta description)
- Timestamps (created, updated)

### ProductCategory

Model for organizing products into categories:

- Name
- Slug (for URL-friendly representation)
- Description
- Active status

### ProductImage

Model for storing product images:

- Image file
- Alt text (for accessibility)
- Primary flag (to indicate the main product image)
- Timestamps (created, updated)

## Views

- `ProductListView`: Displays a list of products with filtering and pagination
- `ProductDetailView`: Displays detailed information about a specific product
- `CategoryListView`: Displays a list of product categories

## Management Commands

### import_products

Imports products from the legacy 4D system:

```
python manage.py import_products [--limit N] [--update] [--dry-run]
```

Options:
- `--limit N`: Limit the import to N products
- `--update`: Update existing products
- `--dry-run`: Perform a dry run without saving to the database

## Templates

- `product_list.html`: Template for displaying the product list
- `product_detail.html`: Template for displaying product details
- `category_list.html`: Template for displaying the category list

## Forms

- `ProductForm`: Form for creating and editing products
- `ProductCategoryForm`: Form for creating and editing product categories
- `ProductImageForm`: Form for uploading product images
- `ProductSearchForm`: Form for searching and filtering products

## URLs

- `/products/`: Product list view
- `/products/categories/`: Category list view
- `/products/<id>/`: Product detail view (by ID)
- `/products/<slug>/`: Product detail view (by slug)

## Admin Interface

The app provides a comprehensive admin interface for managing products, categories, and images.

## Installation

1. Add 'products' to INSTALLED_APPS in settings.py
2. Run migrations: `python manage.py migrate products`
3. Include the app URLs in your project's urls.py:
   ```python
   path('products/', include('products.urls', namespace='products')),
   ```

## Dependencies

- Pillow: Required for image handling
- Django: 4.2 or higher 