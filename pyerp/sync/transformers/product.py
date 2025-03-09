"""Product data transformer implementation."""

import logging
from typing import Any, Dict, List
import pandas as pd

from .base import BaseTransformer, ValidationError

# Configure database logging to ERROR level
db_logger = logging.getLogger('django.db.backends')
db_logger.setLevel(logging.ERROR)

# Configure logger
logger = logging.getLogger("pyerp.sync.transformers.product")
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False


class ProductTransformer(BaseTransformer):
    """Transformer for product data."""

    def transform(
        self, source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform product data from legacy format.
        
        Args:
            source_data: List of source product records
            
        Returns:
            List of transformed product records
            
        Raises:
            ValueError: If source data is invalid
        """
        logger.info(f"Starting transformation of {len(source_data)} records")
        logger.info(f"Field mappings: {self.field_mappings}")
        
        transformed_records = []
        
        for record in source_data:
            try:
                logger.info(f"Processing record: {record}")
                
                # Apply base field mappings
                transformed = self.apply_field_mappings(record)
                logger.info(f"After field mappings: {transformed}")
                
                # Handle modified_time field - ensure it's a valid datetime or None
                if 'modified_time' in transformed:
                    try:
                        if pd.isna(transformed['modified_time']):
                            transformed['modified_time'] = None
                        else:
                            # Try to parse as datetime if it's a string
                            if isinstance(
                                transformed['modified_time'], str
                            ):
                                transformed['modified_time'] = pd.to_datetime(
                                    transformed['modified_time']
                                )
                    except Exception as e:
                        logger.warning(
                            f"Error processing modified_time: {e}"
                        )
                        transformed['modified_time'] = None
                
                # Handle empty or null name field
                if not transformed.get('name'):
                    # Try to generate a name from SKU or legacy_id
                    if transformed.get('sku'):
                        transformed['name'] = (
                            f"Product {transformed['sku']}"
                        )
                    elif transformed.get('legacy_id'):
                        transformed['name'] = (
                            f"Product {transformed['legacy_id']}"
                        )
                    else:
                        transformed['name'] = "Unnamed Product"
                    logger.info(
                        f"Generated default name: {transformed['name']}"
                    )
                
                # Extract SKU components if needed
                sku = transformed.get('sku')
                logger.info(f"SKU value: {sku}")
                
                if sku is not None:
                    try:
                        sku_parts = self._parse_sku(sku)
                        logger.info(f"SKU parts: {sku_parts}")
                        transformed.update(sku_parts)
                    except Exception as e:
                        logger.warning(
                            "Error parsing SKU: %s",
                            str(e),
                            extra={
                                'record': record,
                                'sku': sku
                            }
                        )
                        # Set default values if SKU parsing fails
                        transformed.update({
                            'base_sku': str(sku).strip() if sku else '',
                            'variant_code': ''
                        })
                else:
                    logger.warning(
                        "No SKU found in transformed record",
                        extra={'record': record}
                    )
                    transformed.update({
                        'base_sku': '',
                        'variant_code': ''
                    })
                
                # Apply price transformations
                if 'Preise' in record:
                    price_data = self._transform_prices(record['Preise'])
                    transformed.update(price_data)
                
                # Apply custom transformations
                transformed = self.apply_custom_transformers(
                    transformed, record
                )
                
                transformed_records.append(transformed)
                logger.info(f"Final transformed record: {transformed}")
                
            except Exception as e:
                logger.error(
                    "Error transforming record: %s",
                    str(e),
                    extra={'record': record}
                )
                continue
        
        logger.info(f"Completed transformation of {len(transformed_records)} records")
        return transformed_records

    def _parse_sku(self, sku: str) -> Dict[str, str]:
        """Parse SKU into components.
        
        Args:
            sku: Product SKU to parse
            
        Returns:
            Dictionary with SKU components
        """
        result = {
            'base_sku': '',
            'variant_code': ''
        }
        
        if sku is None:
            logger.warning("Received None value for SKU")
            return result
            
        # Ensure sku is a string and strip whitespace
        try:
            sku = str(sku).strip()
        except (AttributeError, TypeError):
            logger.warning(f"Could not convert SKU to string: {sku}")
            return result
            
        if not sku:
            return result
        
        # Split at last hyphen for variant codes
        try:
            if '-' in sku:
                parts = sku.rsplit('-', 1)
                if len(parts) == 2 and all(parts):
                    result['base_sku'] = parts[0]
                    result['variant_code'] = parts[1]
                else:
                    result['base_sku'] = sku
            else:
                result['base_sku'] = sku
        except Exception as e:
            logger.warning(f"Error splitting SKU {sku}: {e}")
            result['base_sku'] = sku
        
        return result

    def _transform_prices(self, price_data: str) -> Dict[str, float]:
        """Transform price data from legacy format.
        
        Args:
            price_data: Price data string from legacy system
            
        Returns:
            Dictionary with transformed price fields
        """
        prices = {}
        
        try:
            # Parse price string (format: "Laden:10.00|Handel:8.00|...")
            if isinstance(price_data, str):
                for price_item in price_data.split('|'):
                    if ':' in price_item:
                        key, value = price_item.split(':', 1)
                        try:
                            prices[f"price_{key.lower()}"] = float(value)
                        except ValueError:
                            logger.warning(
                                f"Invalid price value: {value}",
                                extra={'price_item': price_item}
                            )
        except Exception as e:
            logger.error(
                f"Error parsing price data: {e}",
                extra={'price_data': price_data}
            )
        
        return prices

    def validate_record(
        self, record: Dict[str, Any]
    ) -> List[ValidationError]:
        """Validate a transformed product record.
        
        Args:
            record: Record to validate
            
        Returns:
            List of validation errors
        """
        errors = super().validate_record(record)
        
        # Validate required fields
        required_fields = ['sku', 'name']
        for field in required_fields:
            if not record.get(field):
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing or empty"
                ))
        
        # Validate SKU format
        if record.get('sku'):
            if not self._is_valid_sku(record['sku']):
                errors.append(ValidationError(
                    field='sku',
                    message="Invalid SKU format"
                ))
        
        # Validate prices
        price_fields = [
            key for key in record.keys() if key.startswith('price_')
        ]
        for field in price_fields:
            price = record[field]
            if not isinstance(price, (int, float)) or price < 0:
                errors.append(ValidationError(
                    field=field,
                    message="Price must be a non-negative number",
                    context={'value': price}
                ))
        
        return errors

    def _is_valid_sku(self, sku: str) -> bool:
        """Check if SKU format is valid.
        
        Args:
            sku: SKU to validate
            
        Returns:
            True if SKU is valid, False otherwise
        """
        if not isinstance(sku, str):
            return False
            
        # SKU must be non-empty and contain only allowed characters
        if not sku or not all(c.isalnum() or c == '-' for c in sku):
            return False
            
        # If SKU contains variant code, validate format
        if '-' in sku:
            base_sku, variant_code = sku.rsplit('-', 1)
            if not base_sku or not variant_code:
                return False
                
        return True 