# -*- coding: utf-8 -*-
"""
Management command for importing products from external sources.
"""
from django.core.management.base import BaseCommand, CommandError  # noqa: F401
from pyerp.core.validators import ImportValidator, ValidationResult


class ProductImportValidator(ImportValidator):
    """Validator for product import data."""

    def validate_sku(self, value, row_data):

        """Validate the product SKU."""
        if not value:
            return ValidationResult(is_valid=False, errors={"sku": ["SKU is required"]})  # noqa: E501
        return ValidationResult(is_valid=True)

    def validate_name(self, value, row_data):

        """Validate the product name."""
        if not value:
            return ValidationResult(is_valid=False, errors={"name": ["Name is required"]})  # noqa: E501
        return ValidationResult(is_valid=True)

    def validate_list_price(self, value, row_data):

        """Validate the list price."""
        try:
            price = float(value)
            if price < 0:
                return ValidationResult(
                    is_valid=False,  # noqa: E128
                    errors={"list_price": ["Price cannot be negative"]}  # noqa: F841
                )
            return ValidationResult(is_valid=True)
        except (ValueError, TypeError):
            return ValidationResult(
                is_valid=False,  # noqa: E128
                errors={"list_price": ["Invalid price format"]}  # noqa: F841
  # noqa: F841
            )

    def cross_validate_row(self, validated_data):
        """Perform cross-field validation."""
        return ValidationResult(is_valid=True)
  # noqa: F841


class Command(BaseCommand):
    """Command to import products from external sources."""

    help = "Import products from CSV file"  # noqa: F841
  # noqa: F841

    def create_product_validator(self):

        """Create and return a product validator instance."""
        return ProductImportValidator()

    def validate_products(self, data):
        """Validate a list of product data."""
        validator = self.create_product_validator()
        results = []

        for row in data:
            result = validator.validate_row(row)
            results.append((row, result))

        return results

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Import products command executed")
        # Implementation for test purposes only
        return True
