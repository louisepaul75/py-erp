"""
Transformers for inventory data from legacy systems.
"""

from typing import Dict, Any, List
from decimal import Decimal
import json

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
        from pyerp.business_modules.inventory.models import BoxType, StorageLocation
        existing_box_types = {
            bt.name: bt for bt in BoxType.objects.all()
        }
        
        # Get all storage locations by UUID for lookup
        storage_locations_by_uuid = {
            sl.legacy_id: sl for sl in StorageLocation.objects.all()
        }
        
        # Also get storage locations by location_code for fallback lookup
        storage_locations_by_code = {
            sl.location_code: sl for sl in StorageLocation.objects.all() if sl.location_code
        }
        
        # Log the number of storage locations found
        logger.info(f"Found {len(storage_locations_by_uuid)} storage locations by UUID")
        logger.info(f"Found {len(storage_locations_by_code)} storage locations by code")
        
        # Track stats
        boxes_with_location = 0
        boxes_without_location = 0
        boxes_with_location_not_found = 0
        
        for data in source_data:
            # Extract required fields
            legacy_id = data.get('ID')
            if not legacy_id:
                logger.warning(f"Skipping record with missing ID: {data}")
                continue
                
            # Extract box code
            box_code = data.get('Schuettencode', '')
            if not box_code:
                # Generate a code if not provided
                box_code = f"SC{legacy_id}"
                logger.info(f"Generated box code for legacy ID {legacy_id}: {box_code}")
            
            # Extract box type
            box_type_name = data.get('Schuettentyp', '')
            
            # If no box type is specified, use the "Unknown" box type
            if not box_type_name:
                box_type_name = 'Unknown'
                logger.info(f"Box {legacy_id} has no box type specified. Using 'Unknown' box type.")
            
            # Validate box type exists
            if box_type_name in existing_box_types:
                box_type = existing_box_types.get(box_type_name)
            else:
                # If the specified box type doesn't exist, use the "Unknown" box type
                logger.warning(
                    f"Box type '{box_type_name}' not found for box {legacy_id}. "
                    f"Using 'Unknown' box type instead."
                )
                box_type = existing_box_types.get('Unknown')
                
            # If we still don't have a box type, something is wrong
            if not box_type:
                logger.error(
                    f"'Unknown' box type not found. Cannot proceed with import."
                )
                continue
            
            # Extract storage location
            storage_location_code = None
            storage_location_uuid = data.get('UUID_Stamm_Lagerorte')
            storage_location = None
            
            # Step 1: Try to find by UUID from the main field
            if storage_location_uuid:
                logger.debug(f"Box {legacy_id} has direct storage location UUID: {storage_location_uuid}")
                storage_location = storage_locations_by_uuid.get(storage_location_uuid)
                if storage_location:
                    storage_location_code = storage_location.location_code
                    boxes_with_location += 1
                    logger.info(
                        f"Found storage location {storage_location.location_code} "
                        f"for box {legacy_id} using direct UUID {storage_location_uuid}"
                    )
                else:
                    boxes_with_location_not_found += 1
                    logger.warning(
                        f"Storage location with direct UUID {storage_location_uuid} "
                        f"not found for box {legacy_id}"
                    )
            
            # Step 2: If not found and data_ exists, try to extract from JSON
            if not storage_location and data.get('data_'):
                try:
                    if isinstance(data.get('data_'), str):
                        data_json = json.loads(data.get('data_', '{}'))
                    else:
                        data_json = data.get('data_', {})
                    
                    # Check for storage location UUID in data_
                    if data_json.get('Stamm_Lagerort'):
                        storage_location_uuid = data_json.get('Stamm_Lagerort')
                        logger.debug(f"Box {legacy_id} has JSON storage location UUID: {storage_location_uuid}")
                        storage_location = storage_locations_by_uuid.get(storage_location_uuid)
                        if storage_location:
                            storage_location_code = storage_location.location_code
                            boxes_with_location += 1
                            logger.info(
                                f"Found storage location {storage_location.location_code} "
                                f"for box {legacy_id} using JSON UUID {storage_location_uuid}"
                            )
                        else:
                            boxes_with_location_not_found += 1
                            logger.warning(
                                f"Storage location with JSON UUID {storage_location_uuid} "
                                f"not found for box {legacy_id}"
                            )
                    
                    # Also check for storage location code in data_
                    if not storage_location and data_json.get('Lagerort'):
                        location_code = data_json.get('Lagerort')
                        logger.debug(f"Box {legacy_id} has JSON location code: {location_code}")
                        storage_location = storage_locations_by_code.get(location_code)
                        if storage_location:
                            storage_location_code = location_code
                            boxes_with_location += 1
                            logger.info(
                                f"Found storage location {storage_location.location_code} "
                                f"for box {legacy_id} using JSON location code {location_code}"
                            )
                        else:
                            boxes_with_location_not_found += 1
                            logger.warning(
                                f"Storage location with JSON code {location_code} "
                                f"not found for box {legacy_id}"
                            )
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in data_ field: {data.get('data_')}")
            
            # Step 3: If still not found, check if we can find a location using the box code
            if not storage_location and box_code:
                # Try to extract location code from box code if it contains location information
                # Example: If box_code is "DE-Hamburg-R04-F02-B02-123", extract "DE-Hamburg-R04-F02-B02"
                for location_code in storage_locations_by_code.keys():
                    if location_code and box_code.startswith(location_code):
                        storage_location = storage_locations_by_code.get(location_code)
                        if storage_location:
                            storage_location_code = location_code
                            boxes_with_location += 1
                            logger.info(
                                f"Found storage location {storage_location.location_code} "
                                f"for box {legacy_id} by matching box code prefix {location_code}"
                            )
                            break
            
            if not storage_location:
                boxes_without_location += 1
                logger.info(
                    f"Box {legacy_id} with code {box_code} has no storage location"
                )
                storage_location_code = None

            # Map purpose from Schuettenzweck
            purpose = data.get('Schuettenzweck', '').lower()
            purpose = self.PURPOSE_MAPPING.get(purpose, 'STORAGE')

            # Extract parent box ID from URI if present
            parent_box_legacy_id = None
            
            # Create transformed record
            transformed_record = {
                'legacy_id': legacy_id,
                'code': box_code,
                'box_type': box_type,  # Now always has a value (either the actual box type or "Unknown")
                'storage_location': storage_location,  # Use the actual StorageLocation object
                'purpose': purpose,
                'status': 'AVAILABLE',  # Default status
                'barcode': data.get('Barcode', ''),
                'notes': data.get('Bemerkung', ''),
            }
            
            transformed_records.append(transformed_record)
        
        # Log summary statistics
        logger.info(f"Transformed {len(transformed_records)} box records")
        logger.info(f"Boxes with storage location: {boxes_with_location}")
        logger.info(f"Boxes without storage location: {boxes_without_location}")
        logger.info(f"Boxes with storage location reference not found: {boxes_with_location_not_found}")
            
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