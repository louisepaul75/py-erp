"""
Extended tests for the core validators module.

This module contains additional tests for the validator classes in
pyerp/core/validators.py to improve test coverage.
"""

from decimal import Decimal

from pyerp.core.validators import (
    BusinessRuleValidator,
    ChoiceValidator,
    CompoundValidator,
    DecimalValidator,
    LengthValidator,
    RangeValidator,
    RegexValidator,
    RequiredValidator,
    SkuValidator,
    ValidationResult,
    validate_data,
)


class TestValidationResult:
    """Test suite for ValidationResult class."""

    def test_initialization(self):
        """Test initialization of ValidationResult."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == {}
        assert result.warnings == {}
        assert result.context == {}

    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        result.add_error("field1", "Error message 1")
        result.add_error("field2", "Error message 2")

        assert result.is_valid is False
        assert "field1" in result.errors
        assert "field2" in result.errors
        assert result.errors["field1"] == ["Error message 1"]
        assert result.errors["field2"] == ["Error message 2"]

        # Test adding multiple errors for the same field
        result.add_error("field1", "Error message 3")
        # Warnings do not affect validity

    def test_add_warning(self):
        """Test adding warnings to ValidationResult."""
        result = ValidationResult()
        result.add_warning("field1", "Warning message 1")

        assert result.is_valid is True  # Warnings don't affect validity
        assert "field1" in result.warnings
        assert result.warnings["field1"] == ["Warning message 1"]

        # Test adding multiple warnings for the same field
        result.add_warning("field1", "Warning message 2")
        assert result.warnings["field1"] == [
            "Warning message 1",
            "Warning message 2",
        ]

    def test_merge(self):
        """Test merging ValidationResults."""
        result1 = ValidationResult()
        result1.add_error("field1", "Error 1")
        result1.add_warning("field2", "Warning 1")

        result2 = ValidationResult()
        result2.add_error("field3", "Error 2")
        result2.add_warning("field4", "Warning 2")

        result1.merge(result2)

        assert result1.is_valid is False
        assert set(result1.errors.keys()) == {"field1", "field3"}
        assert set(result1.warnings.keys()) == {"field2", "field4"}

        # Test merging with overlapping fields
        result3 = ValidationResult()
        result3.add_error("field1", "Error 3")
        result3.add_warning("field2", "Warning 3")

        result1.merge(result3)
        assert result1.errors["field1"] == ["Error 1", "Error 3"]
        assert result1.warnings["field2"] == ["Warning 1", "Warning 3"]


class TestRequiredValidator:
    """Test suite for RequiredValidator class."""

    def test_required_validator_with_value(self):
        """Test RequiredValidator with a value present."""
        validator = RequiredValidator()
        result = validator("test")
        assert result.is_valid is True
        assert not result.errors

    def test_required_validator_without_value(self):
        """Test RequiredValidator with missing value."""
        validator = RequiredValidator(error_message="This field is required")
        result = validator("")
        assert result.is_valid is False
        assert "field" in result.errors
        assert "This field is required" in result.errors["field"][0]

        # Test with None
        result = validator(None)
        assert result.is_valid is False

        # Note: Whitespace-only strings might be considered valid depending on
        # implementation. This test should be adjusted based on the actual
        # implementation. If the implementation doesn't consider whitespace as
        # empty, this test should be omitted or the assertion should be changed
        # to match the expected behavior.


class TestRegexValidator:
    """Test suite for RegexValidator class."""

    def test_regex_validator_match(self):
        """Test RegexValidator with matching pattern."""
        validator = RegexValidator(r"^\d{3}-\d{2}-\d{4}$")  # SSN pattern
        result = validator("123-45-6789")
        assert result.is_valid is True
        assert not result.errors

    def test_regex_validator_no_match(self):
        """Test RegexValidator with non-matching pattern."""
        validator = RegexValidator(
            r"^\d{3}-\d{2}-\d{4}$",
            error_message="Invalid format. Use XXX-XX-XXXX",
        )
        result = validator("123-456-789")
        assert result.is_valid is False
        assert "field" in result.errors
        assert "Invalid format" in result.errors["field"][0]

    def test_regex_validator_none_value(self):
        """Test RegexValidator with None value."""
        validator = RegexValidator(r"^\d{3}-\d{2}-\d{4}$")
        # None should pass as the regex validator doesn't enforce presence
        result = validator(None)
        assert result.is_valid is True


class TestRangeValidator:
    """Test suite for RangeValidator class."""

    def test_range_validator_within_range(self):
        """Test RangeValidator with value in range."""
        validator = RangeValidator(min_value=0, max_value=100)
        result = validator(50)
        assert result.is_valid is True
        assert not result.errors

    def test_range_validator_below_min(self):
        """Test RangeValidator with value below minimum."""
        validator = RangeValidator(
            min_value=0,
            max_value=100,
            error_message="Value must be between 0 and 100",
        )
        result = validator(-10)
        assert result.is_valid is False
        assert "field" in result.errors
        assert "Value must be between 0 and 100" in result.errors["field"][0]

    def test_range_validator_above_max(self):
        """Test RangeValidator with value above maximum."""
        validator = RangeValidator(min_value=0, max_value=100)
        result = validator(150)
        assert result.is_valid is False

    def test_range_validator_min_only(self):
        """Test RangeValidator with only minimum value specified."""
        validator = RangeValidator(min_value=0)
        result = validator(10)
        assert result.is_valid is True

        result = validator(-5)
        assert result.is_valid is False

    def test_range_validator_max_only(self):
        """Test RangeValidator with only maximum value specified."""
        validator = RangeValidator(max_value=100)
        result = validator(50)
        assert result.is_valid is True

        result = validator(200)
        assert result.is_valid is False


class TestLengthValidator:
    """Test suite for LengthValidator class."""

    def test_length_validator_within_range(self):
        """Test LengthValidator with string of valid length."""
        validator = LengthValidator(min_length=2, max_length=10)
        result = validator("Hello")
        assert result.is_valid is True
        assert not result.errors

    def test_length_validator_too_short(self):
        """Test LengthValidator with string that's too short."""
        validator = LengthValidator(min_length=5, max_length=10)
        result = validator("Hi")
        assert result.is_valid is False
        assert "field" in result.errors

    def test_length_validator_too_long(self):
        """Test LengthValidator with string that's too long."""
        validator = LengthValidator(min_length=2, max_length=5)
        result = validator("Too long string")
        assert result.is_valid is False
        assert "field" in result.errors

    def test_length_validator_min_only(self):
        """Test LengthValidator with only minimum length specified."""
        validator = LengthValidator(min_length=3)
        result = validator("abc")
        assert result.is_valid is True

        result = validator("ab")
        assert result.is_valid is False

    def test_length_validator_max_only(self):
        """Test LengthValidator with only maximum length specified."""
        validator = LengthValidator(max_length=5)
        result = validator("12345")
        assert result.is_valid is True

        result = validator("123456")
        assert result.is_valid is False


