from rest_framework import serializers
from .models import Customer, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'is_primary', 'salutation', 'first_name', 'last_name',
            'company_name', 'street', 'country', 'postal_code', 'city',
            'phone', 'fax', 'email', 'contact_person', 'formal_salutation'
        ]


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_number', 'legacy_address_number', 'customer_group',
            'delivery_block', 'price_group', 'vat_id', 'payment_method',
            'shipping_method', 'credit_limit', 'discount_percentage',
            'payment_terms_discount_days', 'payment_terms_net_days',
            'notes', 'addresses'
        ]


class DummySalesSerializer(serializers.Serializer):
    """
    A dummy sales serializer to make the API documentation work.
    This is just a placeholder until real models are implemented.
    """

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(max_length=500, required=False)
    created_at = serializers.DateTimeField(read_only=True)
