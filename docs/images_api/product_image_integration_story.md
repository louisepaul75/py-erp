# Product Image Integration User Story

## Story Metadata
- **ID:** PYERP-124
- **Type:** Feature
- **Epic:** Product Management
- **Priority:** High
- **Story Points:** 13
- **Assignee:** TBD
- **Sprint:** Upcoming
- **Labels:** product, images, integration, api
- **Status:** To Do

## Summary
Integrate the external image database with the ERP system to display and manage product images within the application.

## Description

### As a product manager/sales representative
### I want to access and manage product images from our external image database directly within the ERP system
### So that I can efficiently work with product visuals while ensuring consistent product representation across all systems

Currently, product images are stored in a separate Django application accessed via API. This story implements the integration between our ERP system and the image database to display product images in the ERP and allow basic image management without needing to access the external system.

The external image database contains different image types (Produktfoto, social media, etc.), and each product can have multiple images while each image can be linked to multiple products. Images need to be prioritized based on type and a "front" flag, with Produktfoto + front=true having the highest priority.

## Business Value
- Improves product data completeness by showing relevant images alongside product information
- Reduces context switching between systems when managing products
- Ensures consistency of product images across ERP and other systems
- Enhances sales and marketing processes by providing immediate visual product verification

## Acceptance Criteria

1. **Image Display**
   - [ ] Product detail pages display images from the external database
   - [ ] Images are displayed according to priority (Produktfoto + front=true first, then Produktfoto only, etc.)
   - [ ] If multiple images exist, they are displayed in a thumbnail gallery with the primary image highlighted
   - [ ] Image gallery supports clicking thumbnails to view larger images

2. **Image Management**
   - [ ] Admins can select which image should be the primary image for a product
   - [ ] Admins can view all available images for a product in the admin interface
   - [ ] Admins can trigger manual synchronization for specific products
   - [ ] Image metadata (type, source) is visible in the admin interface

3. **Synchronization**
   - [ ] The system performs a daily automatic sync with the external image database
   - [ ] Sync process is logged with details of added/updated/removed images
   - [ ] Failed syncs generate appropriate notifications to administrators
   - [ ] Sync process runs in the background without impacting system performance

4. **Performance & Security**
   - [ ] Images load asynchronously to prevent UI slowdowns
   - [ ] Image data is cached appropriately to reduce API calls
   - [ ] API credentials are stored securely (not in code)
   - [ ] System gracefully handles cases where the external API is unavailable

5. **Integration**
   - [ ] Images are available via API for other systems (like POS or eCommerce)
   - [ ] Image URLs are accessible in product exports
   - [ ] Image changes in the external system are reflected in the ERP within 24 hours

## Technical Details

### Data Models
```python
class ProductImage(models.Model):
    """
    Cached information about product images from external system
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    external_id = models.CharField(max_length=255, help_text="ID from external image database")
    image_url = models.URLField(max_length=500)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    image_type = models.CharField(max_length=50, help_text="Type of image (e.g., 'Produktfoto')")
    is_primary = models.BooleanField(default=False, help_text="Whether this is the primary image for the product")
    is_front = models.BooleanField(default=False, help_text="Whether this image is marked as 'front' in the source system")
    priority = models.IntegerField(default=0, help_text="Display priority (lower numbers shown first)")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional metadata from the source system")
    last_synced = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'id']
        unique_together = [('product', 'external_id')]
        indexes = [
            models.Index(fields=['product', 'is_primary']),
            models.Index(fields=['external_id']),
        ]

class ImageSyncLog(models.Model):
    """
    Track image synchronization history and results
    """
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='in_progress'
    )
    images_added = models.IntegerField(default=0)
    images_updated = models.IntegerField(default=0)
    images_deleted = models.IntegerField(default=0)
    products_affected = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
```

### API Integration
- API client will connect to `http://webapp.zinnfiguren.de/api/all-files-and-articles/`
- Authentication via HTTP Basic Auth with credentials from environment variables
- Support for pagination with configurable page size

### Image Prioritization Logic
1. Produktfoto + front=true images (highest priority)
2. Produktfoto images (second priority)
3. Images with front=true flag (third priority)
4. All other images (lowest priority)

### Format Prioritization Logic ✅ *Implemented*
1. PNG format (highest priority)
2. JPEG format (medium priority)
3. Original format (lowest priority)
4. For each format, higher resolution images are preferred for product detail views
5. Thumbnails use appropriate lower resolution versions for better performance

### Environment Configuration
```python
# settings.py additions
IMAGE_API = {
    'BASE_URL': os.environ.get('IMAGE_API_URL', 'http://webapp.zinnfiguren.de/api/'),
    'USERNAME': os.environ.get('IMAGE_API_USERNAME'),
    'PASSWORD': os.environ.get('IMAGE_API_PASSWORD'),
    'TIMEOUT': int(os.environ.get('IMAGE_API_TIMEOUT', 30)),
    'CACHE_ENABLED': os.environ.get('IMAGE_API_CACHE_ENABLED', 'True').lower() == 'true',
    'CACHE_TIMEOUT': int(os.environ.get('IMAGE_API_CACHE_TIMEOUT', 3600)),  # 1 hour
}
```

### Security Considerations
- Credentials for the image API are stored in environment variables, not in code ✅ *Configured*
- API credentials have been securely configured in the environment variables ✅ *Configured*
- Environment variables are configured in the .env file (not committed to version control)
- API requests use HTTPS when in production
- API client implements retry logic with exponential backoff
- Error handling includes security considerations (not exposing sensitive information in error messages)

## Tasks

