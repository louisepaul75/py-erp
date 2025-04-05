"""Product data transformer implementation."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseTransformer, ValidationError

# Configure database logging to ERROR level
db_logger = logging.getLogger("django.db.backends")
db_logger.setLevel(logging.ERROR)

# Configure logger
logger = logging.getLogger("pyerp.sync.transformers.product")
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False


class ProductTransformer(BaseTransformer):
    """Transformer for product data."""

    _pending_variants = []  # Store variants with missing parents

    def transform(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a single product record from legacy format."""
        # transformed_records = [] # Removed list

        # Log transformer configuration
        logger.debug("Transformer config: field_mappings=%s", self.field_mappings)

        # Remove outer loop: for record in source_data:
        try:
            # Log the complete source record for debugging
            logger.debug("Processing source record: %s", record)

            # Check for aktiv/Aktiv field and log its presence (both case variants)
            if 'aktiv' in record:
                logger.debug("Found 'aktiv' field in source record: %s (type: %s)",
                             record['aktiv'], type(record['aktiv']).__name__)
            elif 'Aktiv' in record:
                logger.debug("Found 'Aktiv' field in source record: %s (type: %s)",
                             record['Aktiv'], type(record['Aktiv']).__name__)
            else:
                logger.debug("Neither 'aktiv' nor 'Aktiv' field found in source record")

            # Apply field mappings from config
            transformed = {}
            for src_field, tgt_field in self.field_mappings.items():
                if src_field in record:
                    value = record[src_field]
                    # Ensure description fields are never None
                    desc_fields = [
                        "description",
                        "description_en",
                        "short_description",
                        "short_description_en",
                    ]
                    if tgt_field in desc_fields:
                        value = value if value is not None else ""
                    transformed[tgt_field] = value
                    logger.debug(
                        "Mapped field %s -> %s: %s", src_field, tgt_field, value
                    )

            # Ensure that both aktiv and Aktiv fields are correctly mapped to is_active
            if 'is_active' not in transformed:
                # Try lowercase aktiv first
                if 'aktiv' in record:
                    value = record['aktiv']
                    # Convert to Python boolean
                    if isinstance(value, str):
                        # Convert string representations to boolean
                        transformed['is_active'] = value.lower() in ("true", "1", "yes", "y", "t")
                    elif isinstance(value, (int, float)):
                        # Convert numeric representations to boolean
                        transformed['is_active'] = bool(value)
                    else:
                        # Handle boolean values directly
                        transformed['is_active'] = bool(value)

                    logger.debug(
                        "Directly mapped aktiv -> is_active: %s -> %s",
                        value,
                        transformed['is_active']
                    )
                # Then try uppercase Aktiv
                elif 'Aktiv' in record:
                    value = record['Aktiv']
                    # Convert to Python boolean
                    if isinstance(value, str):
                        # Convert string representations to boolean
                        transformed['is_active'] = value.lower() in ("true", "1", "yes", "y", "t")
                    elif isinstance(value, (int, float)):
                        # Convert numeric representations to boolean
                        transformed['is_active'] = bool(value)
                    else:
                        # Handle boolean values directly
                        transformed['is_active'] = bool(value)

                    logger.debug(
                        "Directly mapped Aktiv -> is_active: %s -> %s",
                        value,
                        transformed['is_active']
                    )
                else:
                    # If neither aktiv nor Aktiv is found, set default to True
                    transformed['is_active'] = True
                    logger.debug("No aktiv/Aktiv field found, using default is_active=True")

            # Ensure required text fields have default values
            required_text_fields = [
                "description",
                "description_en",
                "short_description",
                "short_description_en",
                "keywords",
                "dimensions",
            ]
            for field in required_text_fields:
                if field not in transformed:
                    transformed[field] = ""
                    logger.debug("Set default empty string for %s", field)

            # Handle SKU and variant information
            if "Nummer" in record:
                transformed["sku"] = str(record["Nummer"]).strip()

            # Get legacy_base_sku from fk_ArtNr if available
            if "fk_ArtNr" in record and record["fk_ArtNr"]:
                legacy_base_sku = str(record["fk_ArtNr"]).strip()
                transformed["legacy_base_sku"] = legacy_base_sku
                logger.debug("Using fk_ArtNr for legacy_base_sku: %s", legacy_base_sku)
            # Otherwise try alteNummer
            elif "alteNummer" in record and record["alteNummer"]:
                alte_nr = str(record["alteNummer"]).strip()
                sku_parts = self._parse_sku(alte_nr)
                transformed["legacy_base_sku"] = sku_parts["base_sku"]
                logger.debug(
                    "Using alteNummer for legacy_base_sku: %s", sku_parts["base_sku"]
                )

            # Get variant_code from ArtikelArt if available
            if "ArtikelArt" in record and record["ArtikelArt"]:
                var_code = str(record["ArtikelArt"]).strip()
                transformed["variant_code"] = var_code
                logger.debug("Using ArtikelArt for variant_code: %s", var_code)
            # If no ArtikelArt, try alteNummer
            elif "alteNummer" in record and record["alteNummer"]:
                alte_nr = str(record["alteNummer"]).strip()
                sku_parts = self._parse_sku(alte_nr)
                if sku_parts["variant_code"]:
                    var_code = sku_parts["variant_code"]
                    transformed["variant_code"] = var_code
                    logger.debug("Using alteNummer for variant_code: %s", var_code)

            # Set legacy_id from __KEY if available
            if "__KEY" in record:
                transformed["legacy_id"] = str(record["__KEY"])

            # Handle refOld field
            if "refOld" in record:
                transformed["refOld"] = str(record["refOld"])
                logger.debug("Set refOld from source: %s", transformed["refOld"])

            # Handle Familie_ field for variants
            if "Familie_" in record:
                parent_id = str(record["Familie_"])
                transformed["legacy_parent_id"] = parent_id
                logger.debug("Set legacy_parent_id from Familie_: %s", parent_id)

            # Ensure required fields for parent products
            if not transformed.get("name") and "Bezeichnung" in record:
                transformed["name"] = record["Bezeichnung"]

            # Handle release date
            if "Release_date" in record:
                transformed["release_date"] = self._parse_legacy_date(
                    record["Release_date"]
                )

            # Log transformed record for debugging
            logger.debug("After field mappings: %s", transformed)

            # Skip records with missing required fields
            if not transformed.get("sku") or not transformed.get("name"):
                # Fix 3: Adjust the logging extra dict to avoid 'name' conflict
                logger.warning(
                    "Skipping record with missing required fields (SKU: %s, Name: %s)",
                    transformed.get("sku", "<Missing>"),
                    transformed.get("name", "<Missing>"),
                    # extra={
                    #     "sku": transformed.get("sku"),
                    #     "record_name": transformed.get("name"), # Renamed 'name' key
                    # },
                )
                return None # Return None if skipping

            # Apply custom transformers specified in config
            custom_transformers = self.config.get("custom_transformers", [])
            for transformer_name in custom_transformers:
                # Check if the transformer method exists
                if hasattr(self, transformer_name) and callable(getattr(self, transformer_name)):
                    # Call the transformer method
                    transformer_method = getattr(self, transformer_name)
                    try:
                        transformed = transformer_method(transformed, record)
                        if transformed is None:
                            logger.warning(
                                f"Transformer {transformer_name} returned None, skipping record"
                            )
                            # Skip if any transformer returned None
                            return None # Return None if skipping
                    except Exception as e:
                        logger.error(
                            f"Error applying transformer {transformer_name}: {e}",
                            exc_info=True
                        )
                else:
                    logger.warning(f"Transformer method {transformer_name} not found")

            # # Skip if any transformer returned None # Handled above
            # if transformed is None:
            #     continue

            # Try to establish parent relationship for variants
            if "legacy_parent_id" in transformed:
                transformed = self.transform_parent_relationship(
                    transformed, record
                )
                if transformed is None:
                     # If parent linking fails and returns None, skip the record
                    return None

            # Add the transformed record # Removed list append
            # transformed_records.append(transformed)
            logger.debug("Successfully transformed record: %s", transformed)
            # Fix 2: Return the single transformed record dictionary
            return transformed

        except Exception as e:
            logger.error(
                "Error transforming record: %s",
                str(e),
                exc_info=True,
                extra={"record": record},
            )
            # Return None on error
            return None

        # logger.info("Transformed %d records successfully", len(transformed_records)) # Removed
        # return transformed_records # Removed

    def _parse_sku(self, sku: str) -> Dict[str, str]:
        """Parse SKU into components.

        Args:
            sku: Product SKU to parse (e.g. '11400-BE')

        Returns:
            Dictionary with base_sku and variant_code
        """
        result = {"base_sku": "", "variant_code": ""}

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
            if "-" in sku:
                parts = sku.rsplit("-", 1)
                if len(parts) == 2 and all(parts):
                    # For legacy SKUs like '11400-BE'
                    result["base_sku"] = parts[0]
                    result["variant_code"] = parts[1]
                    logger.debug(
                        "Split legacy SKU: %s -> base=%s, variant=%s",
                        sku,
                        result["base_sku"],
                        result["variant_code"],
                    )
                else:
                    result["base_sku"] = sku
            else:
                # No variant code, treat entire SKU as base
                result["base_sku"] = sku
        except Exception as e:
            logger.warning(f"Error splitting SKU {sku}: {e}")
            result["base_sku"] = sku

        return result

    def _transform_prices(self, price_data: Dict[str, Any]) -> Dict[str, float]:
        """Transform price data from legacy format.

        Args:
            price_data: Price data dictionary from legacy system

        Returns:
            Dictionary with transformed price fields
        """
        prices = {}

        try:
            # Parse price data from the Coll array
            if isinstance(price_data, dict) and "Coll" in price_data:
                for price_item in price_data["Coll"]:
                    if isinstance(price_item, dict):
                        art = price_item.get("Art")
                        preis = price_item.get("Preis")
                        if art and preis is not None:
                            try:
                                prices[f"price_{art.lower()}"] = float(preis)
                            except (ValueError, TypeError):
                                logger.warning(
                                    f"Invalid price value: {preis}",
                                    extra={"price_item": price_item},
                                )
        except Exception as e:
            logger.error(
                f"Error parsing price data: {e}", extra={"price_data": price_data}
            )

        return prices

    def validate_record(self, record: Dict[str, Any]) -> List[ValidationError]:
        """Validate a transformed product record.

        Args:
            record: Record to validate

        Returns:
            List of validation errors
        """
        errors = super().validate_record(record)

        # Validate required fields
        required_fields = ["sku", "name"]
        for field in required_fields:
            if not record.get(field):
                errors.append(
                    ValidationError(
                        field=field,
                        message=f"Required field '{field}' is missing or empty",
                    )
                )

        return errors

    def _parse_legacy_date(self, date_input: Any) -> Optional[datetime]:
        """Parse a legacy date string or existing datetime object.

        Args:
            date_input: Date string in legacy format (e.g. '1!1!1991')
                          or a datetime object/Timestamp.

        Returns:
            Parsed datetime object or None if parsing fails
        """
        if not date_input:
            return None

        # Handle if it's already a datetime object (or pandas Timestamp)
        if isinstance(date_input, datetime):
             # Optional: Convert to timezone-naive if necessary
             # if date_input.tzinfo:
             #     return date_input.astimezone(None)
             return date_input # Already a datetime object

        # Handle string format like '1!1!1991'
        if isinstance(date_input, str):
            if date_input == "0!0!0":
                return None
            try:
                # Split the date string into components
                day, month, year = date_input.split("!")
                # Convert to integers
                day = int(day)
                month = int(month)
                year = int(year)
                # Create datetime object
                # Ensure year is reasonable (e.g., avoid year 0)
                if year < 1900 or year > 2100: # Adjust range as needed
                     logger.warning(f"Invalid year '{year}' parsed from legacy date: {date_input}")
                     return None
                return datetime(year, month, day)
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(
                    f"Error parsing legacy date string: {e}", extra={"date_str": date_input}
                )
                return None

        # Handle other unexpected types
        logger.warning(f"Unexpected type for legacy date parsing: {type(date_input).__name__}", extra={"date_input": date_input})
        return None

    def transform_parent_relationship(
        self, transformed: Dict[str, Any], source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform parent relationship for variant products.

        Args:
            transformed: The transformed record
            source: The source record

        Returns:
            Updated transformed record with parent relationship
        """
        from pyerp.business_modules.products.models import ParentProduct

        if "legacy_parent_id" in transformed:
            try:
                # Try to find parent by legacy_id
                parent = ParentProduct.objects.get(
                    legacy_id=transformed["legacy_parent_id"]
                )
                transformed["parent"] = parent
                
                # Update parent product's legacy_base_sku with the variant's legacy_base_sku if available
                legacy_base_sku = transformed.get("legacy_base_sku")
                if legacy_base_sku and (not parent.legacy_base_sku or parent.legacy_base_sku != legacy_base_sku):
                    parent.legacy_base_sku = legacy_base_sku
                    parent.save()
                    logger.info(
                        "Updated parent product legacy_base_sku. "
                        f"Parent ID: {parent.id}, "
                        f"Parent SKU: {parent.sku}, "
                        f"New legacy_base_sku: {legacy_base_sku}"
                    )
                
                logger.info(
                    "Found parent product for variant. "
                    f"Variant SKU: {transformed.get('sku')}, "
                    f"Variant legacy_id: {transformed.get('legacy_id')}, "
                    f"Parent SKU: {parent.sku}, "
                    f"Parent legacy_id: {parent.legacy_id}"
                )
            except ParentProduct.DoesNotExist:
                # Try to find parent by legacy_base_sku if available
                legacy_base_sku = transformed.get("legacy_base_sku")
                if legacy_base_sku:
                    try:
                        parent = ParentProduct.objects.get(legacy_base_sku=legacy_base_sku)
                        transformed["parent"] = parent
                        logger.info(
                            "Found parent product by legacy_base_sku. "
                            f"Variant SKU: {transformed.get('sku')}, "
                            f"Legacy Base SKU: {legacy_base_sku}, "
                            f"Parent SKU: {parent.sku}"
                        )
                    except ParentProduct.DoesNotExist:
                        logger.warning(
                            "Parent product not found by legacy_id or legacy_base_sku. "
                            f"Variant SKU: {transformed.get('sku')}, "
                            f"Legacy ID: {transformed.get('legacy_id')}, "
                            f"Parent ID: {transformed['legacy_parent_id']}, "
                            f"Legacy Base SKU: {legacy_base_sku}"
                        )
                        # Store for retry
                        if not hasattr(self, "_pending_variants"):
                            self._pending_variants = []
                        self._pending_variants.append(
                            {"transformed": transformed.copy(), "source": source.copy()}
                        )
                        return None
                else:
                    logger.warning(
                        "Parent product not found and no legacy_base_sku available. "
                        f"Variant SKU: {transformed.get('sku')}, "
                        f"Legacy ID: {transformed.get('legacy_id')}, "
                        f"Parent ID: {transformed['legacy_parent_id']}"
                    )
                    # Store for retry
                    if not hasattr(self, "_pending_variants"):
                        self._pending_variants = []
                    self._pending_variants.append(
                        {"transformed": transformed.copy(), "source": source.copy()}
                    )
                    return None

        return transformed

    def post_transform(
        self, transformed_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process any pending variants after all records are transformed.

        Args:
            transformed_records: List of transformed records

        Returns:
            Updated list of transformed records
        """
        from pyerp.business_modules.products.models import ParentProduct

        if not hasattr(self, "_pending_variants"):
            return transformed_records

        # Try to process pending variants
        retry_count = 3  # Number of retries for finding parents
        for attempt in range(retry_count):
            if not self._pending_variants:
                break

            pending_count = len(self._pending_variants)
            logger.info(
                f"Retry attempt {attempt + 1}: "
                f"Processing {pending_count} pending variants"
            )

            remaining_variants = []
            for variant in self._pending_variants:
                try:
                    # Try by legacy_id first
                    parent = ParentProduct.objects.get(
                        legacy_id=variant["transformed"]["legacy_parent_id"]
                    )
                    variant["transformed"]["parent"] = parent
                    
                    # Update parent product's legacy_base_sku with the variant's legacy_base_sku if available
                    legacy_base_sku = variant["transformed"].get("legacy_base_sku")
                    if legacy_base_sku and (not parent.legacy_base_sku or parent.legacy_base_sku != legacy_base_sku):
                        parent.legacy_base_sku = legacy_base_sku
                        parent.save()
                        logger.info(
                            "Updated parent product legacy_base_sku during retry. "
                            f"Parent ID: {parent.id}, "
                            f"Parent SKU: {parent.sku}, "
                            f"New legacy_base_sku: {legacy_base_sku}"
                        )
                    
                    transformed_records.append(variant["transformed"])
                    logger.info(
                        "Successfully linked variant "
                        f"{variant['transformed'].get('sku')} "
                        f"to parent {parent.sku} by legacy_id"
                    )
                except ParentProduct.DoesNotExist:
                    # Try by legacy_base_sku if available
                    legacy_base_sku = variant["transformed"].get("legacy_base_sku")
                    if legacy_base_sku:
                        try:
                            parent = ParentProduct.objects.get(legacy_base_sku=legacy_base_sku)
                            variant["transformed"]["parent"] = parent
                            transformed_records.append(variant["transformed"])
                            logger.info(
                                "Successfully linked variant "
                                f"{variant['transformed'].get('sku')} "
                                f"to parent {parent.sku} by legacy_base_sku"
                            )
                        except ParentProduct.DoesNotExist:
                            remaining_variants.append(variant)
                    else:
                        remaining_variants.append(variant)

            self._pending_variants = remaining_variants
            if remaining_variants:
                logger.warning(
                    f"Still have {len(remaining_variants)} "
                    "variants with missing parents"
                )
                import time

                time.sleep(2)  # Wait a bit before retrying

        # Log any remaining unlinked variants
        if self._pending_variants:
            logger.error(
                f"Failed to link {len(self._pending_variants)} "
                "variants to their parents after all retries"
            )
            for variant in self._pending_variants:
                transformed = variant["transformed"]
                logger.error(
                    "Unlinked variant: "
                    f"SKU={transformed.get('sku')}, "
                    f"Legacy ID={transformed.get('legacy_id')}, "
                    f"Parent ID={transformed.get('legacy_parent_id')}, "
                    f"Legacy Base SKU={transformed.get('legacy_base_sku')}"
                )

        return transformed_records

    def transform_boolean_flags(self, transformed: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
        """Transform boolean fields from various formats to Python boolean values.
        
        Args:
            transformed: The transformed record
            source: The source record
            
        Returns:
            Updated transformed record with boolean fields properly converted
        """
        # Map source boolean fields to target boolean fields
        boolean_field_mappings = {
            "Aktiv": "is_active",
            "aktiv": "is_active",  # Handle both case variants
            "Verkaufsartikel": "is_verkaufsartikel",
            "neu": "is_new",
            "Haengend": "is_hanging",
            "Einseitig": "is_one_sided",
        }
        
        logger.debug("Starting transform_boolean_flags for record with SKU: %s", transformed.get("sku", "unknown"))
        
        # Process each boolean field mapping
        for source_field, target_field in boolean_field_mappings.items():
            if source_field in source:
                # Get the value from source record
                value = source[source_field]
                
                # Convert to Python boolean
                if isinstance(value, str):
                    # Convert string representations to boolean
                    bool_value = value.lower() in ("true", "1", "yes", "y", "t")
                elif isinstance(value, (int, float)):
                    # Convert numeric representations to boolean
                    bool_value = bool(value)
                else:
                    # Handle boolean values directly
                    bool_value = bool(value)
                
                # Set the value in the transformed record
                transformed[target_field] = bool_value
                
                logger.debug(
                    "Converted boolean field %s -> %s: %s -> %s (Source type: %s)",
                    source_field,
                    target_field,
                    value,
                    bool_value,
                    type(value).__name__
                )
        
        # Set a default value for is_active if not already set
        if "is_active" not in transformed:
            transformed["is_active"] = True
            logger.debug("Set default is_active=True for record with SKU: %s", transformed.get("sku", "unknown"))
            
        # Ensure the critical fields are definitely in the transformed record
        logger.debug("After transform_boolean_flags - SKU: %s, is_active: %s", 
                    transformed.get("sku", "unknown"), 
                    transformed.get("is_active", "not set"))
        
        return transformed
