"""
Product data validators for the pyERP system.

This module provides validators specific to product data, including import validation.  # noqa: E501
"""

import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from django.utils.translation import gettext_lazy as translate
from django.core.exceptions import ValidationError

from pyerp.core.validators import (
    DecimalValidator,
    ImportValidator,
    LengthValidator,
    RangeValidator,
    RequiredValidator,
    SkuValidator,
    ValidationResult,
)
from pyerp.products.models import Product, ProductCategory

logger = logging.getLogger(__name__)


class ProductImportValidator(ImportValidator):
    """
    Validator for product data during import from legacy system.

    Validates and transforms product data from legacy 4D system during import.
    """

    def __init_translate(
        self,
        *,  # Make all arguments keyword-only
        strict: bool = False,
        transform_data: bool = True,
        default_category: Optional["ProductCategory"] = None,
    ) -> None:
        super().__init_translate(strict, transform_data)
        self.default_category = default_category

    def _pre_validate_row(
        self,
        row_data: dict[str, Any],
        result: ValidationResult,
        row_index: int | None = None,
    ) -> None:
        """
        Pre-validation checks for the entire row.

        Args:
            row_data: The row data dictionary
            result: ValidationResult to add errors/warnings to
            row_index: Optional index of the row being validated
        """
        logger.debug("Validating product data row %s", row_index or "unknown")

        # Check if product has minimal required fields
        if not row_data.get("sku") and not row_data.get("alteNummer"):
            result.add_error(
                "sku",
                translate(
                    "Product must have an SKU (either 'sku' or 'alteNummer' field)",
                ),
            )

        # Check if product has a name
        if not row_data.get("name") and not row_data.get("Bezeichnung"):
            result.add_error(
                "name",
                translate(
                    "Product must have a name (either 'name' or 'Bezeichnung' field)",
                ),
            )

    def _post_validate_row(
        self,
        row_data: dict[str, Any],
        result: ValidationResult,
        row_index: int | None = None,
    ) -> None:
        """
        Post-validation checks for cross-field business rules.

        Args:
            row_data: The row data dictionary
            result: ValidationResult to add errors/warnings to
            row_index: Optional index of the row being validated
        """
        if not self.transform_data and "sku" in row_data:
            if Product.objects.filter(sku=row_data["sku"]).exists():
                result.add_warning(
                    "sku",
                    translate("Product with this SKU already exists"),
                )

        # If parent and variant code are both set, validate the combination
        if "is_parent" in row_data and "variant_code" in row_data:
            if row_data["is_parent"] and row_data["variant_code"]:
                result.add_error(
                    "is_parent",
                    translate("Parent products should not have variant codes"),
                )

    def validate_sku(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[str, ValidationResult]:
        """
        Validate the SKU field.

        Args:
            value: The field value
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # Use alteNummer as SKU if sku is not provided
        if not value and "alteNummer" in row_data:
            value = row_data["alteNummer"]

        # Check if SKU is provided
        if not value:
            result.add_error("sku", translate("SKU is required"))
            return value, result

        # Validate SKU format
        sku_validator = SkuValidator()
        sku_result = sku_validator(value, field_name="sku")
        result.merge(sku_result)

        # Check SKU length
        length_validator = LengthValidator(min_length=1, max_length=50)
        length_result = length_validator(value, field_name="sku")
        result.merge(length_result)

        # Parse base_sku and variant_code if not already in the data
        if (
            "-" in value
            and "base_sku" not in row_data
            and "variant_code" not in row_data
        ):
            try:
                base_sku, variant_code = value.split("-", 1)
                row_data["base_sku"] = base_sku
                row_data["variant_code"] = variant_code
                row_data["is_parent"] = False
            except ValueError:
                result.add_warning(
                    "sku",
                    translate("Could not parse variant information from SKU"),
                )
        elif "base_sku" not in row_data:
            row_data["base_sku"] = value
            row_data["variant_code"] = ""
            row_data["is_parent"] = True

        return value, result

    def validate_name(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[str, ValidationResult]:
        """
        Validate the name field.

        Args:
            value: The field value
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # Use Bezeichnung as name if name is not provided
        if not value and "Bezeichnung" in row_data:
            value = row_data["Bezeichnung"]

        # Check if name is provided
        required_validator = RequiredValidator(translate("Product name is required"))
        required_result = required_validator(value, field_name="name")
        result.merge(required_result)

        # Check name length
        if value:
            length_validator = LengthValidator(min_length=1, max_length=255)
            length_result = length_validator(value, field_name="name")
            result.merge(length_result)

        return value, result

    def validate_list_price(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[Decimal, ValidationResult]:
        """
        Validate the list_price field.

        Args:
            value: The field value
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # Extract from Preise if available and not directly provided
        if (value is None or value == 0) and "Preise" in row_data:
            preise = row_data["Preise"]
            if isinstance(preise, dict) and "Coll" in preise:
                for price_item in preise["Coll"]:
                    if (
                        isinstance(price_item, dict)
                        and price_item.get("Art") == "Laden"
                    ):
                        try:
                            value = Decimal(str(price_item.get("Preis", 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning(
                                "list_price",
                                translate(
                                    "Could not parse list price from Preise data",
                                ),
                            )

        # Default to 0 if not found
        if value is None:
            value = Decimal("0.00")

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error(
                    "list_price",
                    translate("List price must be a valid decimal number"),
                )
                return Decimal("0.00"), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name="list_price")
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name="list_price")
        result.merge(range_result)

        return value, result

    def validate_wholesale_price(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[Decimal, ValidationResult]:
        """
        Validate the wholesale_price field.

        Args:
            value: The field value
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # Extract from Preise if available and not directly provided
        if (value is None or value == 0) and "Preise" in row_data:
            preise = row_data["Preise"]
            if isinstance(preise, dict) and "Coll" in preise:
                for price_item in preise["Coll"]:
                    if (
                        isinstance(price_item, dict)
                        and price_item.get("Art") == "Handel"
                    ):
                        try:
                            value = Decimal(str(price_item.get("Preis", 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning(
                                "wholesale_price",
                                translate(
                                    "Could not parse wholesale price from Preise data",
                                ),
                            )

        # Default to 0 if not found
        if value is None:
            value = Decimal("0.00")

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error(
                    "wholesale_price",
                    translate("Wholesale price must be a valid decimal number"),
                )
                return Decimal("0.00"), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name="wholesale_price")
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name="wholesale_price")
        result.merge(range_result)

        return value, result

    def validate_cost_price(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[Decimal, ValidationResult]:
        """
        Validate the cost_price field.

        Args:
            value: The field value
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # Extract from Preise if available and not directly provided
        if (value is None or value == 0) and "Preise" in row_data:
            preise = row_data["Preise"]
            if isinstance(preise, dict) and "Coll" in preise:
                for price_item in preise["Coll"]:
                    if (
                        isinstance(price_item, dict)
                        and price_item.get("Art") == "Einkauf"
                    ):
                        try:
                            value = Decimal(str(price_item.get("Preis", 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning(
                                "cost_price",
                                translate(
                                    "Could not parse cost price from Preise data",
                                ),
                            )

        # Default to 0 if not found
        if value is None:
            value = Decimal("0.00")

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error(
                    "cost_price",
                    translate("Cost price must be a valid decimal number"),
                )
                return Decimal("0.00"), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name="cost_price")
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name="cost_price")
        result.merge(range_result)

        return value, result

    def validate_category(
        self,
        value: Any,
        row_data: dict[str, Any],
        row_index: int | None = None,
    ) -> tuple[Optional["ProductCategory"], ValidationResult]:
        """
        Validate the category field.

        Args:
            value: The field value (category instance or code)
            row_data: The complete row data
            row_index: Optional index of the row being validated

        Returns:
            Tuple of (transformed_value, ValidationResult)
        """
        result = ValidationResult()

        # If already a ProductCategory instance, use it
        if isinstance(value, ProductCategory):
            return value, result

        # Try to use ArtGruppe from legacy data if category is not provided
        if not value and "ArtGruppe" in row_data:
            value = row_data["ArtGruppe"]

        # If still no category, use the default
        if not value:
            if self.default_category:
                return self.default_category, result
            result.add_warning(
                "category",
                translate("No category specified and no default category available"),
            )
            return None, result

        # If category is a string, try to find the category by code
        if isinstance(value, str):
            try:
                category = ProductCategory.objects.get(code=value)
                return category, result
            except ProductCategory.DoesNotExist:
                result.add_warning(
                    "category",
                    translate("Category with code '%(code)s' does not exist")
                    % {"code": value},
                )

                # Use default category as fallback
                if self.default_category:
                    return self.default_category, result

        return None, result


# Model-level validation methods that can be used in clean() methods


def validate_product_model(product: Product) -> bool:
    """
    Validate a product model instance.

    Args:
        product: The product instance to validate

    Returns:
        bool: True if validation passes, raises ValidationError otherwise
    """
    # Validate SKU
    if not product.sku or not product.sku.isalnum():
        raise ValidationError({"sku": ["Invalid SKU format"]})

    # Validate parent/variant relationship
    if product.is_parent and product.variant_code:
        raise ValidationError({
            "variant_code": ["Parent products cannot have variant codes"]
        })

    # Validate prices
    if product.list_price is not None and product.cost_price is not None:
        if product.list_price < product.cost_price:
            raise ValidationError({
                "list_price": ["List price cannot be less than cost"]
            })

    return True