1. **Setup & Foundation** (3 points)
   - [x] Create data models for ProductImage and ImageSyncLog
   - [x] Set up configuration framework for API connection
   - [x] Create base API client with authentication handling

2. **Sync Implementation** (5 points)
   - [x] Implement image data processing and prioritization logic
   - [x] Create management command for initial sync
   - [ ] Implement Celery task for background processing
   - [ ] Add scheduled job for daily sync

3. **UI Components** (3 points)
   - [ ] Add image gallery component to product detail pages
   - [ ] Implement admin interface for image management
   - [ ] Create API endpoints for frontend interaction

4. **Testing & Quality Assurance** (2 points)
   - [x] Write unit tests for API client and data processing
   - [x] Create integration tests for sync process
   - [ ] Perform performance testing with large product catalogs

5. **Documentation & Deployment** (1 point)
   - [x] Document API integration details
   - [ ] Create user guide for image management
   - [ ] Prepare deployment instructions

## Progress Summary (As of 2025-03-15)

### Completed Tasks
- ✅ Set up proper environment configuration for API credentials
- ✅ Created test scripts to verify API connectivity and authentication
- ✅ Successfully tested retrieval of images for specific products (article numbers)
- ✅ Documented API structure and image data format
- ✅ Implemented image prioritization logic in test scripts
- ✅ Created ProductImage and ImageSyncLog models with migrations
- ✅ Implemented format prioritization to prefer web-friendly formats (PNG > JPEG > original)
- ✅ Added resolution-based selection to choose the best quality images
- ✅ Created sync_product_images management command for synchronizing product images
- ✅ Successfully tested syncing images with a test product
- ✅ Implemented smart article number selection based on product hierarchy
- ✅ Created robust fallback logic for image retrieval with multiple strategies
- ✅ Enhanced ProductListView to preload images for both parent and variant products
- ✅ Improved ProductDetailView to use the new fallback logic for image retrieval
- ✅ Updated save_product_images function to use consistent image retrieval logic
- ✅ Added detailed logging for image retrieval process to aid troubleshooting
- ✅ Implemented custom template filter for accessing dictionary items by key
- ✅ Modified sync process to use individual record processing instead of bulk operations
- ✅ Added comprehensive error handling for individual image creation and updates
- ✅ Ensured proper database sequence usage for reliable ID generation
- ✅ Optimized batch processing for primary flag updates

### Parent-Variant Product Handling
- ✅ **Smart Article Number Selection**: Implemented `get_appropriate_article_number` method that intelligently determines which article number to use based on product type:
  - For parent products: Uses the parent's SKU
  - For variants with a parent: Uses the parent's SKU for consistent imagery
  - For variants without a parent: Uses the base_sku if available, otherwise falls back to the variant's own SKU

- ✅ **Fallback Strategy**: Implemented `get_product_images` method with comprehensive fallback logic:
  1. First tries with the appropriate article number based on product type
  2. If no images found, tries with the product's own SKU
  3. If still no images and it's a variant, tries with the base_sku
  4. If still no images and it has a parent, tries with the parent's SKU
  
- ✅ **Optimized Batch Processing**: Enhanced ProductListView to:
  - Create a mapping of products to their appropriate article numbers
  - Get unique article numbers to search for (reducing API calls)
  - Preload images for these article numbers
  - Map the images back to products for display

### API Findings
1. **API Structure**:
   - The API contains approximately 2,489 image records
   - Each image can be associated with multiple products
   - Images have multiple file formats (original + exported versions)

2. **Image Types**:
   - Various image types were identified: "Produktfoto", "Markt-Messe-Shop", "Szene"
   - These types can be used for prioritization

3. **File Formats**:
   - Original images are in various formats including PSD, JPEG, etc.
   - Exported formats include: PNG, JPEG, TIFF
   - Image resolutions range from thumbnails (200×200) to full size (4032×3024)
   - Format prioritization system implemented: PNG > JPEG > original format

4. **Product Association**:
   - Products are linked via the `articles` array with an article number
   - Some images have a `front=true` attribute indicating they should be the primary image
   - Not all images are associated with products (empty articles array)
   - Product SKU must match article number for successful association
   - Parent-variant relationships require special handling for consistent imagery

### Database Improvements
- ✅ **Individual Record Processing**:
  - Replaced bulk operations with individual record creation and updates
  - Each image is saved individually using `image.save()` to ensure proper ID generation
  - Added error handling for individual records to prevent sync failures
  
- ✅ **Sequence Management**:
  - Ensured proper usage of the `products_productimage_id_seq` sequence
  - Fixed potential ID conflicts that could occur with bulk operations
  - Improved compatibility with PostgreSQL's sequence management
  
- ✅ **Performance Optimizations**:
  - Maintained transaction handling for database consistency
  - Optimized page size defaults for better performance
  - Added batch processing for primary flag updates

### Next Steps
1. Complete the admin interface for image management
2. Implement the UI components for displaying images on product pages
3. Set up scheduled daily sync with Celery
4. Create user documentation for the image management interface

## Dependencies
- Requires working external image database API
- Depends on existing Product model
- Needs Celery setup for background processing

## References
- [Legacy code snippet for image API interaction](link-to-code-repository)
- [External Image DB API Documentation](link-to-documentation)
- [PRD section on Product Image Integration](.ai/prd.md#411-product-image-integration)

## Definition of Done
- All acceptance criteria are met
- Code passes all tests (>80% coverage) and meets quality standards
- Documentation is complete and up-to-date
- Feature has been tested in staging environment with real data
- Product owners have approved the implementation 