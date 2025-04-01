"""
Tests for custom validator implementations.

This module tests custom validators and validator composition patterns,
ensuring the extensibility of the validation framework.
"""

import re
from decimal import Decimal
from django.test import TestCase
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator as DjangoRegexValidator

from pyerp.core.validators import (
    ValidationResult,
    Validator,
    RequiredValidator,
    RegexValidator,
    CompoundValidator,
    BusinessRuleValidator,
)
from pyerp.core.form_validation import ValidatedForm, ValidatedFormMixin


class CreditCardValidator(Validator):
    """Custom validator for credit card numbers using the Luhn algorithm."""
    
    def __init__(self, error_message=None):
        """Initialize with optional error message."""
        message = error_message or "Invalid credit card number"
        super().__init__(message)
    
    def _validate(self, value, result, **kwargs):
        """Validate credit card number using Luhn algorithm."""
        field_name = kwargs.get('field_name', 'card_number')
        
        # Skip empty values
        if not value:
            return
        
        # Remove spaces and dashes
        card_number = re.sub(r'[\s-]', '', value)
        
        # Check if all digits
        if not card_number.isdigit():
            result.add_error(field_name, self.message)
            return
        
        # Apply Luhn algorithm
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        if checksum % 10 != 0:
            result.add_error(field_name, self.message)


class PasswordStrengthValidator(Validator):
    """Custom validator for password strength with configurable requirements."""
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True,
                 require_digits=True, require_special=False, error_message=None):
        """Initialize with password requirements."""
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        message = error_message or "Password does not meet security requirements"
        super().__init__(message)
    
    def _validate(self, value, result, **kwargs):
        """Validate password strength against requirements."""
        field_name = kwargs.get('field_name', 'password')
        
        # Skip empty values
        if not value:
            return
        
        # Check minimum length
        if len(value) < self.min_length:
            result.add_error(
                field_name,
                f"Password must be at least {self.min_length} characters long"
            )
            return  # Stop validation if minimum length not met
        
        # Check for uppercase letters
        if self.require_uppercase and not any(c.isupper() for c in value):
            result.add_error(
                field_name,
                "Password must contain at least one uppercase letter"
            )
        
        # Check for lowercase letters
        if self.require_lowercase and not any(c.islower() for c in value):
            result.add_error(
                field_name,
                "Password must contain at least one lowercase letter"
            )
        
        # Check for digits
        if self.require_digits and not any(c.isdigit() for c in value):
            result.add_error(
                field_name,
                "Password must contain at least one digit"
            )
        
        # Check for special characters
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            result.add_error(
                field_name,
                "Password must contain at least one special character"
            )


class URLValidator(Validator):
    """Custom validator for URL format with optional protocol requirement."""
    
    def __init__(self, require_protocol=True, allowed_protocols=None, error_message=None):
        """Initialize with URL requirements."""
        self.require_protocol = require_protocol
        self.allowed_protocols = allowed_protocols or ['http', 'https']
        message = error_message or "Invalid URL format"
        super().__init__(message)
    
    def _validate(self, value, result, **kwargs):
        """Validate URL format."""
        field_name = kwargs.get('field_name', 'url')
        
        # Skip empty values
        if not value:
            return
        
        # Basic URL pattern
        if self.require_protocol:
            protocols = '|'.join(self.allowed_protocols)
            # Updated regex to allow optional port (:port) and optional query string (?...) after path
            pattern = rf'^({protocols})://([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(:\d+)?(/[\w\-.~!$&\'()*+,;=:@/%]*)?(\?[^\s]*)?$'
        else:
            # Updated regex to allow optional query string (?...) after path for both domain and localhost parts
            domain_part = r'([a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])'
            localhost_part = r'localhost(:\d+)?'
            path_part = r'(/[\w\-.~!$&\'()*+,;=:@/%]*)?'
            query_part = r'(\?[^\s]*)?'
            pattern = rf'^(({domain_part}|{localhost_part}){path_part}{query_part})$'
        
        if not re.match(pattern, value):
            if self.require_protocol:
                protocols_str = ', '.join(self.allowed_protocols)
                error_msg = f"URL must start with {protocols_str}:// and have a valid domain"
            else:
                error_msg = "Invalid URL format"
            
            result.add_error(field_name, error_msg)


