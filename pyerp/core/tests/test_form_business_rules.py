"""
Tests for business rule validation in forms.

This module tests complex business rule validation scenarios in forms,
focusing on cross-field validation and conditional business logic.
"""

from django.test import TestCase
from django import forms

from pyerp.core.form_validation import ValidatedForm
from pyerp.core.validators import (
    ValidationResult,
    RequiredValidator,
    LengthValidator,
    RegexValidator,
    RangeValidator,
    ChoiceValidator,
    BusinessRuleValidator,
    CompoundValidator,
)


class ProductForm(ValidatedForm):
    """Form for product with business rule validation."""
    
    name = forms.CharField(max_length=100)
    sku = forms.CharField(max_length=50)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    sale_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    quantity = forms.IntegerField()
    category = forms.ChoiceField(choices=[
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('food', 'Food & Beverages'),
    ])
    
    def setup_validators(self):
        # Basic field validation
        self.add_validator('name', RequiredValidator())
        self.add_validator('name', LengthValidator(min_length=3, max_length=100))
        
        self.add_validator('sku', RequiredValidator())
        self.add_validator('sku', RegexValidator(
            r'^[A-Za-z0-9\-]+$',
            error_message="SKU can only contain letters, numbers, and hyphens"
        ))
        
        self.add_validator('price', RequiredValidator())
        self.add_validator('price', RangeValidator(
            min_value=0.01,
            error_message="Price must be greater than zero"
        ))
        
        self.add_validator('quantity', RequiredValidator())
        self.add_validator('quantity', RangeValidator(
            min_value=0,
            error_message="Quantity cannot be negative"
        ))
        
        self.add_validator('category', RequiredValidator())
        self.add_validator('category', ChoiceValidator(
            choices=['electronics', 'clothing', 'books', 'food'],
            error_message="Please select a valid category"
        ))
        
        # Business rule: Sale price must be less than regular price
        def sale_price_rule(value, **kwargs):
            result = ValidationResult()
            field_name = kwargs.get('field_name', 'sale_price')
            form = kwargs.get('form')
            
            if form and value:
                try:
                    price = float(form.cleaned_data.get('price', 0))
                    sale_price = float(value)
                    
                    if sale_price >= price:
                        result.add_error(field_name, "Sale price must be less than regular price")
                except (ValueError, TypeError):
                    result.add_error(field_name, "Invalid price format")
            
            return result
        
        self.add_validator('sale_price', BusinessRuleValidator(sale_price_rule))
        
        # Form-level business rule: Electronics products must have a SKU starting with 'E-'
        def electronics_sku_rule(cleaned_data):
            result = ValidationResult()
            
            category = cleaned_data.get('category')
            sku = cleaned_data.get('sku', '')
            
            if category == 'electronics' and not sku.startswith('E-'):
                result.add_error('sku', "Electronics SKUs must start with 'E-'")
                
            return result
        
        self.add_form_validator(electronics_sku_rule)


class OrderForm(ValidatedForm):
    """Form for orders with complex business rule validation."""
    
    customer_name = forms.CharField(max_length=100)
    customer_type = forms.ChoiceField(choices=[
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('partner', 'Partner')
    ])
    order_value = forms.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    discount_code = forms.CharField(max_length=20, required=False)
    payment_method = forms.ChoiceField(choices=[
        ('credit', 'Credit Card'),
        ('bank', 'Bank Transfer'),
        ('cash', 'Cash on Delivery')
    ])
    shipping_method = forms.ChoiceField(choices=[
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('pickup', 'Store Pickup')
    ])
    
    def setup_validators(self):
        # Basic validation
        self.add_validator('customer_name', RequiredValidator())
        self.add_validator('customer_type', RequiredValidator())
        self.add_validator('order_value', RequiredValidator())
        self.add_validator('order_value', RangeValidator(
            min_value=0.01,
            error_message="Order value must be greater than zero"
        ))
        
        self.add_validator('discount_percent', RangeValidator(
            min_value=0,
            max_value=100,
            error_message="Discount must be between 0-100%"
        ))
        
        # Business rule: Discount code required if discount percent > 0
        def discount_code_required(value, **kwargs):
            result = ValidationResult()
            field_name = kwargs.get('field_name', 'discount_code')
            form = kwargs.get('form')
            
            if form:
                discount_percent = form.cleaned_data.get('discount_percent')
                
                if discount_percent and float(discount_percent) > 0 and not value:
                    result.add_error(field_name, "Discount code is required when applying a discount")
            
            return result
        
        self.add_validator('discount_code', BusinessRuleValidator(discount_code_required))
        
        # Form-level validation rules
        
        # Rule 1: Wholesale customers get maximum 30% discount
        # Rule 2: Partners can use bank transfer, retail must use credit or cash
        # Rule 3: Order value limits for certain payment methods
        def order_business_rules(cleaned_data):
            result = ValidationResult()
            
            customer_type = cleaned_data.get('customer_type')
            discount_percent = cleaned_data.get('discount_percent')
            payment_method = cleaned_data.get('payment_method')
            order_value = cleaned_data.get('order_value')
            
            # Rule 1: Discount limits by customer type
            if discount_percent:
                discount = float(discount_percent)
                if customer_type == 'wholesale' and discount > 30:
                    result.add_error('discount_percent', "Wholesale customers can receive maximum 30% discount")
                elif customer_type == 'retail' and discount > 15:
                    result.add_error('discount_percent', "Retail customers can receive maximum 15% discount")
            
            # Rule 2: Payment method restrictions by customer type
            if customer_type == 'retail' and payment_method == 'bank':
                result.add_error('payment_method', "Retail customers cannot use bank transfers")
            
            # Rule 3: Order value limits for payment methods
            if order_value:
                order_val = float(order_value)
                if payment_method == 'cash' and order_val > 1000:
                    result.add_error('payment_method', "Cash payment not available for orders over $1,000")
            
            return result
        
        self.add_form_validator(order_business_rules)


