"""Production data transformer implementation."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseTransformer, ValidationError

# Import ParentProduct model
from pyerp.business_modules.products.models import ParentProduct

# Configure logger
logger = logging.getLogger("pyerp.sync.transformers.production")
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False


class ProductionOrderTransformer(BaseTransformer):
    """Transformer for production order data."""
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform production order data from legacy format."""
        transformed_records = []
        
        # Log transformer configuration
        logger.debug("Transformer config: field_mappings=%s", self.field_mappings)
        
        for record in source_data:
            try:
                # Log the source record for debugging
                logger.debug("Processing source record: %s", record)
                
                # Apply field mappings from config
                transformed = self.apply_field_mappings(record)
                
                # Apply custom transformations
                transformed = self.apply_custom_transformers(transformed, record)
                
                # Ensure order_number is set
                if "WerkAufNr" in record:
                    transformed["order_number"] = str(record["WerkAufNr"]).strip()
                    logger.debug("Set order_number to %s", transformed["order_number"])
                
                # Set legacy identifiers
                if "__KEY" in record:
                    transformed["legacy_key"] = str(record["__KEY"])
                    logger.debug("Set legacy_key to %s", transformed["legacy_key"])
                
                if "UUID" in record:
                    transformed["legacy_id"] = str(record["UUID"])
                    logger.debug("Set legacy_id to %s", transformed["legacy_id"])
                
                # Set legacy form ID
                if "linked_Form" in record:
                    transformed["legacy_form_id"] = str(record["linked_Form"])
                    logger.debug("Set legacy_form_id to %s", transformed["legacy_form_id"])
                
                # Map status codes
                if "Status" in record:
                    status_code = record["Status"]
                    transformed["status"] = self._map_status(status_code)
                    logger.debug("Mapped status %s to %s", status_code, transformed["status"])
                
                # Convert dates
                if "eingestellt" in record and record["eingestellt"]:
                    transformed["creation_date"] = self._parse_date(record["eingestellt"])
                    logger.debug("Parsed creation_date to %s", transformed["creation_date"])
                
                if "Termin" in record and record["Termin"]:
                    transformed["planned_date"] = self._parse_date(record["Termin"])
                    logger.debug("Parsed planned_date to %s", transformed["planned_date"])
                
                # Skip records with missing required fields
                if not transformed.get("order_number"):
                    logger.warning("Skipping record with missing order_number")
                    continue
                
                # Log transformed record for debugging
                logger.debug("Transformed record: %s", transformed)
                
                transformed_records.append(transformed)
            except Exception as e:
                logger.error("Error transforming record: %s", e, exc_info=True)
                continue
        
        return transformed_records
    
    def _map_status(self, status: str) -> str:
        """Map legacy status codes to new status values."""
        status_mapping = {
            "V": "completed",
            "E": "in_progress",
            "S": "scheduled",
            "D": "draft",
            "C": "cancelled"
        }
        return status_mapping.get(status, "draft")
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from legacy format."""
        if not date_str or date_str == "0!0!0":
            return None
        
        try:
            # Try standard format first
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            try:
                # Try alternative format
                return datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, TypeError):
                logger.warning("Could not parse date: %s", date_str)
                return None


class ProductionOrderItemTransformer(BaseTransformer):
    """Transformer for production order item data."""
    
    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform production order item data from legacy format."""
        transformed_records = []
        
        # Log transformer configuration
        logger.debug("Transformer config: field_mappings=%s", self.field_mappings)
        
        for record in source_data:
            try:
                # Log the source record for debugging
                logger.debug("Processing source record: %s", record)
                
                # Apply field mappings from config
                transformed = self.apply_field_mappings(record)
                
                # Apply custom transformations
                transformed = self.apply_custom_transformers(transformed, record)
                
                # Set required fields
                if "W_Auftr_Nr" in record:
                    transformed["production_order"] = {
                        "order_number": str(record["W_Auftr_Nr"]).strip()
                    }
                    logger.debug("Set production_order reference to %s", 
                                transformed["production_order"])
                
                if "WAP_Nr" in record:
                    transformed["item_number"] = int(record["WAP_Nr"])
                    logger.debug("Set item_number to %s", transformed["item_number"])
                
                # Explicitly set the operation_type (Arbeitsgang)
                if "Arbeitsgang" in record and record["Arbeitsgang"]:
                    transformed["operation_type"] = str(record["Arbeitsgang"]).strip()
                    logger.debug("Set operation_type to %s", transformed["operation_type"])
                
                # Set legacy identifiers
                if "__KEY" in record:
                    transformed["legacy_key"] = str(record["__KEY"])
                
                if "UUID" in record:
                    transformed["legacy_id"] = str(record["UUID"])
                
                # Set legacy references
                if "linked_Kostenstelle" in record:
                    transformed["legacy_kostenstelle_id"] = str(record["linked_Kostenstelle"])
                
                if "linked_Form_Artikel" in record:
                    transformed["legacy_form_artikel_id"] = str(record["linked_Form_Artikel"])
                
                # Set product information
                if "Art_Nr" in record:
                    art_nr = str(record["Art_Nr"]).strip()
                    transformed["product_sku"] = art_nr
                    
                    # Look up parent product by legacy_base_sku
                    try:
                        parent_product = ParentProduct.objects.filter(
                            legacy_base_sku=art_nr
                        ).first()
                        
                        if parent_product:
                            transformed["parent_product"] = parent_product
                            logger.info(
                                "Found parent product by legacy_base_sku: %s, "
                                "Parent ID: %s, Parent SKU: %s",
                                art_nr, parent_product.id, parent_product.sku
                            )
                        else:
                            logger.warning(
                                "No parent product found with legacy_base_sku: %s", 
                                art_nr
                            )
                    except Exception as e:
                        logger.error(
                            "Error finding parent product for Art_Nr: %s - %s", 
                            art_nr, str(e)
                        )
                
                # Convert quantities
                self._set_numeric_field(transformed, record, "St_Soll", "target_quantity")
                self._set_numeric_field(transformed, record, "St_Haben", "completed_quantity")
                self._set_numeric_field(transformed, record, "St_Rest", "remaining_quantity")
                self._set_numeric_field(transformed, record, "Anteil", "product_share")
                self._set_numeric_field(transformed, record, "St_Std", "standard_time")
                self._set_numeric_field(transformed, record, "Wert", "value")
                
                # Convert time fields
                if "Zeit" in record and record["Zeit"] is not None:
                    try:
                        transformed["estimated_time"] = int(record["Zeit"])
                    except (ValueError, TypeError):
                        transformed["estimated_time"] = 0
                
                # Map status codes
                if "Status" in record:
                    status_code = record["Status"]
                    transformed["status"] = self._map_status(status_code)
                
                # Convert dates
                if "Datum_begin" in record and record["Datum_begin"]:
                    transformed["start_date"] = self._parse_date(record["Datum_begin"])
                
                # Skip records with missing required fields
                if not transformed.get("production_order") or not "item_number" in transformed:
                    logger.warning("Skipping record with missing required fields")
                    continue
                
                # Log transformed record
                logger.debug("Transformed record: %s", transformed)
                
                transformed_records.append(transformed)
            except Exception as e:
                logger.error("Error transforming record: %s", e, exc_info=True)
                continue
        
        return transformed_records
    
    def _set_numeric_field(self, target: Dict[str, Any], source: Dict[str, Any], 
                           source_field: str, target_field: str) -> None:
        """Safely convert and set a numeric field."""
        if source_field in source and source[source_field] is not None:
            try:
                target[target_field] = float(source[source_field])
                # Convert to int if it's a whole number
                if target[target_field] == int(target[target_field]):
                    target[target_field] = int(target[target_field])
            except (ValueError, TypeError):
                target[target_field] = 0
    
    def _map_status(self, status: str) -> str:
        """Map legacy status codes to new status values."""
        status_mapping = {
            "V": "completed",
            "E": "in_progress",
            "P": "pending",
            "C": "cancelled"
        }
        return status_mapping.get(status, "pending")
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from legacy format."""
        if not date_str or date_str == "0!0!0":
            return None
        
        try:
            # Try standard format first
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            try:
                # Try alternative format
                return datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, TypeError):
                logger.warning("Could not parse date: %s", date_str)
                return None 