from rest_framework import serializers
from .models import Customer, Address, SalesRecord, SalesRecordItem


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class SalesRecordItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRecordItem
        fields = [
            "id",
            "legacy_id",
            "sales_record",
            "position",
            "legacy_sku",
            "description",
            "quantity",
            "unit_price",
            "discount_percentage",
            "tax_rate",
            "tax_amount",
            "line_subtotal",
            "line_total",
            "item_type",
            "notes",
            "fulfillment_status",
            "fulfilled_quantity",
            "product",
        ]


class SalesRecordSerializer(serializers.ModelSerializer):
    # line_items = SalesRecordItemSerializer(many=True, read_only=True) # Temporarily commented out for debugging
    # customer_name = serializers.CharField(source="customer.name", read_only=True) # Temporarily commented out for debugging

    class Meta:
        model = SalesRecord
        fields = [
            "id",
            "legacy_id",
            "record_number",
            "record_date",
            "record_type",
            "customer",
            # "customer_name", # Temporarily commented out
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "handling_fee",
            "total_amount",
            "payment_status",
            "payment_date",
            "currency",
            "tax_type",
            "notes",
            "payment_terms",
            "payment_method",
            "shipping_method",
            "shipping_address",
            "billing_address",
            # "line_items", # Temporarily commented out
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
