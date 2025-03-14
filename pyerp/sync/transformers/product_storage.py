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
    # Handle None values
    if value is None:
        return Decimal('0')
        
    # Handle float/int values directly
    if isinstance(value, (float, int)):
        # Check for NaN
        if isinstance(value, float) and (value != value):  # NaN check
            return Decimal('0')
        return Decimal(str(value))
    
    # Handle string values
    if not value or (isinstance(value, str) and value.lower() in ('null', 'nan')):
        return Decimal('0')
    
    # Replace comma with dot for decimal separator
    if isinstance(value, str):
        value = value.replace(',', '.')
        
        # Remove any non-numeric characters except dot
        value = ''.join(c for c in value if c.isdigit() or c == '.')
    
    try:
        decimal_value = Decimal(value)
        # Check if the result is NaN
        if decimal_value.is_nan():
            return Decimal('0')
        return decimal_value
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
        
        Args:
            product_id: The ID_Artikel_Stamm value from Artikel_Lagerorte
            
        Returns:
            VariantProduct instance or None if not found
        """
        # Skip lookup for empty or zero product IDs
        if not product_id or product_id == "0":
            self.log.info("Skipping lookup for empty or zero product ID")
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
        if quantity_str is None:
            return Decimal("0")
            
        # Handle float values directly
        if isinstance(quantity_str, (float, int)):
            return Decimal(str(quantity_str))
            
        # Handle string values
        if not quantity_str or (isinstance(quantity_str, str) and quantity_str.lower() == "null"):
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
            # For Artikel_Lagerorte, we want to primarily use ID_Artikel_Stamm
            # as this matches with refOld in Artikel_Variante
            product_id = data.get("ID_Artikel_Stamm")
            
            # Ensure product_id is a string
            if product_id is not None:
                product_id = str(product_id).strip()
                
            if not product_id or product_id == "0":
                # Fall back to refOld if ID_Artikel_Stamm is not available or is 0
                product_id = data.get("refOld")
                if product_id is not None:
                    product_id = str(product_id).strip()
                self.log.info("ID_Artikel_Stamm not found or is 0, falling back to refOld")
                
            if not product_id or product_id == "0":
                self.log.info(f"Skipping record with missing or zero product identifier: {data.get('UUID')}")
                return None

            # Try to find the product by refOld (matching Artikel_Variante's refOld)
            product = self._get_product(product_id)
            if not product:
                # Log the missing product as info and continue with other records
                self.log.info(f"Skipping record - product with ID {product_id} not found: {data.get('UUID')}")
                return None

            # Handle quantity - explicitly check for null/NaN values
            bestand = data.get("Bestand")
            if bestand is None or (isinstance(bestand, float) and (bestand != bestand)):  # NaN check
                self.log.debug(f"Null or NaN quantity found, setting to 0")
                quantity = Decimal("0")
            else:
                quantity = self._parse_quantity(bestand)
                
            # If quantity is still NaN or invalid, set to 0
            if quantity is None or (hasattr(quantity, 'is_nan') and quantity.is_nan()):
                self.log.debug(f"Invalid quantity after parsing, setting to 0")
                quantity = Decimal("0")
                
            status = self._determine_status(data)

            # Try to find a box slot for this product
            box_slot = None
            try:
                # Look for existing box slot assignments in Lager_Schuetten
                from django.db.models import Q
                from pyerp.business_modules.inventory.models import BoxSlot
                
                # Get the first available box slot
                # This is a temporary solution until we implement proper box slot assignment
                box_slot = BoxSlot.objects.filter(
                    ~Q(stored_products__isnull=False)
                ).first()
                
                if not box_slot:
                    self.log.info(
                        f"No available box slot found for product {product}. "
                        "Skipping record as box_slot is required."
                    )
                    return None
                    
            except Exception as e:
                self.log.info(f"Error finding box slot: {str(e)}")
                return None

            transformed = {
                "legacy_id": data.get("UUID"),
                "product": product,
                "box_slot": box_slot,  # Assign a box slot or skip the record
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