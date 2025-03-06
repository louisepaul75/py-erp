# Image Format Prioritization Implementation

## Overview

This document details the implementation of image format prioritization in the PyERP product image integration. The goal was to enhance the image selection logic to prefer web-friendly formats (PNG, JPEG) over design formats (PSD) while considering image quality and resolution.

## Implementation Details

### Key Changes

1. **Format Priority System:**
   - Implemented a hierarchical format priority: PNG > JPEG > original format
   - Added resolution-based selection within each format category
   - Updated the `parse_image` method in the `ImageAPIClient` class to handle format prioritization

2. **Resolution-Based Selection:**
   - For each format type, we now track the highest resolution available
   - Higher resolution images are preferred for product detail views
   - Lower resolution images (around 200-300px) are selected for thumbnails

3. **Format Conversion Handling:**
   - The system now recognizes various exported file formats including PNG and multiple JPEG variants (jpg_k, jpg_g)
   - Added more robust file format detection and normalization

## Technical Implementation

### Updated Parse Image Method

```python
def parse_image(self, image_data):
    """
    Parse the image data from the API response into a more usable format.
    """
    result = {
        'external_id': image_data.get('id', ''),
        'image_type': image_data.get('original_file', {}).get('type', ''),
        'images': [],
        'metadata': image_data,
    }

    # Initialize image URL variables
    primary_image_url = None
    png_url = None
    jpeg_url = None

    # Process original image
    if image_data.get('original_file') and 'file_url' in image_data['original_file']:
        original_url = image_data['original_file']['file_url']
        original_format = image_data['original_file'].get('format', '').lower()

        # Add to images list
        result['images'].append({
            'type': 'original',
            'format': original_format,
            'url': original_url,
            'resolution': None
        })

        # Set as potential primary image based on format
        if original_format == 'png':
            png_url = original_url
        elif original_format in ('jpg', 'jpeg'):
            jpeg_url = original_url
        else:
            primary_image_url = original_url  # Default to original if not PNG or JPEG

    # Process exported images with resolution tracking
    thumbnail_url = None
    highest_res_png = (0, None)
    highest_res_jpeg = (0, None)

    for export in image_data.get('exported_files', []):
        if export.get('image_url'):
            img_format = export.get('type', '').lower()
            resolution = export.get('resolution', [])
            img_url = export['image_url']

            # Add to images list
            result['images'].append({
                'type': 'exported',
                'format': img_format,
                'url': img_url,
                'resolution': resolution
            })

            # Find suitable thumbnail
            if img_format == 'png' and resolution and resolution[0] <= 300:
                if thumbnail_url is None or (resolution[0] <= 300 and resolution[0] > 150):
                    thumbnail_url = img_url

            # Track highest resolution by format
            if img_format == 'png' and resolution:
                total_pixels = resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                if total_pixels > highest_res_png[0]:
                    highest_res_png = (total_pixels, img_url)
            elif img_format in ('jpg', 'jpg_k', 'jpg_g', 'jpeg') and resolution:
                total_pixels = resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                if total_pixels > highest_res_jpeg[0]:
                    highest_res_jpeg = (total_pixels, img_url)

    # Select highest resolution images by format
    if highest_res_png[1]:
        png_url = highest_res_png[1]
    if highest_res_jpeg[1]:
        jpeg_url = highest_res_jpeg[1]

    # Apply format priority: PNG > JPEG > Original
    if png_url:
        result['image_url'] = png_url
    elif jpeg_url:
        result['image_url'] = jpeg_url
    elif primary_image_url:
        result['image_url'] = primary_image_url

    result['thumbnail_url'] = thumbnail_url

    # Process article data
    for article in image_data.get('articles', []):
        result['articles'] = image_data.get('articles', [])
        result['is_front'] = any(a.get('front', False) for a in image_data.get('articles', []))
        break

    return result
```

## Testing and Validation

### Test Case Results

1. **Original PSD Test:**
   - **Before:** System selected the PSD file as the primary image
   - **After:** System selected the PNG version (424x200) of the same image

2. **Resolution Test:**
   - When multiple PNG files were available, the system correctly selected the highest resolution
   - Thumbnail selection correctly chose PNG files with resolution around 200-300px

3. **Format Fallback Test:**
   - When no PNG was available, the system correctly fell back to JPEG
   - When neither PNG nor JPEG was available, it correctly used the original format

## Benefits

1. **Performance Improvement:**
   - Browsers can directly display PNG and JPEG without conversion
   - Smaller file sizes for web display compared to original design files

2. **User Experience:**
   - Images load faster with web-optimized formats
   - Consistent image quality across the application

3. **Storage Efficiency:**
   - No need to manually convert and store multiple versions of the same image
   - Leverages the formats already available in the external image database

## Next Steps

1. **Image Caching:**
   - Implement local caching of frequently accessed images
   - Add cache headers for improved browser caching

2. **Image Optimization:**
   - Consider adding server-side image optimization for very large images
   - Implement lazy loading for image galleries

3. **UI Implementation:**
   - Complete the product detail page image gallery
   - Implement the admin interface for image management

## Conclusion

The implementation of image format prioritization has significantly improved the handling of product images in PyERP. By intelligently selecting the most appropriate web-friendly formats at the optimal resolution, we've enhanced both performance and user experience while maintaining image quality.

This implementation aligns with the requirements specified in the PRD and completes a key part of the Product Image Integration story.
