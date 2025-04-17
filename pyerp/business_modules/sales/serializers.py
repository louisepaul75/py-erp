from rest_framework import serializers
from .models import (
    Customer,
    Address,
    SalesRecord,
    SalesRecordItem,
    SalesRecordRelationship,
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    # Fields from primary address
    firstName = serializers.CharField(
        source='primary_address.first_name', read_only=True
    )
    lastName = serializers.CharField(
        source='primary_address.last_name', read_only=True
    )
    companyName = serializers.CharField(
        source='primary_address.company_name', read_only=True
    )
    emailMain = serializers.EmailField(
        source='primary_address.email', read_only=True
    )
    phoneMain = serializers.CharField(
        source='primary_address.phone', read_only=True
    )
    # Added billing address fields
    billingStreet = serializers.CharField(
        source='primary_address.street', read_only=True
    )
    billingPostalCode = serializers.CharField(
        source='primary_address.postal_code', read_only=True
    )
    billingCity = serializers.CharField(
        source='primary_address.city', read_only=True
    )
    billingCountry = serializers.CharField(
        source='primary_address.country', read_only=True
    )

    # Calculated/annotated fields
    orderCount = serializers.IntegerField(source='order_count', read_only=True)
    totalSpent = serializers.DecimalField(
        source='total_spent', max_digits=12, decimal_places=2, read_only=True
    )
    since = serializers.DateTimeField(source='created_at', read_only=True)
    lastOrderDate = serializers.DateField(
        source='last_order_date', read_only=True, allow_null=True
    )  # Added last order date

    # Fields determined by logic
    customerName = serializers.SerializerMethodField()
    isCompany = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    # Renamed direct fields from model
    discount = serializers.DecimalField(
        source='discount_percentage',
        max_digits=5,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    creditLimit = serializers.DecimalField(
        source='credit_limit',
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True,
    )
    # Combined payment terms
    paymentTermsOverall = serializers.SerializerMethodField()

    # Field to access the primary address easily within the serializer
    primary_address = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_number',
            'name',
            'customerName',  # Combined name
            'firstName',
            'lastName',
            'companyName',
            'isCompany',
            'emailMain',
            'phoneMain',
            'orderCount',
            'since',
            'totalSpent',
            'lastOrderDate',  # Added
            'avatar',
            'customer_group',
            'delivery_block',
            'vat_id',
            'created_at',  # Keep original if needed
            'modified_at',
            # Address fields
            'billingStreet',
            'billingPostalCode',
            'billingCity',
            'billingCountry',
            # Payment/Discount fields
            'creditLimit',
            'discount',
            'paymentTermsOverall',
            # Internal field
            'primary_address',
        ]
        read_only_fields = ['primary_address']

    def get_primary_address(self, obj) -> Address | None:
        # Access the prefetched primary address
        primary_addresses = getattr(obj, 'primary_address_list', [])
        return primary_addresses[0] if primary_addresses else None

    def get_isCompany(self, obj) -> bool:
        primary_address = self.get_primary_address(obj)
        return bool(primary_address and primary_address.company_name)

    def get_customerName(self, obj) -> str:
        primary_address = self.get_primary_address(obj)
        if primary_address:
            if primary_address.company_name:
                return primary_address.company_name
            else:
                return (
                    f"{primary_address.first_name or ''} "
                    f"{primary_address.last_name or ''}".strip()
                )
        return obj.name or obj.customer_number

    def get_avatar(self, obj) -> str | None:
        # Placeholder for avatar logic
        return None

    def get_paymentTermsOverall(self, obj) -> str | None:
        """Generates a string representation of customer's payment terms."""
        discount_days = obj.payment_terms_discount_days
        net_days = obj.payment_terms_net_days
        discount_percent = obj.discount_percentage  # Use direct discount field

        if net_days is None:
            return None  # No payment terms set

        parts = []
        if (
            discount_days is not None
            and discount_percent is not None
            and discount_percent > 0
        ):
            parts.append(
                f"{discount_percent}% Skonto bei Zahlung innerhalb "
                f"{discount_days} Tagen"
            )

        parts.append(f"Netto {net_days} Tage")
        return ", ".join(parts)


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
    line_items = SalesRecordItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(
        source="customer.get_customerName", read_only=True
    )
    shipping_address_display = AddressSerializer(
        source="shipping_address", read_only=True
    )
    billing_address_display = AddressSerializer(
        source="billing_address", read_only=True
    )

    class Meta:
        model = SalesRecord
        fields = [
            "id",
            "legacy_id",
            "record_number",
            "record_date",
            "record_type",
            "customer",
            "customer_name",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "handling_fee",
            "total_amount",
            "payment_status",
            "delivery_status",
            "payment_date",
            "currency",
            "tax_type",
            "notes",
            "payment_terms",
            "payment_method",
            "shipping_method",
            "shipping_address",
            "billing_address",
            "shipping_address_display",
            "billing_address_display",
            "line_items",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "line_items",
            "customer_name",
            "shipping_address_display",
            "billing_address_display",
            "created_at",
            "modified_at",
        ]


class SalesRecordRelationshipSerializer(serializers.ModelSerializer):
    """
    Serializer for the SalesRecordRelationship model.
    """
    # Optionally include basic details of related records
    from_record_number = serializers.CharField(
        source='from_record.record_number', read_only=True
    )
    to_record_number = serializers.CharField(
        source='to_record.record_number', read_only=True
    )

    class Meta:
        model = SalesRecordRelationship
        fields = [
            "id",
            "from_record",
            "to_record",
            "relationship_type",
            "notes",
            "created_at",
            "modified_at",
            # Optional fields for easier display
            "from_record_number",
            "to_record_number",
        ]
        read_only_fields = [
            "created_at",
            "modified_at",
            "from_record_number",
            "to_record_number",
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
