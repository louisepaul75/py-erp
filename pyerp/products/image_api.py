"""
Image API Client for external product image database.

This module provides a client for interacting with the external image database API
located at webapp.zinnfiguren.de. It handles authentication, connection management,
and parsing of API responses.
"""

import os
import logging
import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class ImageAPIClient:
    """
    Client for interacting with the external image database API.
    
    This client handles:
    - Connection to the API with proper authentication
    - Fetching and caching image data
    - Pagination through the API results
    - Finding images for specific products
    """
    
    def __init__(self):
        """Initialize the client with settings from Django configuration."""
        self.base_url = settings.IMAGE_API.get('BASE_URL', 'http://webapp.zinnfiguren.de/api/')
        self.username = settings.IMAGE_API.get('USERNAME')
        self.password = settings.IMAGE_API.get('PASSWORD')
        self.timeout = settings.IMAGE_API.get('TIMEOUT', 30)
        self.cache_enabled = settings.IMAGE_API.get('CACHE_ENABLED', True)
        self.cache_timeout = settings.IMAGE_API.get('CACHE_TIMEOUT', 3600)  # 1 hour
        
        # Ensure the base URL ends with a slash
        if not self.base_url.endswith('/'):
            self.base_url += '/'

    def _make_request(self, endpoint, params=None):
        """
        Make a request to the API endpoint with authentication.
        
        Args:
            endpoint (str): API endpoint to request
            params (dict, optional): Query parameters
            
        Returns:
            dict: JSON response from the API or None if the request failed
        """
        # Form the full URL
        url = f"{self.base_url}{endpoint}"
        
        # Check if the response is in cache
        cache_key = f"image_api:{endpoint}:{params}"
        if self.cache_enabled:
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Using cached response for {url}")
                return cached_response
        
        try:
            logger.debug(f"Making request to {url} with params {params}")
            response = requests.get(
                url,
                params=params,
                auth=HTTPBasicAuth(self.username, self.password),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache the response if caching is enabled
                if self.cache_enabled:
                    cache.set(cache_key, data, self.cache_timeout)
                    
                return data
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API connection error: {e}")
            return None
    
    def get_all_images(self, page=1, page_size=50):
        """
        Get a page of all images from the API.
        
        Args:
            page (int): Page number
            page_size (int): Number of items per page
            
        Returns:
            dict: API response with image data
        """
        return self._make_request(
            "all-files-and-articles/",
            params={"page": page, "page_size": page_size}
        )
    
    def search_product_images(self, article_number):
        """
        Search for images associated with a specific product by article number.
        
        Args:
            article_number (str): The product article number to search for
            
        Returns:
            list: List of image data for the product
        """
        # This could be optimized if the API supports direct filtering
        page = 1
        page_size = 100
        total_pages = None
        product_images = []
        
        while total_pages is None or page <= total_pages:
            data = self.get_all_images(page=page, page_size=page_size)
            
            if not data:
                break
                
            # Calculate total pages on first response
            if total_pages is None:
                count = data.get('count', 0)
                total_pages = (count + page_size - 1) // page_size
                logger.info(f"Found {count} total records across {total_pages} pages")
            
            # Filter results for the specific article number
            for item in data.get('results', []):
                articles = item.get('articles', [])
                
                # Check if any article matches our article number
                for article in articles:
                    if article.get('number') == article_number:
                        product_images.append(item)
                        break
            
            page += 1
            
            # Stop early if we've found at least one image
            if product_images:
                logger.info(f"Found {len(product_images)} images for article {article_number}")
                break
        
        return product_images
    
    def parse_image(self, image_data):
        """
        Parse the image data from the API response into a more usable format.
        
        Args:
            image_data (dict): Raw image data from the API
            
        Returns:
            dict: Parsed image information with URLs and metadata
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
        
        # Add original image
        if image_data.get('original_file') and 'file_url' in image_data['original_file']:
            original_url = image_data['original_file']['file_url']
            original_format = image_data['original_file'].get('format', '').lower()
            
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
        
        # Add exported images (different formats/resolutions)
        thumbnail_url = None
        highest_res_png = (0, None)
        highest_res_jpeg = (0, None)
        
        for export in image_data.get('exported_files', []):
            if export.get('image_url'):
                img_format = export.get('type', '').lower()
                resolution = export.get('resolution', [])
                img_url = export['image_url']
                
                result['images'].append({
                    'type': 'exported',
                    'format': img_format,
                    'url': img_url,
                    'resolution': resolution
                })
                
                # Find a suitable thumbnail (prefer PNG around 200px)
                if img_format == 'png' and resolution and resolution[0] <= 300:
                    if thumbnail_url is None or (resolution[0] <= 300 and resolution[0] > 150):
                        thumbnail_url = img_url
                
                # Track highest resolution PNG and JPEG for primary image selection
                if img_format == 'png' and resolution:
                    total_pixels = resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                    if total_pixels > highest_res_png[0]:
                        highest_res_png = (total_pixels, img_url)
                elif img_format in ('jpg', 'jpg_k', 'jpg_g', 'jpeg') and resolution:
                    total_pixels = resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                    if total_pixels > highest_res_jpeg[0]:
                        highest_res_jpeg = (total_pixels, img_url)
        
        # Select the primary image URL with format preference: PNG > JPEG > Original
        if highest_res_png[1]:
            png_url = highest_res_png[1]
        if highest_res_jpeg[1]:
            jpeg_url = highest_res_jpeg[1]
        
        # Prioritize PNG > JPEG > Original
        if png_url:
            result['image_url'] = png_url
        elif jpeg_url:
            result['image_url'] = jpeg_url
        elif primary_image_url:
            result['image_url'] = primary_image_url
        
        result['thumbnail_url'] = thumbnail_url
        
        # Set front flag and add article info
        for article in image_data.get('articles', []):
            result['articles'] = image_data.get('articles', [])
            result['is_front'] = any(a.get('front', False) for a in image_data.get('articles', []))
            break
        
        return result
    
    def get_image_priority(self, image_data):
        """
        Calculate the priority of an image based on its type and front flag.
        Lower numbers mean higher priority.
        
        Args:
            image_data (dict): Image data from the API or parsed image
            
        Returns:
            int: Priority value (lower is higher priority)
        """
        # Get the image type and front flag
        if 'original_file' in image_data:
            # Raw API data
            image_type = image_data.get('original_file', {}).get('type', '')
            is_front = any(a.get('front', False) for a in image_data.get('articles', []))
        else:
            # Parsed data
            image_type = image_data.get('image_type', '')
            is_front = image_data.get('is_front', False)
        
        # Calculate priority (lower is higher priority)
        if image_type == 'Produktfoto' and is_front:
            return 1  # Highest priority: Produktfoto + front
        elif image_type == 'Produktfoto':
            return 2  # Second priority: Produktfoto
        elif is_front:
            return 3  # Third priority: Any front image
        elif image_type == 'Markt-Messe-Shop':
            return 4  # Fourth priority: Market/Shop images
        else:
            return 5  # Lowest priority: Everything else
    
    def sort_images_by_priority(self, images):
        """
        Sort images by priority (highest first).
        
        Args:
            images (list): List of image data
            
        Returns:
            list: Sorted list of images
        """
        return sorted(images, key=self.get_image_priority)
    
    def get_best_image_for_product(self, article_number):
        """
        Get the best (highest priority) image for a product.
        
        Args:
            article_number (str): The product article number
            
        Returns:
            dict: Parsed image data for the best image, or None if no images found
        """
        images = self.search_product_images(article_number)
        
        if not images:
            return None
        
        # Sort by priority and take the first one
        sorted_images = self.sort_images_by_priority(images)
        best_image = sorted_images[0]
        
        return self.parse_image(best_image) 