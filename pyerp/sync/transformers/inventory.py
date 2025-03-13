"""
Transformers for inventory data from legacy systems.
"""

from typing import Dict, Any, List
from decimal import Decimal

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
    Transformer for box type data from the legacy system.
    
    This transformer converts box type data from the parameter table
    to the format required by the BoxType model.
    """
    
    # Define color mapping for standardization
    COLOR_MAPPING = {
        'Blau': 'blue',
        'Gelb': 'yellow',
        'Grün': 'green',
        'Rot': 'red',
        'Grau': 'gray',
        'Orange': 'orange',
        'Schwarz': 'black',
        'Transparent': 'transparent',
        'Weiß': 'white',
    }
    
    def transform(
        self, source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform box type data from the parameter table.
        
        Args:
            source_data: List of dictionaries containing parameter records
            
        Returns:
            List of dictionaries in the format required by BoxType model
        """
        transformed_records = []
        
        # Filter for parameter records with scope 'Schüttentypen'
        schuettentypen_records = [
            record for record in source_data 
            if record.get('scope') == 'Schüttentypen'
        ]
        
        if not schuettentypen_records:
            logger.warning("No Schüttentypen records found in parameter table")
            return []
        
        # Extract box types from the data_ field
        for record in schuettentypen_records:
            if 'data_' not in record or not record['data_']:
                logger.warning(
                    f"Record {record.get('id')} has no data_ field"
                )
                continue
                
            try:
                box_types_data = record['data_'].get('Schüttentypen', [])
                if not box_types_data:
                    logger.warning(
                        f"No Schüttentypen data found in record {record.get('id')}"
                    )
                    continue
                    
                for box_type in box_types_data:
                    transformed = self._transform_box_type(box_type)
                    if transformed:
                        transformed_records.append(transformed)
            except Exception as e:
                logger.error(f"Error processing box type data: {e}")
                continue
        
        logger.info(
            f"Transformed {len(transformed_records)} box type records"
        )
        return transformed_records
    
    def _transform_box_type(
        self, box_type: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform a single box type record.
        
        Args:
            box_type: Dictionary containing box type data
            
        Returns:
            Dictionary in the format required by BoxType model
        """
        # Skip empty or invalid records
        if not box_type.get('Type'):
            logger.warning(
                f"Skipping box type with no Type field: {box_type}"
            )
            return None
            
        # Extract the name and color from the Type field
        name = box_type.get('Type', '')
        color = self._extract_color(name)
        
        # Create description with manufacturer and part number
        description = (
            f"{box_type.get('Hersteller', '')} "
            f"{box_type.get('Hersteller_Art_Nr', '')}"
        ).strip()
        
        # Add color information to description
        if color != 'other':
            description += f" - Color: {color}"
            
        # Add dimensions to description
        dimensions = []
        if box_type.get('Box_Länge'):
            dimensions.append(
                f"Length: {box_type.get('Box_Länge')}mm"
            )
        if box_type.get('Box_Breite'):
            dimensions.append(
                f"Width: {box_type.get('Box_Breite')}mm"
            )
        if box_type.get('Box_Höhe'):
            dimensions.append(
                f"Height: {box_type.get('Box_Höhe')}mm"
            )
            
        if dimensions:
            description += f" - Dimensions: {', '.join(dimensions)}"
            
        # Add weight information to description
        if box_type.get('Box_Gewicht'):
            description += f" - Empty Weight: {box_type.get('Box_Gewicht')}g"
            
        if (box_type.get('Trenner_Gewicht') and 
                float(box_type.get('Trenner_Gewicht', 0)) > 0):
            description += (
                f" - Divider Weight: {box_type.get('Trenner_Gewicht')}g"
            )
        
        # Convert dimensions from mm to cm (divide by 10)
        length = self._convert_to_decimal(box_type.get('Box_Länge'))
        width = self._convert_to_decimal(box_type.get('Box_Breite'))
        height = self._convert_to_decimal(box_type.get('Box_Höhe'))
        
        # Convert weight from g to kg (divide by 1000)
        weight_capacity = self._convert_to_decimal(
            box_type.get('Box_Gewicht'), 
            unit_conversion=0.001,
            round_to=2
        )
        
        # Map fields from the box type data to the BoxType model
        transformed = {
            'name': name,
            'description': description,
            'length': length,
            'width': width,
            'height': height,
            'weight_capacity': weight_capacity,
            'slot_count': int(box_type.get('Slots', 1)),
            'slot_naming_scheme': 'numeric',  # Default to numeric naming scheme
            'legacy_id': str(box_type.get('id', '')),
            'is_synchronized': True,
        }
        
        return transformed
    
    def _extract_color(self, name: str) -> str:
        """
        Extract color from the box type name.
        
        Args:
            name: Box type name
            
        Returns:
            Standardized color name
        """
        for german_color, english_color in self.COLOR_MAPPING.items():
            if german_color in name:
                return english_color
        return 'other'
    
    def _convert_to_decimal(
        self, value, unit_conversion=0.1, round_to=2
    ) -> Decimal:
        """
        Convert a value to a decimal, handling None and zero values.
        
        Args:
            value: Value to convert
            unit_conversion: Factor to convert units (default: 0.1 for mm to cm)
            round_to: Number of decimal places to round to
            
        Returns:
            Decimal value or None if conversion fails
        """
        if value is None:
            return None
            
        try:
            decimal_value = float(value)
            # Apply unit conversion if value is positive
            if decimal_value > 0:
                # Convert to Decimal with exact decimal places
                converted = decimal_value * unit_conversion
                # Format to exactly 2 decimal places
                return Decimal(f"{converted:.2f}")
            return None
        except (ValueError, TypeError):
            return None


class BoxTransformer(BaseTransformer):
    """
    Transformer for box data.
    
    This transformer converts box data to the format required by the Box model.
    """
    
    # Define purpose mapping based on box characteristics
    PURPOSE_MAPPING = {
        'lager': 'STORAGE',
        'picken': 'PICKING',
        'pick': 'PICKING',
        'transport': 'TRANSPORT',
        'werkstatt': 'WORKSHOP',
    }
    
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
            
            # Determine purpose based on box type or name
            purpose = self._determine_purpose(record)
            transformed.setdefault('purpose', purpose)
            
            transformed_records.append(transformed)
            
        logger.info(f"Transformed {len(transformed_records)} box records")
        return transformed_records
    
    def _determine_purpose(self, record: Dict[str, Any]) -> str:
        """
        Determine the purpose of the box based on its characteristics.
        
        Args:
            record: Dictionary containing box data
            
        Returns:
            Purpose of the box (STORAGE, PICKING, TRANSPORT, WORKSHOP)
        """
        # Check if purpose is explicitly provided
        if 'purpose' in record:
            purpose = record['purpose'].upper()
            if purpose in ['STORAGE', 'PICKING', 'TRANSPORT', 'WORKSHOP']:
                return purpose
        
        # Check if box type name contains purpose indicators
        box_type_name = ''
        if 'box_type_name' in record:
            box_type_name = record['box_type_name'].lower()
        elif 'box_type' in record and hasattr(record['box_type'], 'name'):
            box_type_name = record['box_type'].name.lower()
        
        # Check for purpose indicators in the name
        for keyword, purpose in self.PURPOSE_MAPPING.items():
            if keyword in box_type_name:
                return purpose
        
        # Default to storage
        return 'STORAGE'


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