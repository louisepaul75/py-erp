from rest_framework import serializers
from .models import Customer, Address, SalesRecord, SalesRecordItem


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    # Fields from primary address
    firstName = serializers.CharField(source='primary_address.first_name', read_only=True)
    lastName = serializers.CharField(source='primary_address.last_name', read_only=True)
    companyName = serializers.CharField(source='primary_address.company_name', read_only=True)
    emailMain = serializers.EmailField(source='primary_address.email', read_only=True)
    phoneMain = serializers.CharField(source='primary_address.phone', read_only=True)

    # Calculated/annotated fields
    orderCount = serializers.IntegerField(source='order_count', read_only=True)
    totalSpent = serializers.DecimalField(source='total_spent', max_digits=12, decimal_places=2, read_only=True)
    since = serializers.DateTimeField(source='created_at', read_only=True)

    # Fields determined by logic
    customerName = serializers.SerializerMethodField()
    isCompany = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    # Field to access the primary address easily within the serializer
    primary_address = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_number',
            'name',
            'customerName', # Combined name
            'firstName',
            'lastName',
            'companyName',
            'isCompany',
            'emailMain',
            'phoneMain',
            'orderCount',
            'since',
            'totalSpent',
            'avatar',
            # Include other fields from Customer if needed by frontend/filtering
            'customer_group',
            'delivery_block',
            'vat_id',
            'created_at', # Keep original if needed
            'modified_at',
            'primary_address', # Include for internal use
        ]
        read_only_fields = ['primary_address']

    def get_primary_address(self, obj) -> Address | None:
        # Access the prefetched primary address
        # 'primary_address_list' contains the result of the prefetch
        primary_addresses = getattr(obj, 'primary_address_list', [])
        return primary_addresses[0] if primary_addresses else None

    def get_isCompany(self, obj) -> bool:
        primary_address = self.get_primary_address(obj)
        # Determine if it's a company based on company_name presence
        return bool(primary_address and primary_address.company_name)

    def get_customerName(self, obj) -> str:
        primary_address = self.get_primary_address(obj)
        if primary_address:
            if primary_address.company_name:
                return primary_address.company_name
            else:
                return f"{primary_address.first_name or ''} {primary_address.last_name or ''}".strip()
        return obj.name or obj.customer_number # Fallback to customer name or number

    def get_avatar(self, obj) -> str | None:
        # Placeholder for avatar logic - assuming no avatar URL for now
        # You might fetch this from another field or generate initials
        return None


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
