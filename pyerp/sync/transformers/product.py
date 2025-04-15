"""Product data transformer implementation."""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
import traceback
from decimal import Decimal, ROUND_HALF_UP

# Import ParentProduct locally within methods where needed to avoid circular imports
# from pyerp.business_modules.products.models import ParentProduct

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

    _pending_variants: List[Dict[str, Any]] = []  # Class attribute

    def __init__(self, config: Dict[str, Any]):
        """Initialize the transformer."""
        super().__init__(config)
        # Ensure _pending_variants is reset for each transformer instance if needed
        # Although typically one instance is created per sync run via factory
        ProductTransformer._pending_variants = []

    def transform(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform a single product record from legacy format."""
        # Log transformer configuration
        logger.debug("Transformer config: field_mappings=%s", self.field_mappings)
        # Log the field mappings being used
        logger.debug("Using field mappings: %s", self.field_mappings)

        try:
            # --- Start: Handle list input ---
            if isinstance(record, list):
                if len(record) == 1 and isinstance(record[0], dict):
                    # Use the first dictionary if it's a single-element list
                    record = record[0]
                    logger.debug(
                        "Input was a single-element list, "
                        "extracted the dictionary."
                    )
                else:
                    logger.error(
                        "Input record is a list but not a single "
                        "dictionary. Skipping.", extra={"record_input": record}
                    )
                    return None
            elif not isinstance(record, dict):
                type_name = type(record).__name__
                logger.error(
                    "Input record is not a dictionary or a single-element "
                    f"list of dict. Type: {type_name}. Skipping.",
                    extra={"record_input": record}
                )
                return None
            # --- End: Handle list input ---

            # Log the complete source record for debugging
            logger.debug("Processing source record: %s", record)

            # Check for aktiv/Aktiv field and log its presence
            if 'aktiv' in record:
                logger.debug(
                    "Found 'aktiv' field in source record: %s (type: %s)",
                    record['aktiv'], type(record['aktiv']).__name__
                )
            elif 'Aktiv' in record:
                logger.debug(
                    "Found 'Aktiv' field in source record: %s (type: %s)",
                    record['Aktiv'], type(record['Aktiv']).__name__
                )
            else:
                logger.debug(
                    "Neither 'aktiv' nor 'Aktiv' field found in source record"
                )

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
                        "Mapped field %s -> %s: %s",
                        src_field, tgt_field, value
                    )

            # Ensure that both aktiv and Aktiv fields are mapped to is_active
            if 'is_active' not in transformed:
                # Try lowercase aktiv first
                if 'aktiv' in record:
                    value = record['aktiv']
                    # Convert to Python boolean
                    if isinstance(value, str):
                        # Convert string representations to boolean
                        bool_val = value.lower() in ("true", "1", "yes", "y", "t")
                        transformed['is_active'] = bool_val
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
                        bool_val = value.lower() in ("true", "1", "yes", "y", "t")
                        transformed['is_active'] = bool_val
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
                    logger.debug(
                        "No aktiv/Aktiv field found, "
                        "using default is_active=True"
                    )

            # Ensure required text fields have default values
            required_text_fields = [
                "description",
                "description_en",
                "short_description",
                "short_description_en",
                "keywords",
                "dimensions",  # Assuming this might be a text field
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
                logger.debug(
                    "Using fk_ArtNr for legacy_base_sku: %s", legacy_base_sku
                )
            # Otherwise try alteNummer
            elif "alteNummer" in record and record["alteNummer"]:
                alte_nr = str(record["alteNummer"]).strip()
                sku_parts = self._parse_sku(alte_nr)
                transformed["legacy_base_sku"] = sku_parts["base_sku"]
                logger.debug(
                    "Using alteNummer for legacy_base_sku: %s",
                    sku_parts["base_sku"]
                )

            # Get variant_code from ArtikelArt if available
            if "ArtikelArt" in record and record["ArtikelArt"]:
                var_code = str(record["ArtikelArt"]).strip()
                transformed["variant_code"] = var_code
                logger.debug(
                    "Using ArtikelArt for variant_code: %s", var_code
                )
            # If no ArtikelArt, try alteNummer
            elif "alteNummer" in record and record["alteNummer"]:
                alte_nr = str(record["alteNummer"]).strip()
                sku_parts = self._parse_sku(alte_nr)
                if sku_parts["variant_code"]:
                    var_code = sku_parts["variant_code"]
                    transformed["variant_code"] = var_code
                    logger.debug(
                        "Using alteNummer for variant_code: %s", var_code
                    )

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
                logger.debug(
                    "Set legacy_parent_id from Familie_: %s", parent_id
                )

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

            # --- Start Enhanced Logging for Missing Fields ---
            missing_reason = []
            if not transformed.get("sku"):
                num_src = record.get('Nummer', '<Not Found>')
                missing_reason.append(f"SKU missing (Source Nummer: {num_src})")
            if not transformed.get("name"):
                bez_src = record.get('Bezeichnung', '<Not Found>')
                missing_reason.append(
                    f"Name missing (Source Bezeichnung: {bez_src})"
                )

            if missing_reason:
                logger.warning(
                    "Skipping record due to missing required fields: %s",
                    "; ".join(missing_reason),
                    extra={"record": record}  # Include full record context
                )
                return None  # Return None if skipping
            # --- End Enhanced Logging ---

            # Apply custom transformers specified in the mapping config
            # Get custom_transformers directly from self.config instead of self.mapping
            custom_transformers = self.config.get('custom_transformers', [])
            
            # If empty and for backward compatibility, try the old nested path
            if not custom_transformers:
                try:
                    if hasattr(self, 'mapping') and self.mapping is not None:
                        custom_transformers = self.mapping.mapping_config.get(
                            'transformation', {}).get('config', {}).get(
                            'custom_transformers', [])
                except AttributeError:
                    logger.warning("self.mapping not available, using transformers from config.")
            
            # Ensure transform_prices is always included if not present
            if 'transform_prices' not in custom_transformers:
                custom_transformers.append('transform_prices')

            logger.debug(f"[transform] Starting custom transformers: {custom_transformers}")
            logger.debug(f"[transform] Before loop, transformed keys: {list(transformed.keys())}")
            for transformer_name in custom_transformers:
                logger.debug(f"[transform] Attempting transformer: {transformer_name}")
                transform_method = getattr(self, transformer_name, None)
                if transform_method and callable(transform_method):
                    try:
                        keys_before = set(transformed.keys())
                        transformed = transform_method(transformed, record)
                        if transformed is None:
                            logger.warning(
                                f"Transformer {transformer_name} returned None, "
                                "skipping record"
                            )
                            return None  # Return None if skipping
                        # Log keys changes
                        keys_after = set(transformed.keys())
                        added_keys = keys_after - keys_before
                        removed_keys = keys_before - keys_after
                        if added_keys: logger.debug(f"[transform] Keys added by {transformer_name}: {added_keys}")
                        if removed_keys: logger.debug(f"[transform] Keys removed by {transformer_name}: {removed_keys}")
                        logger.debug(f"[transform] After {transformer_name}, transformed keys: {list(transformed.keys())}")
                    except Exception as e:
                        logger.error(
                            f"Error applying transformer {transformer_name}: {e}",
                            exc_info=True
                        )
                else:
                    logger.warning(
                        f"Transformer method {transformer_name} not found"
                    )
            
            logger.debug(f"[transform] After custom transformer loop, transformed keys: {list(transformed.keys())}")

            # Try to establish parent relationship for variants
            # Note: Moved after custom transformers loop
            # Note: transform_parent_relationship now handles returning None
            #       if parent needs retry, so no extra check needed here.
            if "legacy_parent_id" in transformed:
                logger.debug("[transform] Attempting parent relationship transform...")
                keys_before_parent = set(transformed.keys())
                transformed = self.transform_parent_relationship(
                    transformed, record
                )
                if transformed is None:
                    # Parent not found, variant stored for retry, skip this record now
                    return None
                # Log parent relationship changes
                keys_after_parent = set(transformed.keys())

            logger.debug("Successfully transformed record: %s", transformed)
            # Return the single transformed record dictionary
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
            sku_str = str(sku).strip()
        except (AttributeError, TypeError):
            logger.warning(f"Could not convert SKU to string: {sku}")
            return result

        if not sku_str:
            return result

        # Split at last hyphen for variant codes
        try:
            if "-" in sku_str:
                parts = sku_str.rsplit("-", 1)
                if len(parts) == 2 and all(parts):
                    # For legacy SKUs like '11400-BE'
                    result["base_sku"] = parts[0]
                    result["variant_code"] = parts[1]
                    logger.debug(
                        "Split legacy SKU: %s -> base=%s, variant=%s",
                        sku_str,
                        result["base_sku"],
                        result["variant_code"],
                    )
                else:
                    result["base_sku"] = sku_str
            else:
                # No variant code, treat entire SKU as base
                result["base_sku"] = sku_str
        except Exception as e:
            logger.warning(f"Error splitting SKU {sku_str}: {e}")
            result["base_sku"] = sku_str

        return result

    def transform_prices(
        self, transformed: Dict[str, Any], source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform price data from legacy format.

        Args:
            transformed: The transformed record dictionary.
            source: The original source record dictionary.

        Returns:
            Updated transformed record dictionary with price fields added.
        """
        from decimal import Decimal, ROUND_HALF_UP

        sku = transformed.get("sku", "N/A")
        logger.debug("[transform_prices] Processing SKU: %s", sku)
        # Get the 'Preise' structure directly from the SOURCE record
        price_data = source.get("Preise")
        logger.debug("[transform_prices] Raw price data from source for SKU %s: %s", sku, price_data)

        if (
            not price_data or
            not isinstance(price_data, dict) or
            "Coll" not in price_data
        ):
            logger.warning(
                "[transform_prices] No valid 'Preise' data structure found in source record for SKU %s. "
                "Skipping price transformation. Data: %s",
                sku,
                price_data, # Log the problematic data
                extra={"source_record": source}
            )
            # Return the record unchanged if no price data
            return transformed

        logger.debug("[transform_prices] Found 'Preise.Coll' for SKU %s. Proceeding with parsing.", sku)
        try:
            # Parse price data from the Coll array
            for i, price_item in enumerate(price_data.get("Coll", [])):  # Safely get Coll list
                logger.debug("[transform_prices] Processing price item %d for SKU %s: %s", i, sku, price_item)
                if isinstance(price_item, dict):
                    art = price_item.get("Art")
                    preis = price_item.get("Preis")
                    # Get packaging unit (Verpackungseinheit)
                    ve = price_item.get("VE")

                    if not art:  # Skip if 'Art' (type) is missing
                        logger.debug("[transform_prices] Skipping item %d for SKU %s: Missing 'Art' key.", i, sku)
                        continue

                    # Standardize the price type for easier checking
                    art_lower = art.lower()
                    logger.debug("[transform_prices] SKU %s, Item %d: Art='%s', Preis='%s', VE='%s'", sku, i, art, preis, ve)

                    # Process 'Laden' (Retail) prices
                    if art_lower == "laden":
                        if preis is not None:
                            try:
                                # Use Decimal for precise handling and ensure it has EXACTLY 2 decimal places
                                # Convert the float value to string first to preserve decimal points
                                orig_value = preis
                                TWO_PLACES = Decimal('0.01')
                                if not isinstance(preis, Decimal):
                                    preis = Decimal(str(preis))
                                
                                # Quantize to exactly 2 decimal places
                                retail_price_val = preis.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
                                transformed["retail_price"] = retail_price_val
                                logger.debug("[transform_prices] SKU %s: Set retail_price: %s (from %s)", 
                                             sku, retail_price_val, orig_value)
                            except (ValueError, TypeError, Decimal.InvalidOperation) as e:
                                logger.warning("[transform_prices] Invalid retail price value: '%s' for SKU %s. Error: %s", 
                                               preis, sku, e)
                        else:
                            logger.debug("[transform_prices] SKU %s: Retail price (Preis) is None.", sku)

                        if ve is not None:
                            try:
                                # Add unit to the TRANSFORMED record
                                retail_unit_val = int(ve)
                                transformed["retail_unit"] = retail_unit_val
                                logger.debug("[transform_prices] SKU %s: Set retail_unit: %s", sku, retail_unit_val)
                            except (ValueError, TypeError) as e:
                                logger.warning("[transform_prices] Invalid retail unit value: '%s' for SKU %s. Error: %s", ve, sku, e)
                        else:
                            logger.debug("[transform_prices] SKU %s: Retail unit (VE) is None.", sku)

                    # Process 'Handel' (Wholesale) prices
                    elif art_lower == "handel":
                        if preis is not None:
                            try:
                                # Use Decimal for precise handling and ensure it has EXACTLY 2 decimal places
                                # Convert the float value to string first to preserve decimal points
                                orig_value = preis
                                TWO_PLACES = Decimal('0.01')
                                if not isinstance(preis, Decimal):
                                    preis = Decimal(str(preis))
                                
                                # Quantize to exactly 2 decimal places
                                wholesale_price_val = preis.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
                                transformed["wholesale_price"] = wholesale_price_val
                                logger.debug("[transform_prices] SKU %s: Set wholesale_price: %s (from %s)", 
                                             sku, wholesale_price_val, orig_value)
                            except (ValueError, TypeError, Decimal.InvalidOperation) as e:
                                logger.warning("[transform_prices] Invalid wholesale price value: '%s' for SKU %s. Error: %s", 
                                               preis, sku, e)
                        else:
                            logger.debug("[transform_prices] SKU %s: Wholesale price (Preis) is None.", sku)

                        if ve is not None:
                            try:
                                # Add unit to the TRANSFORMED record
                                wholesale_unit_val = int(ve)
                                transformed["wholesale_unit"] = wholesale_unit_val
                                logger.debug("[transform_prices] SKU %s: Set wholesale_unit: %s", sku, wholesale_unit_val)
                            except (ValueError, TypeError) as e:
                                logger.warning("[transform_prices] Invalid wholesale unit value: '%s' for SKU %s. Error: %s", ve, sku, e)
                        else:
                            logger.debug("[transform_prices] SKU %s: Wholesale unit (VE) is None.", sku)

                    # Add more price types here if needed (e.g., 'einkauf')
                    # elif art_lower == "einkauf":
                    #    # ... handle cost price ...
                    else:
                        logger.debug("[transform_prices] SKU %s: Unhandled price type 'Art': '%s'", sku, art)
                else:
                    logger.warning("[transform_prices] Price item %d for SKU %s is not a dictionary: %s", i, sku, price_item)

        except Exception as e:
            logger.error("[transform_prices] Error parsing price data for SKU %s: %s", sku, e)
            logger.error("[transform_prices] Traceback: %s", traceback.format_exc())

        logger.debug("[transform_prices] Exiting for SKU: %s. Final transformed keys: %s", sku, list(transformed.keys()))
        # Return the potentially modified TRANSFORMED record
        return transformed

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
            return date_input  # Already a datetime object

        # Handle string format like '1!1!1991'
        if isinstance(date_input, str):
            if date_input == "0!0!0":
                return None
            try:
                # Split the date string into components
                day, month, year = date_input.split("!")
                # Convert to integers
                day_int = int(day)
                month_int = int(month)
                year_int = int(year)
                # Create datetime object
                # Ensure year is reasonable (e.g., avoid year 0)
                if not (1900 <= year_int <= 2100):  # Adjust range as needed
                    logger.warning(
                        f"Invalid year '{year_int}' parsed from "
                        f"legacy date: {date_input}"
                    )
                    return None
                return datetime(year_int, month_int, day_int)
            except (ValueError, TypeError, AttributeError) as e:
                logger.warning(
                    f"Error parsing legacy date string: {e}",
                    extra={"date_str": date_input}
                )
                return None

        # Handle other unexpected types
        type_name = type(date_input).__name__
        logger.warning(
            f"Unexpected type for legacy date parsing: {type_name}",
            extra={"date_input": date_input}
        )
        return None

    def transform_parent_relationship(
        self, transformed: Dict[str, Any], source: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Transform parent relationship for variant products.

        Tries to find the parent product using legacy_id or legacy_base_sku.
        If not found immediately, stores the variant for later processing
        in post_transform.

        Args:
            transformed: The transformed record.
            source: The source record (used for retry).

        Returns:
            Updated transformed record with parent relationship,
            or None if the parent is not found yet (will be retried).
        """
        # Local import to avoid circular dependency at module level
        from pyerp.business_modules.products.models import ParentProduct

        parent = None
        if "legacy_parent_id" in transformed:
            legacy_parent_id_to_find = transformed["legacy_parent_id"]
            variant_sku = transformed.get('sku', 'N/A')
            logger.debug(
                f"Attempting to link variant {variant_sku} "
                f"using legacy_parent_id: {legacy_parent_id_to_find}"
            )
            try:
                # Try to find parent by legacy_id
                parent = ParentProduct.objects.get(
                    legacy_id=legacy_parent_id_to_find  # Use the variable
                )
                logger.info(
                    "Found parent product for variant by legacy_id. "
                    f"Variant SKU: {variant_sku}, "
                    f"Parent SKU: {parent.sku}, "
                    f"Parent legacy_id: {parent.legacy_id}"
                )

            except ParentProduct.DoesNotExist:
                logger.debug(
                    f"Parent not found by legacy_id: {legacy_parent_id_to_find}"
                    f" for variant {variant_sku}"
                )
                # Try to find parent by legacy_base_sku if available
                legacy_base_sku = transformed.get("legacy_base_sku")
                if legacy_base_sku:
                    logger.debug(
                        f"Attempting to link variant {variant_sku} "
                        f"using legacy_base_sku: {legacy_base_sku}"
                    )
                    try:
                        parent = ParentProduct.objects.get(
                            legacy_base_sku=legacy_base_sku
                        )
                        logger.info(
                            "Found parent product by legacy_base_sku. "
                            f"Variant SKU: {variant_sku}, "
                            f"Legacy Base SKU: {legacy_base_sku}, "
                            f"Parent SKU: {parent.sku}"
                        )
                    except ParentProduct.DoesNotExist:
                        logger.warning(
                            "Parent not found by legacy_id OR legacy_base_sku. "
                            "Storing for retry. "
                            f"Variant SKU: {variant_sku}, "
                            f"Legacy ID: {transformed.get('legacy_id')}, "
                            f"Parent Legacy ID: {legacy_parent_id_to_find}, "
                            f"Legacy Base SKU: {legacy_base_sku}"
                        )
                        # Store for retry and return None for now
                        self._store_pending_variant(transformed, source)
                        return None
                else:
                    logger.warning(
                        "Parent not found by legacy_id and NO legacy_base_sku "
                        "available. Storing for retry. "
                        f"Variant SKU: {variant_sku}, "
                        f"Legacy ID: {transformed.get('legacy_id')}, "
                        f"Parent Legacy ID: {legacy_parent_id_to_find}"
                    )
                    # Store for retry and return None for now
                    self._store_pending_variant(transformed, source)
                    return None
            except ParentProduct.MultipleObjectsReturned:
                logger.error(
                    f"Multiple parent products found with legacy_id: "
                    f"{legacy_parent_id_to_find}. Cannot link variant "
                    f"{variant_sku}."
                )
                # Don't retry, this indicates a data issue
                return None  # Or handle as error explicitly
            except Exception as e:
                logger.error(
                    f"Error linking parent for {variant_sku}: {e}",
                    exc_info=True
                )
                # Retry on other errors
                self._store_pending_variant(transformed, source)
                return None

        if parent:
            transformed["parent"] = parent # Modify in place
            # Update parent product's legacy_base_sku if needed
            self._update_parent_legacy_base_sku(parent, transformed)
        # Ensure the original dictionary (with potential price fields) is returned
        return transformed

    def _store_pending_variant(self, transformed, source):
        """Helper to store a variant for later processing."""
        if not hasattr(self, "_pending_variants"):
            # Ensure the class attribute is initialized if accessed
            # directly without __init__ (though unlikely)
            ProductTransformer._pending_variants = []
        # Use the class attribute
        ProductTransformer._pending_variants.append(
            {"transformed": transformed.copy(), "source": source.copy()}
        )

    def _update_parent_legacy_base_sku(self, parent, variant_transformed):
        """Update parent's legacy_base_sku if variant has a better one."""
        # Local import to avoid circular dependency at module level
        from pyerp.business_modules.products.models import ParentProduct

        legacy_base_sku = variant_transformed.get("legacy_base_sku")
        # Only update if variant has one and parent doesn't or they differ
        if legacy_base_sku and (
            not parent.legacy_base_sku or
            parent.legacy_base_sku != legacy_base_sku
        ):
            try:
                parent.legacy_base_sku = legacy_base_sku
                # Save only the legacy_base_sku field to be efficient
                parent.save(update_fields=['legacy_base_sku'])
                logger.info(
                    "Updated parent product legacy_base_sku. "
                    f"Parent ID: {parent.id}, "
                    f"Parent SKU: {parent.sku}, "
                    f"New legacy_base_sku: {legacy_base_sku}"
                )
            except Exception as e:
                logger.error(
                    "Failed to update parent legacy_base_sku for "
                    f"Parent ID {parent.id}: {e}"
                )

    def post_transform(
        self, transformed_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process any pending variants after all records are transformed.

        Args:
            transformed_records: List of successfully transformed records so far.

        Returns:
            Updated list of transformed records including successfully linked
            pending variants.
        """
        # Local import to avoid circular dependency at module level
        from pyerp.business_modules.products.models import ParentProduct

        # Use the class attribute
        if not hasattr(ProductTransformer, "_pending_variants") or \
           not ProductTransformer._pending_variants:
            return transformed_records

        # Try to process pending variants
        retry_count = 3  # Number of retries for finding parents
        for attempt in range(retry_count):
            # Use the class attribute
            if not ProductTransformer._pending_variants:
                break  # Exit if all variants are processed

            pending_count = len(ProductTransformer._pending_variants)
            logger.info(
                f"Retry attempt {attempt + 1}: "
                f"Processing {pending_count} pending variants"
            )

            remaining_variants = []
            successfully_linked_in_retry = []

            # Iterate over a copy for safe removal/modification
            current_pending = ProductTransformer._pending_variants[:]
            ProductTransformer._pending_variants = []  # Clear original list

            for variant_data in current_pending:
                variant_transformed = variant_data["transformed"]
                # variant_source = variant_data["source"]  # Currently unused
                variant_sku = variant_transformed.get('sku', 'N/A')
                parent_legacy_id = variant_transformed.get("legacy_parent_id")
                legacy_base_sku = variant_transformed.get("legacy_base_sku")

                logger.debug(
                    f"Retrying variant {variant_sku}: "
                    f"Parent Legacy ID={parent_legacy_id}, "
                    f"Legacy Base SKU={legacy_base_sku}"
                )

                parent = None
                try:
                    # Try by legacy_id first
                    parent = ParentProduct.objects.get(
                        legacy_id=parent_legacy_id
                    )
                    logger.info(
                        "Successfully linked variant during retry "
                        f"{variant_sku} to parent {parent.sku} by legacy_id"
                    )
                except ParentProduct.DoesNotExist:
                    logger.debug(
                        f"Retry: Parent not found by legacy_id: "
                        f"{parent_legacy_id} for variant {variant_sku}"
                    )
                    # Try by legacy_base_sku if available
                    if legacy_base_sku:
                        logger.debug(
                            "Retry: Attempting lookup by legacy_base_sku: "
                            f"{legacy_base_sku} for variant {variant_sku}"
                        )
                        try:
                            parent = ParentProduct.objects.get(
                                legacy_base_sku=legacy_base_sku
                            )
                            logger.info(
                                "Successfully linked variant during retry "
                                f"{variant_sku} to parent {parent.sku} "
                                "by legacy_base_sku"
                            )
                        except ParentProduct.DoesNotExist:
                            logger.warning(
                                "Retry Failed: Parent not found by "
                                f"legacy_base_sku: {legacy_base_sku} for "
                                f"variant {variant_sku}"
                            )
                            remaining_variants.append(variant_data)
                        except ParentProduct.MultipleObjectsReturned:
                            logger.error(
                                f"Retry Failed: Multiple parents found by "
                                f"legacy_base_sku: {legacy_base_sku} for "
                                f"variant {variant_sku}. Cannot link."
                            )
                            # Don't keep for retry, log as error below
                        except Exception as e_base_sku:
                            logger.error(
                                "Retry Error (lookup by base SKU) for variant "
                                f"{variant_sku}: {e_base_sku}", exc_info=True
                            )
                            # Keep for retry
                            remaining_variants.append(variant_data)
                    else:
                        logger.warning(
                            "Retry Failed: No legacy_base_sku available for "
                            f"variant {variant_sku}"
                        )
                        remaining_variants.append(variant_data)
                except ParentProduct.MultipleObjectsReturned:
                    logger.error(
                        f"Retry Failed: Multiple parents found by legacy_id: "
                        f"{parent_legacy_id} for variant {variant_sku}. "
                        "Cannot link."
                    )
                    # Don't keep for retry, log as error below
                except Exception as e_retry:
                    logger.error(
                        f"Error during retry linking for variant {variant_sku}: "
                        f"{e_retry}",
                        exc_info=True
                    )
                    # Keep variant for logging if error occurs during retry
                    remaining_variants.append(variant_data)

                # If parent found in this retry attempt
                if parent:
                    variant_transformed["parent"] = parent
                    self._update_parent_legacy_base_sku(
                        parent, variant_transformed
                    )
                    # Add to the list of variants linked in this retry pass
                    successfully_linked_in_retry.append(variant_transformed)

            # Update list of pending variants for next attempt
            ProductTransformer._pending_variants = remaining_variants
            # Add newly linked variants to the main results
            transformed_records.extend(successfully_linked_in_retry)

            if remaining_variants and attempt < retry_count - 1:
                logger.warning(
                    f"Still have {len(remaining_variants)} "
                    f"variants with missing parents after attempt {attempt + 1}"
                )
                time.sleep(2)  # Wait a bit before retrying

        # Log any remaining unlinked variants after all retries
        if ProductTransformer._pending_variants:
            logger.error(
                f"Failed to link {len(ProductTransformer._pending_variants)} "
                "variants to their parents after all retries"
            )
            for variant_data in ProductTransformer._pending_variants:
                transformed = variant_data["transformed"]
                logger.error(
                    "Unlinked variant details: "
                    f"SKU={transformed.get('sku')}, "
                    f"Legacy ID={transformed.get('legacy_id')}, "
                    f"Parent Legacy ID={transformed.get('legacy_parent_id')}, "
                    f"Legacy Base SKU={transformed.get('legacy_base_sku')}"
                )

        return transformed_records

    def transform_boolean_flags(
        self, transformed: Dict[str, Any], source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform boolean fields from various formats to Python boolean.

        Args:
            transformed: The transformed record dictionary.
            source: The original source record dictionary.

        Returns:
            Updated transformed record with boolean fields properly converted.
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

        sku = transformed.get("sku", "unknown")
        logger.debug(
            "Starting transform_boolean_flags for record with SKU: %s", sku
        )

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
                    "Converted boolean field %s -> %s: %s -> %s "
                    "(Source type: %s)",
                    source_field,
                    target_field,
                    value,
                    bool_value,
                    type(value).__name__
                )

        # Set a default value for is_active if not already set
        if "is_active" not in transformed:
            transformed["is_active"] = True
            logger.debug(
                "Set default is_active=True for record with SKU: %s", sku
            )

        # Ensure the critical fields are definitely in the transformed record
        is_active_val = transformed.get("is_active", "not set")
        logger.debug(
            "After transform_boolean_flags - SKU: %s, is_active: %s",
            sku, is_active_val
        )

        return transformed

    def transform_dimensions(
        self, transformed: Dict[str, Any], source: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract dimensions from legacy fields if present."""
        # Placeholder - implement actual dimension extraction if needed
        # e.g., from fields like 'Masse_Breite', 'Masse_Hoehe', etc.
        # transformed['length_mm'] = source.get('...')
        # transformed['width_mm'] = source.get('...')
        # transformed['height_mm'] = source.get('...')
        logger.debug(
            "Skipping dimension transformation (not implemented yet) for SKU: %s",
            transformed.get("sku", "N/A")
        )
        return transformed
