"""
Image API Client for external product image database.

This module provides a client for interacting with the external image database API  # noqa: E501
located at webapp.zinnfiguren.de. It handles authentication, connection management,  # noqa: E501
and parsing of API responses.
"""

import hashlib
import json
import logging

import requests
import urllib3
from django.conf import settings
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

from pyerp.products.models import ParentProduct

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
        self.base_url = settings.IMAGE_API.get(
            "BASE_URL",
            "http://webapp.zinnfiguren.de/api/",
        )
        self.username = settings.IMAGE_API.get("USERNAME")
        self.password = settings.IMAGE_API.get("PASSWORD")
        self.timeout = settings.IMAGE_API.get(
            "TIMEOUT",
            60,
        )  # Increased default timeout
        self.cache_enabled = settings.IMAGE_API.get("CACHE_ENABLED", True)
        self.cache_timeout = settings.IMAGE_API.get(
            "CACHE_TIMEOUT",
            3600,
        )  # 1 hour
        self.verify_ssl = settings.IMAGE_API.get(
            "VERIFY_SSL",
            False,
        )  # Default to not verifying SSL

        # Ensure the base URL ends with a slash
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        # Set up retry strategy
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )

        # Create a session with the retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.auth = HTTPBasicAuth(self.username, self.password)

        # Disable SSL verification warnings if verify_ssl is False
        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_appropriate_article_number(self, product):
        """
        Determine the appropriate article number to use for image search
        based on whether the product is a parent or variant.

        Args:
            product: The Product model instance

        Returns:
            str: The article number to use for image search
        """
        logger.debug(
            f"Determining appropriate article number for product {product.sku}",
        )

        # For parent products (ParentProduct model)
        if isinstance(product, ParentProduct):
            logger.debug(f"Using parent SKU: {product.sku}")
            return product.sku

        # For variants (VariantProduct model)
        # First, check if the variant has its own images
        variant_sku = product.sku
        logger.debug(f"Checking variant SKU: {variant_sku}")

        # If it's a variant with a parent, also try the parent's SKU
        if hasattr(product, "parent") and product.parent:
            parent_sku = product.parent.sku
            logger.debug(f"Also checking parent SKU: {parent_sku}")
            return parent_sku

        # If no parent but has base_sku, use that
        if (
            hasattr(product, "base_sku")
            and product.base_sku
            and product.base_sku != product.sku
        ):
            logger.debug(f"Using base SKU: {product.base_sku}")
            return product.base_sku

        # Default to the product's own SKU
        logger.debug(f"Defaulting to product SKU: {product.sku}")
        return product.sku

    def _make_request(self, endpoint, params=None):
        """
        Make a request to the API endpoint with authentication.

        Args:
            endpoint (str): API endpoint to request
            params (dict, optional): Query parameters

        Returns:
            dict: JSON response from the API or None if the request failed
        """
        url = f"{self.base_url}{endpoint}"

        # Create a safe cache key
        if params:
            params_str = json.dumps(params, sort_keys=True)
            params_hash = hashlib.sha256(
                params_str.encode(), usedforsecurity=False
            ).hexdigest()
            cache_key = f"image_api_{endpoint}_{params_hash}"
        else:
            cache_key = f"image_api_{endpoint}_none"

        # Check if the response is in cache
        if self.cache_enabled:
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Using cached response for {url}")
                return cached_response

        try:
            logger.debug(f"Making request to {url} with params {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
                verify=self.verify_ssl,  # Use the SSL verification setting
            )

            if response.status_code == 200:
                data = response.json()

                # Cache the response if caching is enabled
                if self.cache_enabled:
                    cache.set(cache_key, data, self.cache_timeout)

                return data
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        except requests.exceptions.SSLError as e:
            logger.error(f"SSL Error: {e}")
            if self.verify_ssl:
                logger.warning(
                    "Consider setting VERIFY_SSL=False in settings if the certificate is self-signed",
                )
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
            params={"page": page, "page_size": page_size},
        )

    def search_product_images(self, article_number):
        """
        Search for images associated with a specific product by article number.

        Args:
            article_number (str): The product article number to search for

        Returns:
            list: List of image data for the product
        """
        product_cache_key = f"product_images_{article_number}"
        if self.cache_enabled:
            cached_images = cache.get(product_cache_key)
            if cached_images:
                logger.debug(f"Using cached images for product {article_number}")
                return cached_images

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
                count = data.get("count", 0)
                total_pages = (count + page_size - 1) // page_size
                logger.info(f"Found {count} total records across {total_pages} pages")

            # Filter results for the specific article number
            for item in data.get("results", []):
                articles = item.get("articles", [])

                # Check if any article matches our article number
                for article in articles:
                    if article.get("number") == article_number:
                        product_images.append(item)
                        break

            page += 1

        # Continue searching through all pages instead of stopping early
        # We want to find ALL images for this product across all pages

        # Log how many images were found total
        if product_images:
            logger.info(
                f"Found {len(product_images)} images for article {article_number}",
            )

        # Cache the results for this product
        if self.cache_enabled and product_images:
            cache.set(product_cache_key, product_images, self.cache_timeout)

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
            "external_id": image_data.get("id", ""),
            "image_type": image_data.get("original_file", {}).get("type", ""),
            "images": [],
            "metadata": image_data,
        }

        # Initialize image URL variables
        primary_image_url = None
        png_url = None
        jpeg_url = None

        # Add original image
        if (
            image_data.get("original_file")
            and "file_url" in image_data["original_file"]
        ):
            original_url = image_data["original_file"]["file_url"]
            original_format = image_data["original_file"].get("format", "").lower()

            result["images"].append(
                {
                    "type": "original",
                    "format": original_format,
                    "url": original_url,
                    "resolution": None,
                },
            )

            # Set as potential primary image based on format
            if original_format == "png":
                png_url = original_url
            elif original_format in ("jpg", "jpeg"):
                jpeg_url = original_url
            else:
                primary_image_url = (
                    original_url  # Default to original if not PNG or JPEG
                )

        # Add exported images (different formats/resolutions)
        thumbnail_url = None
        highest_res_png = (0, None)
        highest_res_jpeg = (0, None)

        for export in image_data.get("exported_files", []):
            if export.get("image_url"):
                img_format = export.get("type", "").lower()
                resolution = export.get("resolution", [])
                img_url = export["image_url"]

                result["images"].append(
                    {
                        "type": "exported",
                        "format": img_format,
                        "url": img_url,
                        "resolution": resolution,
                    },
                )

                # Find a suitable thumbnail (prefer PNG around 200px)
                if img_format == "png" and resolution and resolution[0] <= 300:
                    if thumbnail_url is None or (
                        resolution[0] <= 300 and resolution[0] > 150
                    ):
                        thumbnail_url = img_url

                # Track highest resolution PNG and JPEG for primary image selection
                if img_format == "png" and resolution:
                    total_pixels = (
                        resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                    )
                    if total_pixels > highest_res_png[0]:
                        highest_res_png = (total_pixels, img_url)
                elif img_format in ("jpg", "jpg_k", "jpg_g", "jpeg") and resolution:
                    total_pixels = (
                        resolution[0] * resolution[1] if len(resolution) >= 2 else 0
                    )
                    if total_pixels > highest_res_jpeg[0]:
                        highest_res_jpeg = (total_pixels, img_url)

        # Select the primary image URL with format preference: PNG > JPEG > Original
        if highest_res_png[1]:
            png_url = highest_res_png[1]
        if highest_res_jpeg[1]:
            jpeg_url = highest_res_jpeg[1]

        # Prioritize PNG > JPEG > Original
        if png_url:
            result["image_url"] = png_url
        elif jpeg_url:
            result["image_url"] = jpeg_url
        elif primary_image_url:
            result["image_url"] = primary_image_url

        result["thumbnail_url"] = thumbnail_url

        # Set front flag and add article info
        result["articles"] = []
        for article in image_data.get("articles", []):
            result["articles"].append(
                {
                    "article_number": article.get("number", ""),
                    "variant_code": article.get("variant", ""),
                    "front": article.get("front", False),
                    "stock": article.get("stock"),
                },
            )

        # Set is_front flag based on any article being marked as front
        result["is_front"] = any(
            a.get("front", False) for a in image_data.get("articles", [])
        )

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
        if "original_file" in image_data:
            image_type = image_data.get("original_file", {}).get("type", "")
            is_front = any(
                a.get("front", False) for a in image_data.get("articles", [])
            )
        else:
            image_type = image_data.get("image_type", "")
            is_front = image_data.get("is_front", False)

        # Calculate priority (lower is higher priority)
        if image_type == "Produktfoto" and is_front:
            return 1  # Highest priority: Produktfoto + front
        if image_type == "Produktfoto":
            return 2  # Second priority: Produktfoto
        if is_front:
            return 3  # Third priority: Any front image
        if image_type == "Markt-Messe-Shop":
            return 4  # Fourth priority: Market/Shop images
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
            dict: Parsed image data for the best image, or None if no images found  # noqa: E501
        """
        images = self.search_product_images(article_number)

        if not images:
            return None

        # Sort by priority and take the first one
        sorted_images = self.sort_images_by_priority(images)
        best_image = sorted_images[0]

        return self.parse_image(best_image)

    def preload_product_images(self, article_numbers):
        """
        Preload images for multiple products at once.

        This method is useful for improving performance when displaying
        lists of products, as it can fetch and cache images for multiple
        products with fewer API calls.

        Args:
            article_numbers (list): List of product article numbers

        Returns:
            dict: Dictionary mapping article numbers to their best images
        """
        if not article_numbers:
            return {}

        # Check which products already have cached images
        uncached_articles = []
        result = {}

        for article in article_numbers:
            product_cache_key = f"product_images_{article}"
            cached_images = cache.get(product_cache_key)

            if cached_images:
                sorted_images = self.sort_images_by_priority(cached_images)
                if sorted_images:
                    result[article] = self.parse_image(sorted_images[0])
            else:
                uncached_articles.append(article)

        if not uncached_articles:
            return result

        # Fetch images for products that aren't cached yet
        logger.info(f"Preloading images for {len(uncached_articles)} products")

        # Process in batches to avoid excessive API calls
        page = 1
        page_size = 100
        total_pages = None

        while total_pages is None or page <= total_pages:
            data = self.get_all_images(page=page, page_size=page_size)

            if not data:
                break

            # Calculate total pages on first response
            if total_pages is None:
                count = data.get("count", 0)
                total_pages = (count + page_size - 1) // page_size

            # Process each image and check if it matches any of our products
            for item in data.get("results", []):
                articles = item.get("articles", [])

                # Check if this image is associated with any of our uncached products
                for article in articles:
                    article_number = article.get("number")
                    if article_number in uncached_articles:
                        product_cache_key = f"product_images_{article_number}"
                        product_images = cache.get(product_cache_key) or []
                        product_images.append(item)

                        # Cache the updated list
                        cache.set(product_cache_key, product_images, self.cache_timeout)

                        # If this is the first image for this product, add it to the result
                        if article_number not in result:
                            result[article_number] = self.parse_image(item)

            # Move to the next page
            page += 1

            # Stop if we've found images for all products
            if all(article in result for article in uncached_articles):
                break

        return result

    def get_product_images(self, product):
        """
        Get images for a product, trying multiple article number formats if needed.  # noqa: E501

        This method implements a fallback strategy to find images for a product:  # noqa: E501
        1. First tries with the appropriate article number based on product type  # noqa: E501
        2. If no images found, tries with the product's own SKU
        3. If still no images and it's a variant, tries with base_sku
        4. If still no images and it has a parent, tries with parent's SKU

        Args:
            product: The Product model instance

        Returns:
            list: List of image data for the product
        """
        article_number = self.get_appropriate_article_number(product)
        logger.info(
            f"Searching for images with primary article number: {article_number}",
        )
        images = self.search_product_images(article_number)

        if images:
            logger.info(f"Found {len(images)} images using primary article number")
            return images

        # If no images found and the article number wasn't the product's own SKU, try that
        if article_number != product.sku:
            logger.info(
                f"No images found with primary article number, trying product SKU: {product.sku}",
            )
            images = self.search_product_images(product.sku)

            if images:
                logger.info(f"Found {len(images)} images using product SKU")
                return images

        # If still no images and it's a variant with a base_sku different from what we've tried
        if (
            not product.is_parent
            and product.base_sku
            and product.base_sku != article_number
            and product.base_sku != product.sku
        ):
            logger.info(f"Trying base SKU: {product.base_sku}")
            images = self.search_product_images(product.base_sku)

            if images:
                logger.info(f"Found {len(images)} images using base SKU")
                return images

        # If still no images and it has a parent that we haven't tried yet
        if (
            product.parent
            and product.parent.sku != article_number
            and product.parent.sku != product.sku
        ):
            logger.info(f"Trying parent SKU: {product.parent.sku}")
            images = self.search_product_images(product.parent.sku)

            if images:
                logger.info(f"Found {len(images)} images using parent SKU")
                return images

        # If we've tried everything and found nothing
        logger.warning(
            f"No images found for product {product.sku} after trying all fallback options",
        )
        return []