class ISBNValidator(Validator):
    """Custom validator for ISBN-10 and ISBN-13 numbers."""
    
    def __init__(self, error_message=None):
        """Initialize with optional error message."""
        message = error_message or "Invalid ISBN format"
        super().__init__(message)
    
    def _validate(self, value, result, **kwargs):
        """Validate ISBN-10 or ISBN-13 format."""
        field_name = kwargs.get('field_name', 'isbn')
        
        # Skip empty values
        if not value:
            return
        
        # Remove dashes and spaces
        isbn = re.sub(r'[\s-]', '', value)
        
        # Validate ISBN-10
        if len(isbn) == 10:
            if not self._validate_isbn10(isbn):
                result.add_error(field_name, "Invalid ISBN-10 format")
        
        # Validate ISBN-13
        elif len(isbn) == 13:
            if not self._validate_isbn13(isbn):
                result.add_error(field_name, "Invalid ISBN-13 format")
        
        # Invalid length
        else:
            result.add_error(field_name, "ISBN must be 10 or 13 characters")
    
    def _validate_isbn10(self, isbn):
        """Validate ISBN-10 format and checksum."""
        # Check if first 9 characters are digits
        if not isbn[:9].isdigit():
            return False
        
        # Check if last character is digit or 'X'
        if not (isbn[9].isdigit() or isbn[9] == 'X'):
            return False
        
        # Calculate checksum
        checksum = sum((10 - i) * (int(isbn[i]) if isbn[i].isdigit() else 10) 
                       for i in range(10))
        
        return checksum % 11 == 0
    
    def _validate_isbn13(self, isbn):
        """Validate ISBN-13 format and checksum."""
        # Check if all characters are digits
        if not isbn.isdigit():
            return False
        
        # Calculate checksum
        checksum = sum(int(isbn[i]) * (1 if i % 2 == 0 else 3) for i in range(13))
        
        return checksum % 10 == 0


class PaymentForm(ValidatedForm):
    """Form with custom credit card validation."""
    
    card_type = forms.ChoiceField(choices=[
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
    ])
    card_number = forms.CharField(max_length=19)
    card_expiry = forms.CharField(max_length=7) # Assumes MM/YYYY
    card_cvv = forms.CharField(max_length=4)
    
    def setup_validators(self):
        # Add standard validators
        self.add_validator('card_type', RequiredValidator())
        self.add_validator('card_number', RequiredValidator())
        self.add_validator('card_expiry', RequiredValidator())
        self.add_validator('card_cvv', RequiredValidator())
        
        # Add custom credit card validator for card number format/checksum
        self.add_validator('card_number', CreditCardValidator())
        
        # Add regex validator for expiry date (MM/YYYY)
        self.add_validator('card_expiry', RegexValidator(
            r'^(0[1-9]|1[0-2])\/20[2-9]\d$', # MM/YYYY
            error_message="Expiry date must be in MM/YYYY format"
        ))
        
        # Removed the previous BusinessRuleValidator for CVV
        # Validation now happens in clean()

    def clean(self):
        """Perform cross-field validation after standard cleaning."""
        cleaned_data = super().clean()
        
        card_type = cleaned_data.get("card_type")
        card_cvv = cleaned_data.get("card_cvv")

        if card_type and card_cvv:
            # AmEx requires 4-digit CVV
            if card_type == 'amex':
                if not (len(card_cvv) == 4 and card_cvv.isdigit()):
                    self.add_error('card_cvv', "American Express requires a 4-digit CVV")
            # Other cards use 3-digit CVV
            else:
                if not (len(card_cvv) == 3 and card_cvv.isdigit()):
                    self.add_error('card_cvv', "CVV must be 3 digits for this card type")

        return cleaned_data


class BookForm(ValidatedForm):
    """Form with custom ISBN validation."""
    
    title = forms.CharField(max_length=200)
    isbn = forms.CharField(max_length=17)
    author = forms.CharField(max_length=100)
    
    def setup_validators(self):
        # Add standard validators
        self.add_validator('title', RequiredValidator())
        self.add_validator('author', RequiredValidator())
        
        # Add custom ISBN validator
        self.add_validator('isbn', ISBNValidator())


class RegistrationForm(ValidatedForm):
    """Form with combined Django and custom validation."""
    
    username = forms.CharField(
        max_length=50,
        validators=[
            DjangoRegexValidator(
                regex=r'^[a-zA-Z0-9_]+$', 
                message="Username can only contain letters, numbers, and underscores"
            )
        ]
    )
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    # Use URL field with extra parameters to ensure strict validation
    website = forms.URLField(
        required=False,
    )
    
    def setup_validators(self):
        """Add our custom validators to the form."""
        # Add password strength validator
        self.add_validator('password', PasswordStrengthValidator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        ))
        
        # Add custom URL validator to ensure protocol is present
        self.add_validator('website', URLValidator(
            require_protocol=True,
            allowed_protocols=['http', 'https']
        ))
        
        # Form-level validation for password confirmation
        def password_match(cleaned_data):
            result = ValidationResult()
            password = cleaned_data.get('password')
            confirm_password = cleaned_data.get('confirm_password')
            if password and confirm_password and password != confirm_password:
                result.add_error('confirm_password', "Passwords do not match")
            return result
        
        self.add_form_validator(password_match)