class UserSubscriptionForm(ValidatedForm):
    """Form for user subscription with tiered validation rules."""
    
    email = forms.EmailField()
    plan = forms.ChoiceField(choices=[
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise')
    ])
    payment_frequency = forms.ChoiceField(choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual')
    ], required=False)
    company_name = forms.CharField(max_length=100, required=False)
    company_size = forms.ChoiceField(choices=[
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201+', '201+ employees')
    ], required=False)
    features = forms.MultipleChoiceField(choices=[
        ('reports', 'Advanced Reports'),
        ('api', 'API Access'),
        ('support', '24/7 Support'),
        ('users', 'Unlimited Users')
    ], required=False)
    
    def setup_validators(self):
        # Basic validation
        self.add_validator('email', RequiredValidator())
        self.add_validator('email', RegexValidator(
            r'^[\w.+-]+@[\w-]+\.[\w.-]+$',
            error_message="Please enter a valid email address"
        ))
        
        self.add_validator('plan', RequiredValidator())
        
        # Compound validator - company info required for premium and enterprise plans
        def company_required(value, **kwargs):
            form = kwargs.get('form')
            if not form:
                return ValidationResult()
                
            plan = form.cleaned_data.get('plan')
            return plan in ['premium', 'enterprise'] and not value
        
        company_validator = BusinessRuleValidator(
            lambda value, **kwargs: company_required(value, **kwargs),
            error_message="Company information is required for premium and enterprise plans"
        )
        
        self.add_validator('company_name', company_validator)
        self.add_validator('company_size', company_validator)
        
        # Form-level validation rules
        def subscription_rules(cleaned_data):
            result = ValidationResult()
            
            plan = cleaned_data.get('plan')
            payment_frequency = cleaned_data.get('payment_frequency')
            features = cleaned_data.get('features', [])
            
            # Rule 1: Paid plans require payment frequency
            if plan in ['basic', 'premium', 'enterprise'] and not payment_frequency:
                result.add_error('payment_frequency', "Please select a payment frequency")
            
            # Rule 2: Feature restrictions based on plan
            if plan == 'free' and features:
                if 'api' in features or 'support' in features:
                    result.add_error('features', "The selected features are not available in the free plan")
            
            if plan == 'basic' and 'users' in features:
                result.add_error('features', "Unlimited users is only available in premium and enterprise plans")
            
            return result
        
        self.add_form_validator(subscription_rules)