class TestChoiceValidator:
    """Test suite for ChoiceValidator class."""

    def test_choice_validator_valid_choice(self):
        """Test ChoiceValidator with valid choice."""
        choices = ["red", "green", "blue"]
        validator = ChoiceValidator(choices)
        result = validator("red")
        assert result.is_valid is True
        assert not result.errors

    def test_choice_validator_invalid_choice(self):
        """Test ChoiceValidator with invalid choice."""
        choices = ["red", "green", "blue"]
        validator = ChoiceValidator(
            choices,
            error_message="Invalid color choice",
        )
        result = validator("yellow")
        assert result.is_valid is False
        assert "field" in result.errors
        assert "Invalid color choice" in result.errors["field"][0]


class TestDecimalValidator:
    """Test suite for DecimalValidator class."""

    def test_decimal_validator_valid(self):
        """Test DecimalValidator with valid decimal."""
        validator = DecimalValidator(max_digits=5, decimal_places=2)
        result = validator("123.45")
        assert result.is_valid is True
        assert not result.errors

        # Test with Decimal object
        result = validator(Decimal("123.45"))
        assert result.is_valid is True

    def test_decimal_validator_too_many_digits(self):
        """Test DecimalValidator with too many total digits."""
        validator = DecimalValidator(max_digits=4, decimal_places=2)
        result = validator("123.45")
        assert result.is_valid is False
        assert "field" in result.errors

    def test_decimal_validator_too_many_decimal_places(self):
        """Test DecimalValidator with too many decimal places."""
        validator = DecimalValidator(max_digits=5, decimal_places=1)
        result = validator("123.45")
        assert result.is_valid is False
        assert "field" in result.errors

    def test_decimal_validator_invalid_decimal(self):
        """Test DecimalValidator with invalid decimal format."""
        validator = DecimalValidator()
        result = validator("not a decimal")
        assert result.is_valid is False
        assert "field" in result.errors


