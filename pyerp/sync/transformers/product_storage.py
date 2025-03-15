"""
Transformer for ProductStorage model.

This module contains the transformer for synchronizing product storage data
from the legacy ERP system to the new system.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation
import json
import logging
import math
import re
from datetime import datetime

from pyerp.business_modules.inventory.models import (
    ProductStorage, BoxSlot, Box, StorageLocation
)
from pyerp.business_modules.products.models import VariantProduct
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.sync.exceptions import TransformError


logger = logging.getLogger(__name__)


def parse_decimal(value: str) -> Decimal:
    """
    Parse a decimal value from a string, handling various formats.
    
    Args:
        value: The string value to parse
        
    Returns:
        Decimal value, or 0 if parsing fails
    """
    if not value:
        return Decimal('0')
        
    try:
        # Remove any non-numeric characters except decimal point and minus sign
        clean_value = re.sub(r'[^\d.-]', '', str(value))
        return Decimal(clean_value)
    except (ValueError, TypeError, decimal.InvalidOperation):
        return Decimal('0')


class ProductStorageTransformer(BaseTransformer):
    """
    Transformer for product storage data.
    
    This transformer handles the synchronization of product storage data from the legacy
    Artikel_Lagerorte table to the ProductStorage model.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the transformer with caches for products and boxes."""
        super().__init__(*args, **kwargs)
        self._product_cache = {}
        self._storage_location_cache = {}
        self._box_slot_cache = {}
        self.log = logger

    def _get_product(self, product_id: str) -> Optional[VariantProduct]:
        """
        Get a product by ID, with caching to improve performance.
        
        Args:
            product_id: ID of the product to find
            
        Returns:
            VariantProduct instance or None if not found
        """
        from pyerp.business_modules.products.models import VariantProduct
            
        if not product_id:
            return None
            
        if product_id not in self._product_cache:
            # Log the product_id format for debugging
            self.log.debug(f"Looking for product with ID: '{product_id}'")
            
            try:
                # First try to find by refOld - this is the key link for legacy sync
                self._product_cache[product_id] = VariantProduct.objects.get(
                    refOld=product_id
                )
                self.log.debug(f"Found by refOld: {self._product_cache[product_id]}")
            except VariantProduct.DoesNotExist:
                # If not found by refOld, try by legacy_id
                try:
                    self._product_cache[product_id] = VariantProduct.objects.get(
                        legacy_id=product_id
                    )
                    self.log.debug(f"Found by legacy_id: {self._product_cache[product_id]}")
                except VariantProduct.DoesNotExist:
                    # If not found, try by sku
                    try:
                        self._product_cache[product_id] = VariantProduct.objects.get(
                            sku=product_id
                        )
                        self.log.debug(f"Found by sku: {self._product_cache[product_id]}")
                    except VariantProduct.DoesNotExist:
                        # If still not found, try by legacy_sku
                        try:
                            self._product_cache[product_id] = VariantProduct.objects.get(
                                legacy_sku=product_id
                            )
                            self.log.debug(
                                f"Found by legacy_sku: {self._product_cache[product_id]}"
                            )
                        except VariantProduct.DoesNotExist:
                            self.log.info(
                                f"Product with ID {product_id} not found using any lookup"
                            )
                            return None
        
        return self._product_cache[product_id]

    def _get_storage_location(self, location_uuid: str) -> Optional[StorageLocation]:
        """
        Get a storage location by UUID, with caching for performance.
        
        Args:
            location_uuid: UUID of the storage location to find
            
        Returns:
            StorageLocation instance or None if not found
        """
        from pyerp.business_modules.inventory.models import StorageLocation
            
        if not location_uuid:
            return None
            
        if location_uuid not in self._storage_location_cache:
            # Log the UUID format for debugging
            self.log.debug(f"Looking for storage location with UUID: '{location_uuid}'")
            
            try:
                # First try to find by legacy_id (UUID)
                self._storage_location_cache[location_uuid] = StorageLocation.objects.get(
                    legacy_id=location_uuid
                )
                self.log.debug(
                    f"Found storage location by UUID: {self._storage_location_cache[location_uuid]}"
                )
            except StorageLocation.DoesNotExist:
                # If not found by UUID, try to find by ID
                # Extract the ID from the UUID in the legacy database
                try:
                    # Get the ID from the legacy database
                    from pyerp.external_api.legacy_erp.client import LegacyERPClient
                    client = LegacyERPClient(environment="live")
                    
                    # Query the legacy database for the storage location
                    df = client.fetch_table(
                        table_name="Stamm_Lagerorte",
                        filter_query=[["UUID", "==", location_uuid]]
                    )
                    
                    if not df.empty:
                        # Get the ID_Lagerort from the result
                        id_lagerort = df['ID_Lagerort'].iloc[0]
                        self.log.info(f"Found ID_Lagerort {id_lagerort} for UUID {location_uuid} in legacy database")
                        
                        # Try to find the storage location by ID
                        try:
                            self._storage_location_cache[location_uuid] = StorageLocation.objects.get(
                                legacy_id=str(id_lagerort)
                            )
                            self.log.info(
                                f"Found storage location by ID: {self._storage_location_cache[location_uuid]}"
                            )
                        except StorageLocation.DoesNotExist:
                            self.log.warning(f"Storage location with ID {id_lagerort} not found")
                            return None
                    else:
                        self.log.warning(f"Storage location with UUID {location_uuid} not found in legacy database")
                        return None
                except Exception as e:
                    self.log.error(f"Error querying legacy database: {e}")
                    return None
        
        return self._storage_location_cache.get(location_uuid)
    
    def _get_box_slot(self, box_id: str, legacy_slot_id: Optional[str] = None) -> Optional['BoxSlot']:
        """
        Get a BoxSlot instance by box ID and optionally slot ID.
        
        Args:
            box_id: The legacy ID of the box
            legacy_slot_id: The legacy ID of the slot (optional)
            
        Returns:
            BoxSlot instance or None if not found
        """
        from pyerp.business_modules.inventory.models import Box, BoxSlot
        
        # Create a cache key from both IDs
        cache_key = f"{box_id}:{legacy_slot_id or '1'}"
        
        if cache_key not in self._box_slot_cache:
            try:
                # First try to find by box and slot legacy ID
                if legacy_slot_id:
                    self._box_slot_cache[cache_key] = BoxSlot.objects.get(
                        box__legacy_id=box_id, 
                        legacy_slot_id=legacy_slot_id
                    )
                    self.log.debug(
                        f"Found BoxSlot by box and slot ID: {self._box_slot_cache[cache_key]}"
                    )
                else:
                    # If no slot ID, try to find the first slot for this box
                    try:
                        box = Box.objects.get(legacy_id=box_id)
                        self._box_slot_cache[cache_key] = box.slots.first()
                        if self._box_slot_cache[cache_key]:
                            self.log.debug(
                                f"Found first slot for box: {self._box_slot_cache[cache_key]}"
                            )
                        else:
                            self.log.warning(f"No slots found for box ID {box_id}")
                            return None
                    except Box.DoesNotExist:
                        self.log.warning(f"Box with legacy_id={box_id} not found")
                        return None
            except BoxSlot.DoesNotExist:
                self.log.warning(
                    f"BoxSlot with box__legacy_id={box_id} and legacy_slot_id={legacy_slot_id} not found"
                )
                return None
                
        return self._box_slot_cache.get(cache_key)
    
    def _parse_quantity(self, quantity_str: Any) -> int:
        """
        Parse quantity string to integer, handling various formats.
        
        Args:
            quantity_str: The quantity value to parse
            
        Returns:
            Integer quantity value
        """
        import math
        import re
        
        if quantity_str is None:
            return 0
            
        if isinstance(quantity_str, (int, float)):
            # Handle NaN values
            if isinstance(quantity_str, float) and math.isnan(quantity_str):
                return 0
            return int(quantity_str)
            
        try:
            quantity_str = str(quantity_str).strip()
            if not quantity_str:
                return 0
                
            # Remove any non-numeric characters
            quantity_str = re.sub(r'[^\d.-]', '', quantity_str)
            if not quantity_str:
                return 0
                
            quantity = float(quantity_str)
            if math.isnan(quantity):
                return 0
                
            return int(quantity)
        except (ValueError, TypeError):
            self.log.warning(f"Failed to parse quantity: {quantity_str}")
            return 0

    def _determine_status(self, data: Dict[str, Any]) -> str:
        """
        Determine the reservation status based on the data.
        
        Args:
            data: The source data record
            
        Returns:
            Reservation status string
        """
        from pyerp.business_modules.inventory.models import ProductStorage
        
        # Check for reservation indicators
        reserved = data.get('Reserved')
        if reserved and str(reserved).strip().upper() in ('TRUE', '1', 'Y', 'YES'):
            return ProductStorage.ReservationStatus.RESERVED
            
        # Check for order references
        order_ref = data.get('Auftrags_Nr')
        if order_ref and str(order_ref).strip() not in ('0', ''):
            return ProductStorage.ReservationStatus.ALLOCATED
            
        # Default to available
        return ProductStorage.ReservationStatus.AVAILABLE

    def transform_artikel_lagerorte(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform data from Artikel_Lagerorte table to ProductStorage model format.
        
        Args:
            data: List of dictionaries containing Artikel_Lagerorte data
            
        Returns:
            List of dictionaries for ProductStorage model
        """
        transformed_records = []
        
        for record in data:
            try:
                # Get product ID
                product_id = record.get("ID_Artikel_Stamm")
                if not product_id:
                    self.log.warning(f"Missing product ID in record {record.get('UUID')}")
                    continue
                
                # Get product
                product = self._get_product(product_id)
                if not product:
                    self.log.info(f"Product not found for ID {product_id}, skipping record")
                    continue
                    
                # Get storage location
                location_uuid = record.get("UUID_Stamm_Lagerorte")
                if not location_uuid:
                    self.log.warning(f"Missing storage location UUID in record {record.get('UUID')}")
                    continue
                    
                storage_location = self._get_storage_location(location_uuid)
                if not storage_location:
                    self.log.warning(f"Storage location not found for UUID {location_uuid}, skipping record")
                    continue
                
                # Parse quantity
                quantity = self._parse_quantity(record.get("Bestand", 0))
                
                # Determine status
                status = self._determine_status(record)
                
                # Create transformed record
                transformed = {
                    'legacy_id': record.get('UUID', ''),
                    'product': product,
                    'storage_location': storage_location,
                    'quantity': quantity,
                    'reservation_status': status,
                }
                
                # Add reservation reference if present
                order_ref = record.get('Auftrags_Nr')
                if order_ref and str(order_ref).strip() not in ('0', ''):
                    transformed['reservation_reference'] = str(order_ref).strip()
                
                transformed_records.append(transformed)

            except Exception as e:
                self.log.error(f"Error transforming record: {e}")
                continue
        
        self.log.info(f"Transformed {len(transformed_records)} product storage records")
        return transformed_records
    
    def transform_lager_schuetten(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        This method is no longer used in the dual-table structure.
        
        For the new architecture, BoxStorageTransformer handles Lager_Schuetten data.
        This method returns an empty list to maintain compatibility with existing code.
        """
        self.log.info("transform_lager_schuetten is deprecated. Use BoxStorageTransformer instead.")
        return []
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform source data based on the configured source table."""
        # Get the source type from the configuration
        source = self.config.get('source', 'Artikel_Lagerorte')
        self.log.info(f"Transforming data from {source}")
        
        # Select the appropriate transformation method based on the source
        if source == 'Artikel_Lagerorte':
            return self.transform_artikel_lagerorte(source_data)
        elif source == 'Lager_Schuetten':
            return self.transform_lager_schuetten(source_data)
        elif source == 'combined':
            # This is a deprecated option, just use Artikel_Lagerorte for simplicity
            self.log.warning("Combined source is deprecated. Use separate transformers for each table.")
            return self.transform_artikel_lagerorte(source_data)
        else:
            raise TransformError(f"Unknown source table: {source}")


class BoxStorageTransformer(BaseTransformer):
    """
    Transformer for box storage data from Lager_Schuetten.
    
    This transformer handles the synchronization of box storage data from the legacy
    Lager_Schuetten table to the BoxStorage model.
    """
    def __init__(self, *args, **kwargs):
        """Initialize the transformer."""
        super().__init__(*args, **kwargs)
        self._product_storage_cache = {}
        self._box_slot_cache = {}
        self.log = logger

    def _get_product_storage(self, uuid: str) -> Optional['ProductStorage']:
        """
        Get a ProductStorage instance by legacy ID.
        
        Args:
            uuid: The legacy UUID of the Artikel_Lagerorte record
            
        Returns:
            ProductStorage instance or None if not found
        """
        from pyerp.business_modules.inventory.models import ProductStorage
            
        if uuid not in self._product_storage_cache:
            try:
                self._product_storage_cache[uuid] = ProductStorage.objects.get(
                    legacy_id=uuid
                )
                self.log.debug(f"Found ProductStorage: {self._product_storage_cache[uuid]}")
            except ProductStorage.DoesNotExist:
                self.log.warning(f"ProductStorage with legacy_id={uuid} not found")
                return None
                
        return self._product_storage_cache[uuid]
    
    def _get_box_slot(self, box_id: str, legacy_slot_id: Optional[str] = None) -> Optional['BoxSlot']:
        """
        Get a BoxSlot instance by box ID and optionally slot ID.
        
        Args:
            box_id: The legacy ID of the box
            legacy_slot_id: The legacy ID of the slot (optional)
            
        Returns:
            BoxSlot instance or None if not found
        """
        from pyerp.business_modules.inventory.models import Box, BoxSlot
        
        # Create a cache key from both IDs
        cache_key = f"{box_id}:{legacy_slot_id or '1'}"
        
        if cache_key not in self._box_slot_cache:
            try:
                # First try to find by box and slot legacy ID
                if legacy_slot_id:
                    self._box_slot_cache[cache_key] = BoxSlot.objects.get(
                        box__legacy_id=box_id, 
                        legacy_slot_id=legacy_slot_id
                    )
                    self.log.debug(
                        f"Found BoxSlot by box and slot ID: {self._box_slot_cache[cache_key]}"
                    )
                else:
                    # If no slot ID, try to find the first slot for this box
                    try:
                        box = Box.objects.get(legacy_id=box_id)
                        self._box_slot_cache[cache_key] = box.slots.first()
                        if self._box_slot_cache[cache_key]:
                            self.log.debug(
                                f"Found first slot for box: {self._box_slot_cache[cache_key]}"
                            )
                        else:
                            self.log.warning(f"No slots found for box ID {box_id}")
                            return None
                    except Box.DoesNotExist:
                        self.log.warning(f"Box with legacy_id={box_id} not found")
                        return None
            except BoxSlot.DoesNotExist:
                self.log.warning(
                    f"BoxSlot with box__legacy_id={box_id} and legacy_slot_id={legacy_slot_id} not found"
                )
                return None
                
        return self._box_slot_cache.get(cache_key)
    
    def _extract_box_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract box data from Lager_Schuetten record.
        
        Args:
            data: Lager_Schuetten record data
            
        Returns:
            Dictionary with extracted data
        """
        # Extract data from the JSON data_ field if present
        box_data = {}
        json_data = data.get('data_', {})
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                self.log.warning(f"Failed to parse JSON data: {json_data}")
                json_data = {}
                
        # Extract key fields
        box_data['legacy_id'] = data.get('ID')
        box_data['box_id'] = data.get('ID_Stamm_Lager_Schuetten')
        box_data['artikel_lagerorte_uuid'] = data.get('UUID_Artikel_Lagerorte')
        
        # Extract additional data from JSON
        box_data['schuetten_id'] = json_data.get('Schuetten_ID')
        box_data['artikel_lagerort'] = json_data.get('Artikel_Lagerort')
        box_data['stamm_lagerort'] = json_data.get('Stamm_Lagerort')
        
        # Extract slot information if available
        relation_data = data.get('Relation_95_zurueck', {})
        if relation_data:
            try:
                slot_data = json.loads(relation_data) if isinstance(relation_data, str) else relation_data
                box_data['slot_id'] = slot_data.get('ID_Lager_Schuetten_Slots')
            except (json.JSONDecodeError, AttributeError):
                self.log.warning(f"Failed to parse slot relation data: {relation_data}")
        
        return box_data
    
    def _parse_quantity(self, quantity_str: Any) -> int:
        """
        Parse a quantity value, handling various formats.
        
        Args:
            quantity_str: The quantity value to parse
            
        Returns:
            Integer quantity value, defaults to 0 for invalid input
        """
        if quantity_str is None:
            return 0
            
        if isinstance(quantity_str, (int, float)):
            # Handle NaN values
            if isinstance(quantity_str, float) and math.isnan(quantity_str):
                return 0
            return int(quantity_str)
            
        try:
            quantity_str = str(quantity_str).strip()
            if not quantity_str:
                return 0
                
            # Remove any non-numeric characters
            quantity_str = re.sub(r'[^\d.-]', '', quantity_str)
            if not quantity_str:
                return 0
                
            quantity = float(quantity_str)
            if math.isnan(quantity):
                return 0
                
            return int(quantity)
        except (ValueError, TypeError):
            self.log.warning(f"Failed to parse quantity: {quantity_str}")
            return 0
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform box storage data from Lager_Schuetten.
        
        Args:
            source_data: List of dictionaries containing Lager_Schuetten data
            
        Returns:
            List of dictionaries for BoxStorage model
        """
        transformed_records = []
        
        for data in source_data:
            try:
                # Extract basic box data
                box_data = self._extract_box_data(data)
                
                # Skip if missing essential data
                if not box_data['artikel_lagerorte_uuid']:
                    self.log.warning(
                        f"Missing artikel_lagerorte_uuid in record {box_data['legacy_id']}, skipping"
                    )
                    continue
                    
                # Get ProductStorage reference
                product_storage = self._get_product_storage(box_data['artikel_lagerorte_uuid'])
                if not product_storage:
                    self.log.warning(
                        f"ProductStorage not found for UUID {box_data['artikel_lagerorte_uuid']}, skipping"
                    )
                    continue
                    
                # Get BoxSlot reference
                box_slot = self._get_box_slot(box_data['box_id'], box_data.get('slot_id'))
                if not box_slot:
                    self.log.warning(
                        f"BoxSlot not found for box {box_data['box_id']} and slot {box_data.get('slot_id')}, skipping"
                    )
                    continue
                
                # Prepare record for BoxStorage
                transformed = {
                    'legacy_id': box_data['legacy_id'],
                    'product_storage': product_storage,
                    'box_slot': box_slot,
                    'quantity': self._parse_quantity(data.get('Menge', 1)),
                    'position_in_slot': '',  # Default empty position
                    'batch_number': data.get('Chargen_Nr', ''),
                }
                
                # Add date fields if available
                if data.get('Ablaufdatum'):
                    try:
                        transformed['expiry_date'] = parse_date(data['Ablaufdatum'])
                    except Exception as e:
                        self.log.warning(f"Failed to parse expiry date: {e}")
                
                transformed_records.append(transformed)
                
            except Exception as e:
                self.log.error(f"Error transforming record: {e}")
                continue
        
        self.log.info(f"Transformed {len(transformed_records)} box storage records")
        return transformed_records 