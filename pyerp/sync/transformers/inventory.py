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
    """Transforms legacy storage location data into StorageLocation format.
    
    This transformer handles the conversion of legacy storage location 
    records into a format compatible with the StorageLocation model.
    """

    def transform(self, source_data: List[Dict]) -> List[Dict]:
        """Transform legacy storage location data into StorageLocation format.

        Args:
            source_data: List of dictionaries containing legacy storage 
                location data.

        Returns:
            List of transformed dictionaries ready for StorageLocation 
            model.
        """
        transformed_records = []
        logger.info(f"Using field mappings: {self.field_mappings}")

        # Track used location combinations to handle duplicates
        used_combinations = {}

        for record in source_data:
            logger.info(f"Processing record: {record}")

            # Extract legacy_id before applying mappings
            legacy_id_field = self.field_mappings.get('legacy_id', 'ID_Lagerort')
            legacy_id = str(record.get(legacy_id_field)) if record.get(legacy_id_field) is not None else None
            
            if not legacy_id:
                logger.warning(
                    f"Skipping record without legacy_id: {record}"
                )
                continue

            # Initialize transformed record with default values
            transformed = {
                'legacy_id': legacy_id,
                'is_active': True,
                'is_synchronized': False
            }

            # Apply field mappings for all fields
            for target_field, source_field in self.field_mappings.items():
                if source_field in record and record[source_field] is not None:
                    value = record[source_field]
                    # Convert numeric values to strings for unit, compartment, shelf
                    if target_field in ['unit', 'compartment', 'shelf'] and value is not None:
                        try:
                            value = str(int(value))
                        except (ValueError, TypeError):
                            value = str(value) if value else ''
                    transformed[target_field] = value

            # Ensure all required fields for unique constraint are set
            # If not in field mappings, try to extract directly from record
            if 'country' not in transformed and 'Land_LKZ' in record:
                transformed['country'] = record['Land_LKZ'] or ''
            if 'city_building' not in transformed and 'Ort_Gebaeude' in record:
                transformed['city_building'] = record['Ort_Gebaeude'] or ''
            if 'unit' not in transformed and 'Regal' in record:
                try:
                    transformed['unit'] = str(int(record['Regal'])) if record['Regal'] is not None else ''
                except (ValueError, TypeError):
                    transformed['unit'] = str(record['Regal']) if record['Regal'] else ''
            if 'compartment' not in transformed and 'Fach' in record:
                try:
                    transformed['compartment'] = str(int(record['Fach'])) if record['Fach'] is not None else ''
                except (ValueError, TypeError):
                    transformed['compartment'] = str(record['Fach']) if record['Fach'] else ''
            if 'shelf' not in transformed and 'Boden' in record:
                try:
                    transformed['shelf'] = str(int(record['Boden'])) if record['Boden'] is not None else ''
                except (ValueError, TypeError):
                    transformed['shelf'] = str(record['Boden']) if record['Boden'] else ''
            if 'location_code' not in transformed and 'Lagerort' in record:
                transformed['location_code'] = record['Lagerort'] or ''

            # Ensure all required fields have at least empty strings
            for field in ['country', 'city_building', 'unit', 'compartment', 'shelf']:
                if field not in transformed:
                    transformed[field] = ''

            # Create location combination key
            location_key = (
                transformed.get('country', ''),
                transformed.get('city_building', ''),
                transformed.get('unit', ''),
                transformed.get('compartment', ''),
                transformed.get('shelf', '')
            )

            # Handle duplicate combinations
            if location_key in used_combinations:
                used_combinations[location_key] += 1
                # Append suffix to location code
                if 'location_code' in transformed:
                    transformed['location_code'] = (
                        f"{transformed['location_code']}_"
                        f"{used_combinations[location_key]}"
                    )
                # Append suffix to unit to make the combination unique
                if 'unit' in transformed:
                    transformed['unit'] = (
                        f"{transformed['unit']}_"
                        f"{used_combinations[location_key]}"
                    )
            else:
                used_combinations[location_key] = 1

            # Generate descriptive name if not already set
            if 'name' not in transformed:
                name_parts = []
                if transformed.get('country'):
                    name_parts.append(transformed['country'])
                if transformed.get('city_building'):
                    name_parts.append(transformed['city_building'])
                if transformed.get('unit'):
                    name_parts.append(f"R{transformed['unit']}")
                if transformed.get('compartment'):
                    name_parts.append(f"F{transformed['compartment']}")
                if transformed.get('shelf'):
                    name_parts.append(f"B{transformed['shelf']}")
                
                if name_parts:
                    transformed['name'] = '-'.join(
                        str(part) for part in name_parts
                    )
                else:
                    transformed['name'] = f"Location {legacy_id}"

            logger.info(f"After field mappings: {transformed}")
            logger.info(f"Final transformed record: {transformed}")
            transformed_records.append(transformed)

        logger.info(
            f"Transformed {len(transformed_records)} storage location "
            f"records, skipped "
            f"{len(source_data) - len(transformed_records)} records "
            f"without legacy_id"
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
    Transformer for box data from Stamm_Lager_Schuetten table.
    
    This transformer converts legacy box data to the format required by 
    the Box model.
    """
    
    # Define purpose mapping based on box characteristics
    PURPOSE_MAPPING = {
        'lager': 'STORAGE',
        'picken': 'PICKING',
        'pick': 'PICKING',
        'transport': 'TRANSPORT',
        'werkstatt': 'WORKSHOP',
    }
    
    def transform(
        self, source_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Transform box data from Stamm_Lager_Schuetten records.
        
        Args:
            source_data: List of dictionaries containing box data from 
                legacy Stamm_Lager_Schuetten table
            
        Returns:
            List of dictionaries in the format required by Box model
        """
        transformed_records = []
        
        # Get all existing box types for validation
        from pyerp.business_modules.inventory.models import BoxType
        existing_box_types = {
            bt.name: bt for bt in BoxType.objects.all()
        }
        
        for record in source_data:
            # Skip records without data_ field
            if 'data_' not in record:
                msg = f"Record {record.get('ID')} has no data_ field"
                logger.warning(msg)
                continue

            # Extract legacy_id
            legacy_id = (
                str(record.get('ID')) 
                if record.get('ID') is not None 
                else None
            )
            if not legacy_id:
                logger.warning("Record has no ID field")
                continue

            # Extract data from data_ JSON field
            data = record.get('data_', {})
            
            # Extract box type name
            box_type_name = data.get('Schuettentype')
            if not box_type_name:
                msg = f"Record {legacy_id} has no box type"
                logger.warning(msg)
                continue

            # Validate box type exists and get instance
            box_type = existing_box_types.get(box_type_name)
            if not box_type:
                msg = (
                    f"Box type '{box_type_name}' not found "
                    f"for box {legacy_id}"
                )
                logger.error(msg)
                continue

            # Extract storage location code (now optional)
            storage_location_code = data.get('Lagerort')
            if not storage_location_code:
                logger.info(
                    f"Record {legacy_id} has no storage location"
                )
                storage_location_code = None

            # Map purpose from Schuettenzweck
            purpose = data.get('Schuettenzweck', '').lower()
            purpose = self.PURPOSE_MAPPING.get(purpose, 'STORAGE')

            # Extract parent box ID from URI if present
            parent_box_legacy_id = None
            if 'viele_schuetten' in record:
                try:
                    parent_data = record['viele_schuetten']
                    if (isinstance(parent_data, dict) and 
                            '__deferred' in parent_data):
                        uri = parent_data['__deferred'].get('uri', '')
                        if uri:
                            # Extract ID from URI pattern
                            import re
                            pattern = r'Stamm_Lager_Schuetten\[(\d+)\]'
                            match = re.search(pattern, uri)
                            if match:
                                parent_box_legacy_id = match.group(1)
                    elif (isinstance(parent_data, str) and 
                          parent_data.isdigit()):
                        parent_box_legacy_id = parent_data
                except (KeyError, IndexError, AttributeError) as e:
                    msg = (
                        f"Could not extract parent box ID from "
                        f"{record.get('viele_schuetten')}: {str(e)}"
                    )
                    logger.warning(msg)

            # Build transformed record
            transformed = {
                'legacy_id': legacy_id,
                'code': f'SC{legacy_id}',
                'box_type': box_type,  # Set the actual BoxType instance
                'box_type_name': box_type_name,  # Keep name for reference
                'storage_location_code': storage_location_code,
                'purpose': purpose,
                'max_slots': record.get('max_Anzahl_Slots', 1),
                'unit_count': data.get('Anzahl_Schuetteneinheiten', 1),
                'last_labelprint_date': record.get('Druckdatum'),
                'last_labelprint_time': record.get('Druckzeit'),
                'parent_box_legacy_id': parent_box_legacy_id,
                'status': 'AVAILABLE',
                'is_active': True,
                'is_synchronized': True,
            }

            # Add audit fields
            audit_fields = [
                'created_name', 'created_date', 'created_time',
                'modified_name', 'modified_date', 'modified_time'
            ]
            for field in audit_fields:
                if field in record:
                    transformed[field] = record[field]

            transformed_records.append(transformed)

        logger.info(f"Transformed {len(transformed_records)} box records")
        return transformed_records


class BoxSlotTransformer(BaseTransformer):
    """
    Transformer for box slot data from Stamm_Lager_Schuetten_Slots table.
    
    This transformer converts legacy box slot data to the format required by 
    the BoxSlot model.
    """
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform box slot data from Stamm_Lager_Schuetten_Slots records.
        
        Args:
            source_data: List of dictionaries containing box slot data from 
                legacy Stamm_Lager_Schuetten_Slots table
            
        Returns:
            List of dictionaries in the format required by BoxSlot model
        """
        transformed_records = []
        
        # Get all existing boxes for validation
        from pyerp.business_modules.inventory.models import Box
        existing_boxes = {
            str(box.legacy_id): box for box in Box.objects.all()
        }
        
        logger.info(f"Found {len(existing_boxes)} existing boxes for slot assignment")
        
        for record in source_data:
            # Apply field mappings from config
            transformed = self.apply_field_mappings(record)
            
            # Apply custom transformations
            transformed = self.apply_custom_transformers(transformed, record)
            
            # Set legacy_id from ID field
            if 'ID' in record:
                transformed['legacy_id'] = str(record['ID'])
            
            # Extract data from JSON field
            if 'data_' in record and record['data_']:
                try:
                    data_json = record['data_']
                    if isinstance(data_json, str):
                        import json
                        data_json = json.loads(data_json)
                    
                    # Extract slot code
                    if 'Slot_Code' in data_json:
                        transformed['slot_code'] = data_json['Slot_Code']
                    
                    # Extract unit number
                    if 'Einheiten_Nr' in data_json:
                        try:
                            transformed['unit_number'] = int(data_json['Einheiten_Nr'])
                        except (ValueError, TypeError):
                            transformed['unit_number'] = 1
                    
                    # Extract color code
                    if 'Einheitenfabe' in data_json:
                        transformed['color_code'] = str(data_json['Einheitenfabe'])
                except Exception as e:
                    logger.warning(f"Error parsing data_ JSON field: {e}")
            
            # Set legacy_slot_id from ID_Lager_Schuetten_Slots
            if 'ID_Lager_Schuetten_Slots' in record:
                transformed['legacy_slot_id'] = str(record['ID_Lager_Schuetten_Slots'])
            
            # Set slot_number from Lfd_Nr
            if 'Lfd_Nr' in record:
                try:
                    transformed['slot_number'] = int(record['Lfd_Nr'])
                except (ValueError, TypeError):
                    transformed['slot_number'] = 1
            
            # Set order_number from Auftrags_Nr
            if 'Auftrags_Nr' in record:
                transformed['order_number'] = str(record['Auftrags_Nr'])
            
            # Resolve box reference
            box_id = None
            
            # First try to get box ID from ID_Lager_Schuetten_Slots
            # which is the box ID in the Stamm_Lager_Schuetten table
            if 'ID_Lager_Schuetten_Slots' in record:
                box_id = str(record['ID_Lager_Schuetten_Slots'])
            
            # Alternatively, try to get box ID from viele_zu_eins reference
            elif 'viele_zu_eins' in record and record['viele_zu_eins']:
                box_id = str(record['viele_zu_eins'])
            
            # If we have a box ID, try to find the box
            if box_id:
                if box_id in existing_boxes:
                    transformed['box'] = existing_boxes[box_id]
                else:
                    logger.warning(
                        f"Box with legacy_id {box_id} not found, skipping slot record"
                    )
                    continue
            else:
                logger.warning(
                    f"No box ID found for slot record {record.get('ID', 'unknown')}, skipping"
                )
                continue
            
            # Generate barcode if not present
            if 'barcode' not in transformed or not transformed['barcode']:
                box_code = transformed['box'].code
                slot_code = transformed.get('slot_code', '')
                transformed['barcode'] = f"{box_code}.{slot_code}"
            
            # Set default values for required fields
            transformed.setdefault('slot_code', f"S{transformed.get('slot_number', 1)}")
            transformed.setdefault('unit_number', 1)
            transformed.setdefault('color_code', '')
            transformed.setdefault('order_number', '')
            transformed.setdefault('occupied', False)
            
            # Add audit fields
            audit_fields = [
                'created_name', 'created_date', 'created_time',
                'modified_name', 'modified_date', 'modified_time'
            ]
            for field in audit_fields:
                if field in record:
                    transformed[field] = record[field]
            
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