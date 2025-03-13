"""
Transformer for ProductStorage model.

This module contains the transformer for synchronizing product storage data
from the legacy ERP system to the new system.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation
import json
import logging

from pyerp.business_modules.inventory.models import (
    ProductStorage, BoxSlot, Box
)
from pyerp.business_modules.products.models import VariantProduct
from pyerp.sync.transformers.base import BaseTransformer
from pyerp.sync.exceptions import TransformError


def parse_decimal(value: str) -> Decimal:
    """
    Parse a string to a Decimal, handling various formats.
    
    Args:
        value: String representation of a decimal number
        
    Returns:
        Decimal value
    """
    if not value or value.lower() == 'null':
        return Decimal('0')
    
    # Replace comma with dot for decimal separator
    value = value.replace(',', '.')
    
    # Remove any non-numeric characters except dot
    value = ''.join(c for c in value if c.isdigit() or c == '.')
    
    try:
        return Decimal(value)
    except (ValueError, InvalidOperation):
        return Decimal('0')


class ProductStorageTransformer(BaseTransformer):
    """
    Transformer for ProductStorage model that combines data from Artikel_Lagerorte
    and Lager_Schuetten tables to create/update ProductStorage records.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.log = logging.getLogger(__name__)
        # Cache for box slots to avoid repeated lookups
        self._box_slot_cache = {}
        # Cache for products to avoid repeated lookups
        self._product_cache = {}
        # Get source from config
        self.source = self.config.get('source')

    def _get_product(self, product_id: str) -> Optional[VariantProduct]:
        """
        Get product instance from cache or database.
        """
        if product_id not in self._product_cache:
            # Log the product_id format for debugging
            self.log.debug(f"Looking for product with legacy_artikel_id: '{product_id}'")
            
            try:
                self._product_cache[product_id] = VariantProduct.objects.get(
                    legacy_artikel_id=product_id
                )
            except VariantProduct.DoesNotExist:
                self.log.warning(f"Product with legacy_artikel_id {product_id} not found")
                return None
        return self._product_cache[product_id]

    def _get_box_slot(self, box_id: str, slot_number: int = 1) -> Optional[BoxSlot]:
        """
        Get box slot instance from cache or database.
        Default slot_number is 1 since most legacy boxes have single slots.
        """
        cache_key = f"{box_id}_{slot_number}"
        if cache_key not in self._box_slot_cache:
            try:
                box = Box.objects.get(legacy_id=box_id)
                self._box_slot_cache[cache_key] = BoxSlot.objects.get(
                    box=box, slot_number=slot_number
                )
            except (Box.DoesNotExist, BoxSlot.DoesNotExist):
                self.log.warning(
                    f"BoxSlot not found for box {box_id} and slot {slot_number}"
                )
                return None
        return self._box_slot_cache[cache_key]

    def _parse_quantity(self, quantity_str: str) -> Optional[Decimal]:
        """
        Parse quantity string to Decimal, handling null/empty values.
        """
        if not quantity_str or quantity_str.lower() == "null":
            return Decimal("0")
        return parse_decimal(quantity_str)

    def _determine_status(self, data: Dict[str, Any]) -> str:
        """
        Determine the status of the product storage based on the data.
        """
        quantity = self._parse_quantity(data.get("Bestand", "0"))
        if quantity == 0:
            return ProductStorage.ReservationStatus.AVAILABLE
        # TODO: Add logic for RESERVED status based on order references
        return ProductStorage.ReservationStatus.AVAILABLE

    def transform_artikel_lagerorte(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform data from Artikel_Lagerorte table.
        """
        try:
            product_id = data.get("ID_Artikel_Stamm")
            if not product_id:
                self.log.warning("Missing ID_Artikel_Stamm in record")
                return None

            # Try to find the product by legacy_id
            product = self._get_product(product_id)
            if not product:
                # Log the missing product and continue with other records
                return None

            quantity = self._parse_quantity(data.get("Bestand", "0"))
            status = self._determine_status(data)

            # We'll set box_slot to None initially and update it later
            # when processing Lager_Schuetten data
            transformed = {
                "legacy_id": data.get("UUID"),
                "product": product,
                "box_slot": None,  # Will be updated when processing Lager_Schuetten
                "quantity": quantity,
                "reservation_status": status,
                "created_by": data.get("created_name"),
                "modified_by": data.get("modified_name"),
            }

            return transformed

        except Exception as e:
            self.log.error(f"Error transforming Artikel_Lagerorte: {str(e)}")
            raise TransformError(f"Failed to transform Artikel_Lagerorte: {str(e)}")

    def transform_lager_schuetten(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Transform data from Lager_Schuetten table and update existing ProductStorage
        records with box slot information.
        """
        try:
            artikel_lagerorte_uuid = data.get("UUID_Artikel_Lagerorte")
            if not artikel_lagerorte_uuid:
                raise TransformError("Missing UUID_Artikel_Lagerorte")

            # Get box slot
            box_id = data.get("ID_Stamm_Lager_Schuetten")
            if not box_id:
                raise TransformError("Missing ID_Stamm_Lager_Schuetten")

            # Parse data_ JSON field if present
            data_json = {}
            if data.get("data_"):
                try:
                    data_json = json.loads(data.get("data_", "{}"))
                except json.JSONDecodeError:
                    self.log.warning(f"Invalid JSON in data_ field: {data.get('data_')}")

            box_slot = self._get_box_slot(box_id)
            if not box_slot:
                self.log.warning(f"Box slot not found for box {box_id}")
                return None

            # Find existing ProductStorage record
            try:
                product_storage = ProductStorage.objects.get(
                    legacy_id=artikel_lagerorte_uuid
                )
                product_storage.box_slot = box_slot
                product_storage.save()
                self.log.info(
                    f"Updated ProductStorage {product_storage.id} with box slot {box_slot}"
                )
                return None  # We've updated existing record, no need to create new one

            except ProductStorage.DoesNotExist:
                self.log.warning(
                    f"ProductStorage not found for UUID {artikel_lagerorte_uuid}"
                )
                return None

        except Exception as e:
            self.log.error(f"Error transforming Lager_Schuetten: {str(e)}")
            raise TransformError(f"Failed to transform Lager_Schuetten: {str(e)}")

    def transform(self, data: Any, source: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        Transform data based on source table.
        
        Args:
            data: Either a single record or a batch of records
            source: Source table name (defaults to self.source)
            
        Returns:
            Transformed data or None if transformation failed
        """
        source = source or self.source
        self.log.debug(f"Transform called with source: {source}, self.source: {self.source}")
        
        # Handle batch processing
        if isinstance(data, list):
            transformed_batch = []
            for record in data:
                transformed = self._transform_record(record, source)
                if transformed:
                    transformed_batch.append(transformed)
            return transformed_batch if transformed_batch else None
        else:
            # Handle single record
            return self._transform_record(data, source)
    
    def _transform_record(self, data: Dict[str, Any], source: str) -> Optional[Dict[str, Any]]:
        """
        Transform a single record based on source table.
        
        Args:
            data: Record to transform
            source: Source table name
            
        Returns:
            Transformed record or None if transformation failed
        """
        # If source is None or empty, default to Artikel_Lagerorte
        if not source:
            source = "Artikel_Lagerorte"
            self.log.debug(f"Source was None, defaulting to {source}")
        
        self.log.debug(f"_transform_record called with source: {source}")
        
        if source == "Artikel_Lagerorte":
            return self.transform_artikel_lagerorte(data)
        elif source == "Lager_Schuetten":
            return self.transform_lager_schuetten(data)
        else:
            raise TransformError(f"Unknown source table: {source}") 