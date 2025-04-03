"""
Transformers for image data from the external CMS.
"""

from typing import Any, Dict, List, Optional
from django.utils import timezone

from pyerp.sync.transformers.base import BaseTransformer
from pyerp.utils.logging import get_logger


logger = get_logger(__name__)


class ImageTransformer(BaseTransformer):
    """Transformer for image data from the external CMS API."""

    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform image data to format expected by Django models.

        Args:
            source_data: List of image records from the API

        Returns:
            List of transformed image records ready for loading
        """
        transformed_records = []
        
        logger.info(f"Transforming {len(source_data)} image records")
        
        for record in source_data:
            try:
                # Create a new dictionary for the transformed record
                transformed = {}
                
                # Process original file data
                original_file = record.get('original_file', {})
                if original_file:
                    # Extract file ID as external_id
                    file_id = original_file.get('file_id')
                    if file_id:
                        transformed['external_id'] = str(file_id)
                    
                    # Extract image type
                    image_type = original_file.get('type')
                    if image_type:
                        transformed['image_type'] = image_type
                    
                    # Extract image URL
                    file_url = original_file.get('file_url')
                    if file_url:
                        transformed['image_url'] = file_url
                
                # Process exported files to find thumbnails or alternative formats
                exported_files = record.get('exported_files', [])
                for exported_file in exported_files:
                    # Find a thumbnail image (smaller size or specific type)
                    if exported_file.get('type') in ['png', 'jpg_k']:
                        file_url = exported_file.get('image_url')
                        if file_url:
                            # If we don't have a primary image URL yet, use this one
                            if 'image_url' not in transformed:
                                transformed['image_url'] = file_url
                            
                            # If this is a smaller image, use it as thumbnail
                            resolution = exported_file.get('resolution', [0, 0])
                            if resolution and isinstance(resolution, list) and len(resolution) >= 2:
                                if resolution[0] <= 500 and 'thumbnail_url' not in transformed:
                                    transformed['thumbnail_url'] = file_url
                
                # Process article associations (linking to products)
                articles = record.get('articles', [])
                article_data = []
                is_front = False
                
                for article in articles:
                    # Extract product article number
                    article_number = article.get('article_number') or article.get('number')
                    if article_number:
                        article_info = {
                            'sku': article_number,
                            'is_front': article.get('front', False)
                        }
                        article_data.append(article_info)
                        
                        # If any article marks this as a front image, set the flag
                        if article.get('front', False):
                            is_front = True
                
                # Store article data in metadata and set front flag
                transformed['metadata'] = {'articles': article_data}
                transformed['is_front'] = is_front
                
                # Set default values for remaining fields
                transformed['is_primary'] = False  # Will be determined during loading
                transformed['alt_text'] = ''
                transformed['priority'] = 0
                transformed['last_synced'] = timezone.now()
                
                # Validate the transformed record
                if 'external_id' not in transformed or 'image_url' not in transformed:
                    logger.warning(f"Skipping record due to missing required fields: {transformed}")
                    continue
                
                # Add the transformed record to the result list
                transformed_records.append(transformed)
                
            except Exception as e:
                logger.error(f"Error transforming image record: {e}", exc_info=True)
        
        logger.info(f"Successfully transformed {len(transformed_records)} image records")
        return transformed_records 