"""
Loaders for image data from the external CMS.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from django.db import transaction
from django.utils import timezone

from pyerp.sync.loaders.base import BaseLoader
from pyerp.utils.logging import get_logger
from pyerp.business_modules.products.models import ProductImage, VariantProduct, ImageSyncLog


logger = get_logger(__name__)


class ProductImageLoader(BaseLoader):
    """Loader for product image data into ProductImage model."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.

        Returns:
            List of required field names
        """
        return []  # No required fields, using Django models directly

    def prepare_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare a record for loading.

        Args:
            record: Transformed image record to prepare

        Returns:
            Tuple of (lookup criteria, prepared record)
        """
        # Extract lookup criteria
        lookup_criteria = {
            'external_id': record.get('external_id')
        }
        
        # Return a copy of the record to avoid modifying the original
        prepared_record = record.copy()
        
        # Extract article information from metadata to find product
        articles = prepared_record.get('metadata', {}).get('articles', [])
        
        # Try to find a matching product
        product = None
        if articles:
            # First try: Direct SKU match with any article
            skus = [article.get('sku') for article in articles if article.get('sku')]
            if skus:
                product = VariantProduct.objects.filter(sku__in=skus).first()
                
                if product:
                    logger.info(f"Found product match by direct SKU: {product.sku}")
                    prepared_record['product'] = product
        
        return lookup_criteria, prepared_record

    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True,
    ) -> Optional[Any]:
        """Load a single image record into the ProductImage model.

        Args:
            lookup_criteria: Criteria to find existing record
            record: Record data to load
            update_existing: Whether to update existing records

        Returns:
            Created or updated ProductImage record, or None if skipped

        Raises:
            ValueError: If record is invalid
        """
        try:
            # Remove non-model fields before creating or updating
            record_copy = record.copy()
            
            # Try to find existing record
            try:
                existing_record = ProductImage.objects.get(**lookup_criteria)
                
                # If we're not updating existing records, skip
                if not update_existing:
                    logger.info(f"Skipping existing image with ID {existing_record.id}")
                    return None
                
                # Update existing record
                for key, value in record_copy.items():
                    if key not in ['id', 'pk']:
                        setattr(existing_record, key, value)
                
                existing_record.save()
                logger.info(f"Updated ProductImage record with ID {existing_record.id}")
                return existing_record
                
            except ProductImage.DoesNotExist:
                # Create new record
                new_record = ProductImage(**record_copy)
                new_record.save()
                logger.info(f"Created new ProductImage record with ID {new_record.id}")
                return new_record
                
        except Exception as e:
            error_msg = f"Error loading image record: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def load(
        self, records: List[Dict[str, Any]], update_existing: bool = True
    ) -> Dict[str, Any]:
        """Load records into the ProductImage model with transaction support.

        Args:
            records: List of records to load
            update_existing: Whether to update existing records

        Returns:
            Dictionary containing load statistics
        """
        # Create or update sync log
        sync_log = ImageSyncLog.objects.create(
            status="in_progress",
            started_at=timezone.now()
        )
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        affected_products = set()
        
        try:
            # Process each record in a separate transaction
            for record in records:
                try:
                    with transaction.atomic():
                        # Prepare record
                        lookup_criteria, prepared_record = self.prepare_record(record)
                        
                        # Load record
                        result = self.load_record(lookup_criteria, prepared_record, update_existing)
                        
                        # Update counters
                        if result is None:
                            skipped_count += 1
                        elif getattr(result, '_state', None).adding:
                            created_count += 1
                        else:
                            updated_count += 1
                            
                        # Track affected products
                        if result and result.product:
                            affected_products.add(result.product.id)
                            
                except Exception as e:
                    logger.error(f"Error loading record: {e}", exc_info=True)
                    error_count += 1
            
            # Update sync log with results
            sync_log.status = "completed"
            sync_log.completed_at = timezone.now()
            sync_log.images_added = created_count
            sync_log.images_updated = updated_count
            sync_log.images_deleted = 0  # No deletion in this implementation
            sync_log.products_affected = len(affected_products)
            sync_log.save()
            
            logger.info(
                f"Image sync completed: {created_count} created, "
                f"{updated_count} updated, {skipped_count} skipped, "
                f"{error_count} errors, {len(affected_products)} products affected"
            )
            
            return {
                "created": created_count,
                "updated": updated_count,
                "skipped": skipped_count,
                "errors": error_count,
                "products_affected": len(affected_products),
                "sync_log_id": sync_log.id
            }
            
        except Exception as e:
            # Update sync log with error
            sync_log.status = "failed"
            sync_log.completed_at = timezone.now()
            sync_log.error_message = str(e)
            sync_log.save()
            
            logger.error(f"Error during image sync: {e}", exc_info=True)
            
            raise 