class CustomValidatorTests(TestCase):
    """Tests for custom validators."""
    
    def test_credit_card_validator(self):
        """Test credit card validation using Luhn algorithm."""
        validator = CreditCardValidator()
        
        # Test with valid credit card numbers
        valid_cards = [
            '4532015112830366',  # Visa
            '5424000000000015',  # MasterCard
            '378282246310005',   # American Express
            '6011000990139424',  # Discover
            '3566002020360505',  # JCB
            '4111 1111 1111 1111',  # Visa with spaces
            '5555-5555-5555-4444',  # MasterCard with dashes
        ]
        
        for card in valid_cards:
            result = validator(card, field_name='card_number')
            self.assertFalse(result.has_errors())
        
        # Test with invalid credit card numbers
        invalid_cards = [
            '1234567890123456',  # Random numbers
            '4532015112830367',  # Visa with wrong checksum
            'ABCDEFGHIJKLMNOP',  # Non-numeric
            '123456789',         # Too short
        ]
        
        for card in invalid_cards:
            result = validator(card, field_name='card_number')
            self.assertTrue(result.has_errors())
            self.assertIn('card_number', result.errors)
    
    def test_password_strength_validator(self):
        """Test password strength validation."""
        validator = PasswordStrengthValidator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special=True
        )
        
        # Test with valid strong password
        result = validator('P@ssw0rd123!', field_name='password')
        self.assertFalse(result.has_errors())
        
        # Test with too short password
        result = validator('P@ss1', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('password', result.errors)
        self.assertIn('at least 8 characters', result.errors['password'][0])
        
        # Test missing uppercase
        result = validator('p@ssw0rd123!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('uppercase', result.errors['password'][0])
        
        # Test missing lowercase
        result = validator('P@SSW0RD123!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('lowercase', result.errors['password'][0])
        
        # Test missing digit
        result = validator('P@ssword!', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('digit', result.errors['password'][0])
        
        # Test missing special character
        result = validator('Passw0rd123', field_name='password')
        self.assertTrue(result.has_errors())
        self.assertIn('special character', result.errors['password'][0])
    
    def test_url_validator(self):
        """Test URL format validation."""
        # Default validator - requires protocol
        validator = URLValidator()
        
        # Test with valid URLs
        valid_urls = [
            'https://example.com',
            'http://subdomain.example.com',
            'https://example.com/path',
            'https://example.com/path?query=value',
            'https://example.com:8080',
        ]
        
        for url in valid_urls:
            result = validator(url, field_name='url')
            self.assertFalse(result.has_errors())
        
        # Test with invalid URLs
        invalid_urls = [
            'example.com',  # Missing protocol
            'ftp://example.com',  # Wrong protocol
            'https:/example.com',  # Malformed protocol
            'https://invalid domain.com',  # Space in domain
        ]
        
        for url in invalid_urls:
            result = validator(url, field_name='url')
            self.assertTrue(result.has_errors())
            self.assertIn('url', result.errors)
        
        # Test validator without protocol requirement
        no_protocol_validator = URLValidator(require_protocol=False)
        
        # These should now be valid
        previously_invalid = [
            'example.com',
            'subdomain.example.com',
            'example.com/path?query=value',
            'localhost:8080',
        ]
        
        for url in previously_invalid:
            result = no_protocol_validator(url, field_name='url')
            self.assertFalse(result.has_errors())
    
    def test_isbn_validator(self):
        """Test ISBN format validation."""
        validator = ISBNValidator()
        
        # Test with valid ISBN-10
        valid_isbn10 = [
            '0-306-40615-2',
            '0306406152',
            '0-7167-0344-0',
            '0716703440',
        ]
        
        for isbn in valid_isbn10:
            result = validator(isbn, field_name='isbn')
            self.assertFalse(result.has_errors())
        
        # Test with valid ISBN-13
        valid_isbn13 = [
            '978-0-306-40615-7',
            '9780306406157',
            '978-3-16-148410-0',
            '9783161484100',
        ]
        
        for isbn in valid_isbn13:
            result = validator(isbn, field_name='isbn')
            self.assertFalse(result.has_errors())
        
        # Test with invalid ISBNs
        invalid_isbns = [
            '0-306-40615-3',  # Wrong check digit for ISBN-10
            '978-0-306-40615-8',  # Wrong check digit for ISBN-13
            '12345',  # Too short
            'ABCDEFGHIJ',  # Non-numeric
            '9780306406158X',  # Too long
        ]
        
        for isbn in invalid_isbns:
            result = validator(isbn, field_name='isbn')
            self.assertTrue(result.has_errors())
            self.assertIn('isbn', result.errors)


class FormWithCustomValidatorsTests(TestCase):
    """Tests for forms using custom validators."""
    
    def test_payment_form_validation(self):
        """Test payment form with credit card validation."""
        # Valid Visa card
        form = PaymentForm(data={
            'card_type': 'visa',
            'card_number': '4111 1111 1111 1111',
            'card_expiry': '12/2025',
            'card_cvv': '123',
        })
        self.assertTrue(form.is_valid())
        
        # Invalid card number
        form = PaymentForm(data={
            'card_type': 'visa',
            'card_number': '4111 1111 1111 1112',  # Invalid checksum
            'card_expiry': '12/2025',
            'card_cvv': '123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('card_number', form.errors)
        
        # Invalid expiry format
        form = PaymentForm(data={
            'card_type': 'visa',
            'card_number': '4111 1111 1111 1111',
            'card_expiry': '12-2025',  # Wrong format
            'card_cvv': '123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('card_expiry', form.errors)
        
        # AmEx with wrong CVV length
        form = PaymentForm(data={
            'card_type': 'amex',
            'card_number': '378282246310005',
            'card_expiry': '12/2025',
            'card_cvv': '123',  # Should be 4 digits for AmEx
        })
        self.assertFalse(form.is_valid())
        self.assertIn('card_cvv', form.errors)
        self.assertIn('4-digit', form.errors['card_cvv'][0])
        
        # Visa with wrong CVV length
        form = PaymentForm(data={
            'card_type': 'visa',
            'card_number': '4111 1111 1111 1111',
            'card_expiry': '12/2025',
            'card_cvv': '1234',  # Should be 3 digits for Visa
        })
        self.assertFalse(form.is_valid())
        self.assertIn('card_cvv', form.errors)
        self.assertIn('3 digits', form.errors['card_cvv'][0])
    
    def test_book_form_validation(self):
        """Test book form with ISBN validation."""
        # Valid ISBN-10
        form = BookForm(data={
            'title': 'Test Book',
            'isbn': '0-306-40615-2',
            'author': 'Test Author',
        })
        self.assertTrue(form.is_valid())
        
        # Valid ISBN-13
        form = BookForm(data={
            'title': 'Test Book',
            'isbn': '978-0-306-40615-7',
            'author': 'Test Author',
        })
        self.assertTrue(form.is_valid())
        
        # Invalid ISBN
        form = BookForm(data={
            'title': 'Test Book',
            'isbn': '0-306-40615-X',  # Invalid check digit
            'author': 'Test Author',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)
    
    def test_registration_form_validation(self):
        """Test registration form with password and URL validation."""
        # Valid form
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'P@ssw0rd123!',
            'confirm_password': 'P@ssw0rd123!',
            'website': 'https://example.com',
        })
        self.assertTrue(form.is_valid())
        
        # Invalid username
        form = RegistrationForm(data={
            'username': 'invalid user!',  # Contains space and special character
            'email': 'user@example.com',
            'password': 'P@ssw0rd123!',
            'confirm_password': 'P@ssw0rd123!',
            'website': 'https://example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Weak password
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'password',  # Missing uppercase, digit, special char
            'confirm_password': 'password',
            'website': 'https://example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Password mismatch
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'P@ssw0rd123!',
            'confirm_password': 'DifferentP@ss!',
            'website': 'https://example.com',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
        self.assertIn('match', form.errors['confirm_password'][0])
        
        # Invalid URL format - use a completely invalid URL format that can't be auto-corrected
        form = RegistrationForm(data={
            'username': 'validuser',
            'email': 'user@example.com',
            'password': 'P@ssw0rd123!',
            'confirm_password': 'P@ssw0rd123!',
            'website': 'invalid url with spaces',  # Invalid URL that can't be fixed by adding a scheme
        })
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)


if __name__ == '__main__':
    TestCase.main() 