class BusinessRuleValidationTests(TestCase):
    """Tests for business rule validation in forms."""
    
    def test_product_sale_price_validation(self):
        """Test business rule for sale price lower than regular price."""
        # Valid case
        form = ProductForm(data={
            'name': 'Test Product',
            'sku': 'TST-123',
            'price': '100.00',
            'sale_price': '80.00',
            'quantity': 10,
            'category': 'books'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - sale price higher than regular price
        form = ProductForm(data={
            'name': 'Test Product',
            'sku': 'TST-123',
            'price': '100.00',
            'sale_price': '120.00',
            'quantity': 10,
            'category': 'books'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('sale_price', form.errors)
        self.assertIn('less than regular price', form.errors['sale_price'][0])
    
    def test_electronics_sku_rule(self):
        """Test business rule for electronics SKU format."""
        # Valid case
        form = ProductForm(data={
            'name': 'Test Electronics',
            'sku': 'E-123',
            'price': '100.00',
            'quantity': 10,
            'category': 'electronics'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - electronics item without proper SKU format
        form = ProductForm(data={
            'name': 'Test Electronics',
            'sku': 'ELEC123',
            'price': '100.00',
            'quantity': 10,
            'category': 'electronics'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('sku', form.errors)
        self.assertIn('must start with', form.errors['sku'][0])
        
        # Other categories don't need the E- prefix
        form = ProductForm(data={
            'name': 'Test Book',
            'sku': 'BK123',
            'price': '20.00',
            'quantity': 5,
            'category': 'books'
        })
        self.assertTrue(form.is_valid())
    
    def test_order_discount_code_required(self):
        """Test business rule for discount code requirement."""
        # Valid case - discount with code
        form = OrderForm(data={
            'customer_name': 'Test Customer',
            'customer_type': 'retail',
            'order_value': '150.00',
            'discount_percent': '10.00',
            'discount_code': 'SUMMER10',
            'payment_method': 'credit',
            'shipping_method': 'standard'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - discount without code
        form = OrderForm(data={
            'customer_name': 'Test Customer',
            'customer_type': 'retail',
            'order_value': '150.00',
            'discount_percent': '10.00',
            'discount_code': '',
            'payment_method': 'credit',
            'shipping_method': 'standard'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('discount_code', form.errors)
        self.assertIn('required when applying a discount', form.errors['discount_code'][0])
    
    def test_customer_type_discount_limits(self):
        """Test business rule for discount limits by customer type."""
        # Valid case - wholesale customer with allowed discount
        form = OrderForm(data={
            'customer_name': 'Wholesale Corp',
            'customer_type': 'wholesale',
            'order_value': '1000.00',
            'discount_percent': '30.00',
            'discount_code': 'BULK30',
            'payment_method': 'bank',
            'shipping_method': 'standard'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - wholesale customer with excessive discount
        form = OrderForm(data={
            'customer_name': 'Wholesale Corp',
            'customer_type': 'wholesale',
            'order_value': '1000.00',
            'discount_percent': '40.00',
            'discount_code': 'BULK40',
            'payment_method': 'bank',
            'shipping_method': 'standard'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('discount_percent', form.errors)
        self.assertIn('maximum 30% discount', form.errors['discount_percent'][0])
        
        # Invalid case - retail customer with excessive discount
        form = OrderForm(data={
            'customer_name': 'John Smith',
            'customer_type': 'retail',
            'order_value': '200.00',
            'discount_percent': '20.00',
            'discount_code': 'SALE20',
            'payment_method': 'credit',
            'shipping_method': 'express'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('discount_percent', form.errors)
        self.assertIn('maximum 15% discount', form.errors['discount_percent'][0])
    
    def test_payment_method_restrictions(self):
        """Test business rules for payment method restrictions."""
        # Invalid case - retail customer with bank transfer
        form = OrderForm(data={
            'customer_name': 'John Smith',
            'customer_type': 'retail',
            'order_value': '200.00',
            'payment_method': 'bank',
            'shipping_method': 'standard'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('payment_method', form.errors)
        self.assertIn('cannot use bank transfers', form.errors['payment_method'][0])
        
        # Invalid case - large order with cash payment
        form = OrderForm(data={
            'customer_name': 'John Smith',
            'customer_type': 'retail',
            'order_value': '1500.00',
            'payment_method': 'cash',
            'shipping_method': 'standard'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('payment_method', form.errors)
        self.assertIn('not available for orders over', form.errors['payment_method'][0])
    
    def test_subscription_payment_frequency(self):
        """Test business rule for subscription payment frequency."""
        # Valid case - free plan doesn't need payment frequency
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'free'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - paid plan without payment frequency
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'basic'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('payment_frequency', form.errors)
        self.assertIn('Please select a payment frequency', form.errors['payment_frequency'][0])
    
    def test_subscription_company_info(self):
        """Test business rule for company information requirement."""
        # Valid case - premium plan with company info
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'premium',
            'payment_frequency': 'annual',
            'company_name': 'Example Corp',
            'company_size': '11-50'
        })
        self.assertTrue(form.is_valid())
        
        # Invalid case - premium plan without company info
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'premium',
            'payment_frequency': 'annual'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)
        self.assertIn('company_size', form.errors)
        self.assertIn('required for premium', form.errors['company_name'][0])
    
    def test_subscription_feature_restrictions(self):
        """Test business rule for feature restrictions by plan."""
        # Invalid case - free plan with premium features
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'free',
            'features': ['api', 'reports']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('features', form.errors)
        self.assertIn('not available in the free plan', form.errors['features'][0])
        
        # Invalid case - basic plan with premium feature
        form = UserSubscriptionForm(data={
            'email': 'user@example.com',
            'plan': 'basic',
            'payment_frequency': 'monthly',
            'features': ['reports', 'users']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('features', form.errors)
        self.assertIn('only available in premium', form.errors['features'][0])


if __name__ == '__main__':
    TestCase.main() 