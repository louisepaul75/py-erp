"""
Product data validators for the pyERP system.

This module provides validators specific to product data, including import validation.  # noqa: E501
"""

from decimal import Decimal, InvalidOperation
import logging
from typing import Any, Dict, Tuple, Optional, TYPE_CHECKING

from django.utils.translation import gettext_lazy as translate  # noqa: F401

from pyerp.core.validators import (  # noqa: F401
    ImportValidator, ValidationResult, RegexValidator, SkuValidator,  # noqa: E128
    DecimalValidator, RangeValidator, LengthValidator, RequiredValidator
)

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from pyerp.products.models import Product, ProductCategory

logger = logging.getLogger(__name__)


class ProductImportValidator(ImportValidator):
    """
    Validator for product data during import from legacy system.

    Validates and transforms product data from legacy 4D system during import.
    """

    def __init_translate(self, strict: bool = False, transform_data: bool = True,  # noqa: E501
  # noqa: E501, F841

                 default_category: Optional['ProductCategory'] = None):
        super().__init_translate(strict, transform_data)
        # Default category to use when none is specified
        self.default_category = default_category

    def _pre_validate_row(self, row_data: Dict[str, Any], result: ValidationResult,  # noqa: E501
                         row_index: Optional[int] = None) -> None:
        """
        Pre-validation checks for the entire row.

        Args:
            row_data: The row data dictionary
            result: ValidationResult to add errors/warnings to
            row_index: Optional index of the row being validated
        """
        # Log row being processed for debugging
        logger.debug(f"Validating product data row {row_index or 'unknown'}")

        # Check if product has minimal required fields
        if not row_data.get('sku') and not row_data.get('alteNummer'):
            result.add_error('sku', translate("Product must have an SKU (either 'sku' or 'alteNummer' field)"))  # noqa: E501

        # Check if product has a name
        if not row_data.get('name') and not row_data.get('Bezeichnung'):
            result.add_error('name', translate("Product must have a name (either 'name' or 'Bezeichnung' field)"))  # noqa: E501

    def _post_validate_row(self, row_data: Dict[str, Any], result: ValidationResult,  # noqa: E501
                          row_index: Optional[int] = None) -> None:
        """
        Post-validation checks for cross-field business rules.

        Args:
            row_data: The row data dictionary
            result: ValidationResult to add errors/warnings to
            row_index: Optional index of the row being validated
        """
        # Check if product with this SKU exists (if not in transform mode)
        if not self.transform_data and 'sku' in row_data:
            if Product.objects.filter(sku=row_data['sku']).exists():
                result.add_warning('sku', translate("Product with this SKU already exists"))  # noqa: E501

        # If parent and variant code are both set, validate the combination
        if 'is_parent' in row_data and 'variant_code' in row_data:
            if row_data['is_parent'] and row_data['variant_code']:
                result.add_error('is_parent', translate("Parent products should not have variant codes"))  # noqa: E501

    def validate_sku(self, value: Any, row_data: Dict[str, Any],
                    row_index: Optional[int] = None) -> Tuple[str, ValidationResult]:  # noqa: E501
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
        if not value and 'alteNummer' in row_data:
            value = row_data['alteNummer']

        # Check if SKU is provided
        if not value:
            result.add_error('sku', translate("SKU is required"))
            return value, result

        # Validate SKU format
        sku_validator = SkuValidator()
        sku_result = sku_validator(value, field_name='sku')
        result.merge(sku_result)

        # Check SKU length
        length_validator = LengthValidator(min_length=1, max_length=50)
        length_result = length_validator(value, field_name='sku')
        result.merge(length_result)

        # Parse base_sku and variant_code if not already in the data
        if '-' in value and 'base_sku' not in row_data and 'variant_code' not in row_data:  # noqa: E501
            try:
                base_sku, variant_code = value.split('-', 1)
                # Inject these values for later validation
                row_data['base_sku'] = base_sku
                row_data['variant_code'] = variant_code
                row_data['is_parent'] = False
            except ValueError:
                result.add_warning('sku', translate("Could not parse variant information from SKU"))  # noqa: E501
        elif 'base_sku' not in row_data:
            # If no variant, use the full SKU as base_sku
            row_data['base_sku'] = value
            row_data['variant_code'] = ''
            row_data['is_parent'] = True

        return value, result

    def validate_name(self, value: Any, row_data: Dict[str, Any],
                     row_index: Optional[int] = None) -> Tuple[str, ValidationResult]:  # noqa: E501
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
        if not value and 'Bezeichnung' in row_data:
            value = row_data['Bezeichnung']

        # Check if name is provided
        required_validator = RequiredValidator(translate("Product name is required"))  # noqa: E501
        required_result = required_validator(value, field_name='name')
        result.merge(required_result)

        # Check name length
        if value:
            length_validator = LengthValidator(min_length=1, max_length=255)
            length_result = length_validator(value, field_name='name')
            result.merge(length_result)

        return value, result

    def validate_list_price(self, value: Any, row_data: Dict[str, Any],
                           row_index: Optional[int] = None) -> Tuple[Decimal, ValidationResult]:  # noqa: E501
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
        if (value is None or value == 0) and 'Preise' in row_data:
            preise = row_data['Preise']
            if isinstance(preise, dict) and 'Coll' in preise:
                for price_item in preise['Coll']:
                    if isinstance(price_item, dict) and price_item.get('Art') == 'Laden':  # noqa: E501
                        try:
                            value = Decimal(str(price_item.get('Preis', 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning('list_price', translate("Could not parse list price from Preise data"))  # noqa: E501

        # Default to 0 if not found
        if value is None:
            value = Decimal('0.00')

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error('list_price', translate("List price must be a valid decimal number"))  # noqa: E501
                return Decimal('0.00'), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name='list_price')
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name='list_price')
        result.merge(range_result)

        return value, result

    def validate_wholesale_price(self, value: Any, row_data: Dict[str, Any],
                                row_index: Optional[int] = None) -> Tuple[Decimal, ValidationResult]:  # noqa: E501
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
        if (value is None or value == 0) and 'Preise' in row_data:
            preise = row_data['Preise']
            if isinstance(preise, dict) and 'Coll' in preise:
                for price_item in preise['Coll']:
                    if isinstance(price_item, dict) and price_item.get('Art') == 'Handel':  # noqa: E501
                        try:
                            value = Decimal(str(price_item.get('Preis', 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning('wholesale_price', translate("Could not parse wholesale price from Preise data"))  # noqa: E501

        # Default to 0 if not found
        if value is None:
            value = Decimal('0.00')

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error('wholesale_price', translate("Wholesale price must be a valid decimal number"))  # noqa: E501
                return Decimal('0.00'), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name='wholesale_price')
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name='wholesale_price')
        result.merge(range_result)

        return value, result

    def validate_cost_price(self, value: Any, row_data: Dict[str, Any],
                           row_index: Optional[int] = None) -> Tuple[Decimal, ValidationResult]:  # noqa: E501
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
        if (value is None or value == 0) and 'Preise' in row_data:
            preise = row_data['Preise']
            if isinstance(preise, dict) and 'Coll' in preise:
                for price_item in preise['Coll']:
                    if isinstance(price_item, dict) and price_item.get('Art') == 'Einkauf':  # noqa: E501
                        try:
                            value = Decimal(str(price_item.get('Preis', 0)))
                            break
                        except (InvalidOperation, TypeError):
                            result.add_warning('cost_price', translate("Could not parse cost price from Preise data"))  # noqa: E501

        # Default to 0 if not found
        if value is None:
            value = Decimal('0.00')

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            try:
                value = Decimal(str(value))
            except (InvalidOperation, TypeError):
                result.add_error('cost_price', translate("Cost price must be a valid decimal number"))  # noqa: E501
                return Decimal('0.00'), result

        # Validate decimal format
        decimal_validator = DecimalValidator(max_digits=10, decimal_places=2)
        decimal_result = decimal_validator(value, field_name='cost_price')
        result.merge(decimal_result)

        # Validate price range
        range_validator = RangeValidator(min_value=0)
        range_result = range_validator(value, field_name='cost_price')
        result.merge(range_result)

        return value, result

    def validate_category(self, value: Any, row_data: Dict[str, Any],
                         row_index: Optional[int] = None) -> Tuple[Optional['ProductCategory'], ValidationResult]:  # noqa: E501
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
        if not value and 'ArtGruppe' in row_data:
            value = row_data['ArtGruppe']

        # If still no category, use the default
        if not value:
            if self.default_category:
                return self.default_category, result
            else:
                result.add_warning('category', translate("No category specified and no default category available"))  # noqa: E501
                return None, result

        # If category is a string, try to find the category by code
        if isinstance(value, str):
            try:
                category = ProductCategory.objects.get(code=value)
                return category, result
            except ProductCategory.DoesNotExist:
                result.add_warning('category', translate("Category with code '%(code)s' does not exist") % {'code': value})  # noqa: E501

                # Use default category as fallback
                if self.default_category:
                    return self.default_category, result

        return None, result


# Model-level validation methods that can be used in clean() methods


def validate_product_model(product):
    """
    Validate a product model instance beyond field-level validation.

    Args:
        product: The Product instance to validate

    Raises:
        ValidationError: If the product fails validation
    """
    errors = {}

    # Check SKU format
    sku_validator = SkuValidator()
    sku_result = sku_validator(product.sku, field_name='sku')
    if not sku_result.is_valid:
        errors['sku'] = sku_result.errors['sku']

    # Check parent-variant relationship
    if product.is_parent and product.variant_code:
        errors.setdefault('is_parent', []).append(
            translate("Parent products should not have variant codes")  # noqa: E128
        )

    # Ensure base_sku is set
    if not product.base_sku:
        if '-' in product.sku:
            base_sku, _ = product.sku.split('-', 1)
            product.base_sku = base_sku
        else:
            product.base_sku = product.sku
  # noqa: F841

    # Check prices
    if product.list_price < product.cost_price:
        errors.setdefault('list_price', []).append(
            translate("List price should not be less than cost price")  # noqa: E128
        )

    # Raise ValidationError if there are any errors
    if errors:
        from django.core.exceptions import ValidationError
        raise ValidationError(errors)
