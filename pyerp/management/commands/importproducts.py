"""
Management command for importing products from external sources.
"""

from django.core.management.base import BaseCommand

from pyerp.core.validators import ImportValidator, ValidationResult


class ProductImportValidator(ImportValidator):
    """Validator for product import data."""

    def __init__(
        self,
        strict=False,
        transform_data=True,
        default_category=None,
    ):
        """Initialize the validator."""
        super().__init__(strict=strict, transform_data=transform_data)
        self.default_category = default_category

    def validate_sku(self, value, row_data, row_index=None):
        """Validate the product SKU."""
        result = ValidationResult()
        if not value:
            result.add_error("sku", "SKU is required")
            return None, result
        return value, result

    def validate_name(self, value, row_data, row_index=None):
        """Validate the product name."""
        result = ValidationResult()
        if not value:
            result.add_error("name", "Name is required")
            return None, result
        return value, result

    def validate_list_price(self, value, row_data, row_index=None):
        """Validate the list price."""
        result = ValidationResult()
        try:
            price = float(value)
            if price < 0:
                result.add_error("list_price", "Price cannot be negative")
                return None, result
            return price, result
        except (ValueError, TypeError):
            result.add_error("list_price", "Invalid price format")
            return None, result

    def cross_validate_row(self, validated_data):
        """Perform cross-field validation."""
        return ValidationResult()


class Command(BaseCommand):
    """Command to import products from external sources."""

    help = "Import products from CSV file"

    def create_product_validator(self, strict=False, default_category=None):
        """Create and return a product validator instance."""
        return ProductImportValidator(
            strict=strict,
            transform_data=True,
            default_category=default_category,
        )

    def validate_products(self, data, validator=None):
        """Validate a list of product data."""
        if validator is None:
            validator = self.create_product_validator()
        valid_products = []

        for row in data:
            is_valid, validated_data, result = validator.validate_row(row)
            if is_valid:
                valid_products.append(validated_data)

        return valid_products

    def get_products_from_file(self, file_path):
        """Read and parse the input file."""
        if not file_path:
            raise FileNotFoundError("No file path provided")
        # This would be implemented to read the actual file
        raise FileNotFoundError(f"File not found: {file_path}")

    def create_or_update_product(self, product_data, default_category=None):
        """Create or update a product."""
        # This would be implemented to create/update the product
        pass

    def handle(self, *args, **options):
        """Execute the command."""
        if not options.get('file_path'):
            self.stderr.write("No file path provided")
            return False
            
        try:
            data = self.get_products_from_file(options['file_path'])
            default_category = None
            if 'default_category' in options:
                from pyerp.products.models import ProductCategory
                default_category = ProductCategory.objects.get(
                    code=options['default_category']
                )
                
            validator = self.create_product_validator(
                strict=options.get('strict', False),
                default_category=default_category,
            )
            
            valid_products = self.validate_products(data, validator)
                    
            if not valid_products:
                self.stderr.write("No valid products found")
                return False
                
            for product_data in valid_products:
                self.create_or_update_product(
                    product_data,
                    default_category=default_category,
                )
                
            self.stdout.write("Import products command executed successfully")
            return True
            
        except FileNotFoundError as e:
            self.stderr.write(str(e))
            raise
        except Exception as e:
            self.stderr.write(
                f"Error during import: {str(e)}"
            )
            return False
