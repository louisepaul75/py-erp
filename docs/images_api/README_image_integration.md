# Product Image Integration

This module integrates the external image database with our ERP system, allowing users to view and manage product images directly within the application.

## Setup Instructions

### 1. Environment Variables

Set up your environment variables in the `.env` file. If you don't have one, copy `.env.example` to `.env` and fill in the values:

```
cp .env.example .env
```

Then edit the `.env` file and update the Image API configuration section:

```
# Image API Configuration
IMAGE_API_URL=http://webapp.zinnfiguren.de/api/
IMAGE_API_USERNAME=your_api_username
IMAGE_API_PASSWORD=your_api_password
IMAGE_API_TIMEOUT=30
IMAGE_API_CACHE_ENABLED=True
IMAGE_API_CACHE_TIMEOUT=3600
```

Replace `your_api_username` and `your_api_password` with the actual credentials.

### 2. Install Dependencies

Make sure you have the required dependencies:

```
pip install requests python-dotenv
```

### 3. Test the API Connection

Run the test script to verify that you can connect to the API:

```
python scripts/test_image_api_connection.py
```

If successful, you should see:
```
YYYY-MM-DD HH:MM:SS - image_api_test - INFO - Testing connection to http://webapp.zinnfiguren.de/api/
YYYY-MM-DD HH:MM:SS - image_api_test - INFO - ✅ Connection successful!
YYYY-MM-DD HH:MM:SS - image_api_test - INFO - API returned 12345 total records
```

To see sample data from the API:

```
python scripts/test_image_api_connection.py --verbose
```

## Database Models

After verifying the API connection, you'll need to create the database models:

1. Run migrations to create the necessary tables:

```
python manage.py makemigrations products
python manage.py migrate
```

2. Initialize the data by running the sync command:

```
python manage.py sync_product_images --dry-run
```

Review the output to make sure everything looks correct, then run without the `--dry-run` flag to actually import the data.

## Usage

### Viewing Product Images

Once the integration is set up, product images will appear in the following places:

1. Product detail pages - Main product image with thumbnail gallery
2. Product list pages - Thumbnail of the primary image
3. Admin interface - All images with metadata

### Managing Images

Administrators can manage product images through the admin interface:

1. Go to `Admin > Products > Product Images`
2. Select a product to view its images
3. Use the "Set as Primary" button to mark an image as the primary image
4. Use the "Sync Images" action to refresh images from the external database

### API Endpoints

The following API endpoints are available for frontend integration:

- `GET /api/v1/product-images/?product_id=<id>` - Get all images for a product
- `POST /api/v1/product-images/set-primary/` - Set an image as primary

## Troubleshooting

If you encounter issues with the image integration:

1. Check your API credentials in the `.env` file
2. Run the test script with the `--verbose` flag to debug connection issues
3. Check the image sync logs in the admin interface
4. Ensure your network allows connections to the external API

## Development

When developing features related to the image integration:

1. Use the dry-run option for sync commands to preview changes
2. Run tests with `pytest tests/test_image_api.py`
3. Check the code coverage with `pytest --cov=products.image_api tests/`
