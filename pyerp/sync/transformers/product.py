"""Product data transformer implementation."""

import logging
from typing import Any, Dict, List

from .base import BaseTransformer, ValidationError


logger = logging.getLogger(__name__)


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
        transformed_records = []
        
        for record in source_data:
            try:
                # Apply base field mappings
                transformed = self.apply_field_mappings(record)
                
                # Extract SKU components if needed
                if 'sku' in transformed:
                    sku_parts = self._parse_sku(transformed['sku'])
                    transformed.update(sku_parts)
                
                # Apply price transformations
                if 'Preise' in record:
                    price_data = self._transform_prices(record['Preise'])
                    transformed.update(price_data)
                
                # Apply custom transformations
                transformed = self.apply_custom_transformers(
                    transformed, record
                )
                
                transformed_records.append(transformed)
                
            except Exception as e:
                logger.error(
                    f"Error transforming record: {e}",
                    extra={'record': record}
                )
                continue
        
        return transformed_records

    def _parse_sku(self, sku: str) -> Dict[str, str]:
        """Parse SKU into components.
        
        Args:
            sku: Product SKU to parse
            
        Returns:
            Dictionary with SKU components
        """
        result = {
            'base_sku': sku,
            'variant_code': ''
        }
        
        # Split at last hyphen for variant codes
        if '-' in sku:
            parts = sku.rsplit('-', 1)
            if len(parts) == 2:
                result['base_sku'] = parts[0]
                result['variant_code'] = parts[1]
        
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