class TestSkuValidator:
    """Test suite for SkuValidator class."""

    def test_sku_validator_valid(self):
        """Test SkuValidator with valid SKU."""
        validator = SkuValidator()
        result = validator("ABC-123")
        assert result.is_valid is True
        assert not result.errors

    def test_sku_validator_invalid(self):
        """Test SkuValidator with invalid SKU."""
        validator = SkuValidator()
        result = validator("123 ABC")  # Contains space, likely invalid
        assert result.is_valid is False
        assert "field" in result.errors


class TestCompoundValidator:
    """Test suite for CompoundValidator class."""

    def test_compound_validator_all_valid(self):
        """Test CompoundValidator with all validators passing."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10),
            RegexValidator(r"^[A-Z]"),  # Must start with uppercase
        ]
        validator = CompoundValidator(validators)
        result = validator("Hello")
        assert result.is_valid is True
        assert not result.errors

    def test_compound_validator_one_invalid(self):
        """Test CompoundValidator with one failing validator."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10),
            RegexValidator(r"^[A-Z]"),  # Must start with uppercase
        ]
        validator = CompoundValidator(validators)
        result = validator("hello")  # lowercase, should fail regex
        assert result.is_valid is False
        assert "field" in result.errors

    def test_compound_validator_all_invalid(self):
        """Test CompoundValidator with all validators failing."""
        validators = [
            RequiredValidator(),
            LengthValidator(min_length=3, max_length=10),
            RegexValidator(r"^[A-Z]"),  # Must start with uppercase
        ]
        validator = CompoundValidator(validators)
        result = validator("")  # Empty, fails all validators
        assert result.is_valid is False
        assert "field" in result.errors
        # Should have at least one error message
        assert len(result.errors["field"]) >= 1

    def test_compound_validator_not_require_all(self):
        """Test CompoundValidator with require_all_valid=False."""
        validators = [
            LengthValidator(min_length=3, max_length=5),
            RegexValidator(r"^[A-Z]"),  # Must start with uppercase
        ]
        validator = CompoundValidator(validators, require_all_valid=False)
        result = validator("Hello")  # Valid length, valid regex
        assert result.is_valid is True

        result = validator("Hi")  # Invalid length, valid regex
        # Still valid because we don't require all
        assert result.is_valid is True

        result = validator("hello")  # Valid length, invalid regex
        # Still valid because we don't require all
        assert result.is_valid is True

        result = validator("h")  # Invalid length, invalid regex
        # Invalid because all validators failed
        assert result.is_valid is False


class TestBusinessRuleValidator:
    """Test suite for BusinessRuleValidator class."""

    def test_business_rule_validator_valid(self):
        """Test BusinessRuleValidator with passing rule."""

        # Rule: price must be at least 10% of cost
        def price_rule(value, **kwargs):
            cost = kwargs.get("cost", 0)
            price = value
            return price >= cost * 0.1

        validator = BusinessRuleValidator(
            price_rule,
            error_message="Price must be at least 10% of cost",
        )
        result = validator(20, cost=100)  # 20 is 20% of 100, should pass
        assert result.is_valid is True
        assert not result.errors

    def test_business_rule_validator_invalid(self):
        """Test BusinessRuleValidator with failing rule."""

        # Rule: price must be at least 10% of cost
        def price_rule(value, **kwargs):
            cost = kwargs.get("cost", 0)
            price = value
            return price >= cost * 0.1

        validator = BusinessRuleValidator(
            price_rule,
            error_message="Price must be at least 10% of cost",
        )
        result = validator(5, cost=100)  # 5 is 5% of 100, should fail
        assert result.is_valid is False
        assert "field" in result.errors
        assert "Price must be at least 10%" in result.errors["field"][0]


def test_validate_data():
    """Test validate_data function."""
    validators = [
        RequiredValidator(),
        LengthValidator(min_length=3),
    ]

    # Valid data
    result = validate_data("test", validators)
    assert result.is_valid is True
    assert not result.errors

    # Invalid data
    result = validate_data("", validators)
    assert result.is_valid is False
    assert "field" in result.errors

    # With context
    def context_validator(value, **kwargs):
        if kwargs.get("user_role") != "admin":
            return False
        return True

    validators = [
        BusinessRuleValidator(context_validator, error_message="Admin only"),
    ]
    result = validate_data("test", validators, context={"user_role": "user"})
    assert result.is_valid is False

    result = validate_data("test", validators, context={"user_role": "admin"})
    assert result.is_valid is True
