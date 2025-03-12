"""
Transformers for inventory data from legacy systems.
"""

from typing import Dict, Any, List

from pyerp.business_modules.products.models import VariantProduct
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)


class StammLagerorteTransformer(BaseTransformer):
    """
    Transformer for Stamm_Lagerorte data from the legacy system.
    
    This transformer converts legacy storage location data to the format
    required by the StorageLocation model.
    """
    
    def transform(
        self, source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform storage location data from legacy format.
        
        Args:
            source_data: List of dictionaries containing legacy storage location data
            
        Returns:
            List of dictionaries in the format required by StorageLocation model
        """
        transformed_records = []
        skipped_records = 0
        
        for record in source_data:
            # Directly extract ID_Lagerort before applying mappings
            legacy_id = record.get('ID_Lagerort')
            
            # Log the original record to see if ID_Lagerort is present
            logger.debug(
                f"Original record before mapping: ID_Lagerort={legacy_id}, "
                f"keys={list(record.keys())}"
            )
            
            # Skip records without a legacy_id
            if legacy_id is None:
                skipped_records += 1
                logger.warning(f"Skipping record without legacy_id: {record}")
                continue
                
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Ensure legacy_id is set correctly
            transformed['legacy_id'] = str(legacy_id)
            
            # Log the transformed record to see if legacy_id is present
            logger.debug(
                f"After field mapping: legacy_id={transformed.get('legacy_id')}, "
                f"keys={list(transformed.keys())}"
            )
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Generate a descriptive name if not present
            if 'name' not in transformed:
                # Use location_code if available, otherwise generate from components
                if ('location_code' in transformed and 
                        transformed['location_code']):
                    transformed['name'] = transformed['location_code']
                else:
                    country = transformed.get('country', '')
                    city_building = transformed.get('city_building', '')
                    unit = transformed.get('unit', '')
                    compartment = transformed.get('compartment', '')
                    shelf = transformed.get('shelf', '')
                    
                    name_parts = [
                        p for p in [
                            country, city_building, unit, compartment, shelf
                        ] if p
                    ]
                    transformed['name'] = (
                        ' / '.join(name_parts) if name_parts 
                        else f"Location {transformed['legacy_id']}"
                    )
            
            # Set default values for required fields
            transformed.setdefault('is_active', True)
            
            # Log the legacy ID for debugging
            logger.debug(f"Mapped legacy ID: {transformed['legacy_id']}")
            
            transformed_records.append(transformed)
            
        logger.info(
            f"Transformed {len(transformed_records)} storage location records, "
            f"skipped {skipped_records} records without legacy_id"
        )
        return transformed_records


class BoxTypeTransformer(BaseTransformer):
    """
    Transformer for box type data.
    
    This transformer converts box type data to the format required by the 
    BoxType model.
    """
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform box type data.
        
        Args:
            source_data: List of dictionaries containing box type data
            
        Returns:
            List of dictionaries in the format required by BoxType model
        """
        transformed_records = []
        
        for record in source_data:
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Set default values for required fields
            transformed.setdefault('is_active', True)
            
            transformed_records.append(transformed)
            
        logger.info(f"Transformed {len(transformed_records)} box type records")
        return transformed_records


class BoxTransformer(BaseTransformer):
    """
    Transformer for box data.
    
    This transformer converts box data to the format required by the Box model.
    """
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform box data.
        
        Args:
            source_data: List of dictionaries containing box data
            
        Returns:
            List of dictionaries in the format required by Box model
        """
        transformed_records = []
        
        for record in source_data:
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Set default values for required fields
            transformed.setdefault('status', 'AVAILABLE')
            
            transformed_records.append(transformed)
            
        logger.info(f"Transformed {len(transformed_records)} box records")
        return transformed_records


class BoxSlotTransformer(BaseTransformer):
    """
    Transformer for box slot data.
    
    This transformer converts box slot data to the format required by the 
    BoxSlot model.
    """
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform box slot data.
        
        Args:
            source_data: List of dictionaries containing box slot data
            
        Returns:
            List of dictionaries in the format required by BoxSlot model
        """
        transformed_records = []
        
        for record in source_data:
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Set default values for required fields
            transformed.setdefault('is_occupied', False)
            
            transformed_records.append(transformed)
            
        logger.info(f"Transformed {len(transformed_records)} box slot records")
        return transformed_records


class ProductInventoryTransformer(BaseTransformer):
    """
    Transformer for product inventory data.
    
    This transformer converts product inventory data to the format required by
    the ProductStorage model, including resolving product references by SKU.
    """
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform product inventory data.
        
        Args:
            source_data: List of dictionaries containing product inventory data
            
        Returns:
            List of dictionaries in the format required by ProductStorage model
        """
        transformed_records = []
        
        for record in source_data:
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Resolve product by SKU if SKU is provided
            if 'product_sku' in transformed and 'product' not in transformed:
                try:
                    product_sku = transformed.pop('product_sku')
                    product = VariantProduct.objects.get(sku=product_sku)
                    transformed['product'] = product
                except VariantProduct.DoesNotExist:
                    logger.warning(
                        f"Product with SKU {product_sku} not found, skipping record"
                    )
                    continue
            
            # Set default values for required fields
            transformed.setdefault('quantity', 1)
            transformed.setdefault('reservation_status', 'AVAILABLE')
            
            transformed_records.append(transformed)
            
        logger.info(
            f"Transformed {len(transformed_records)} product inventory records"
        )
        return transformed_records 