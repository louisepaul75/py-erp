from django.db import models
from django.db.utils import OperationalError
from django.utils.translation import gettext_lazy as _


class SalesModel(models.Model):
    """
    Base model for sales-related models.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    legacy_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("ID in the legacy system"),
    )
    legacy_modified = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_(
            "Last modification timestamp in legacy system"
        ),
    )
    is_synchronized = models.BooleanField(
        default=False,
        help_text=_(
            "Whether this record is synchronized with the legacy system"
        ),
    )

    class Meta:
        abstract = True


class Customer(SalesModel):
    """
    Customer model representing business partners and clients.
    Maps to the Kunden table in the legacy system.
    """
    customer_number = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Customer number (maps to KundenNr in legacy system)"),
    )
    name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Customer name"),
    )
    legacy_address_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Address number in legacy system (AdrNr)"),
    )
    customer_group = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Customer group (maps to Kundengr in legacy system)"),
    )
    delivery_block = models.BooleanField(
        default=False,
        help_text=_("Whether deliveries are blocked (maps to Liefersperre)"),
    )
    price_group = models.CharField(
        max_length=10,
        blank=True,
        help_text=_("Price group (maps to Preisgru in legacy system)"),
    )
    vat_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("VAT ID number (maps to USt_IdNr in legacy system)"),
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Payment method (maps to Zahlungsart in legacy system)"),
    )
    shipping_method = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Shipping method (maps to Versandart in legacy system)"),
    )
    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Credit limit (maps to Kreditlimit in legacy system)"),
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Discount percentage (maps to Rabatt in legacy system)"),
    )
    payment_terms_discount_days = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Days for early payment discount (maps to SkontoTage)"),
    )
    payment_terms_net_days = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Days until payment is due (maps to NettoTage)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Internal notes about the customer"),
    )

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        app_label = "sales"
        indexes = [
            models.Index(fields=["customer_number"]),
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["customer_group"]),
        ]

    def __str__(self):
        return f"{self.customer_number}"


class Address(SalesModel):
    """
    Address model representing customer addresses.
    Maps to the Adressen table in the legacy system.
    One customer can have multiple addresses.
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="addresses",
        help_text=_("Customer this address belongs to"),
    )
    address_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Address number from legacy system"),
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("Whether this is the primary address for the customer"),
    )
    salutation = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Salutation (maps to Anrede in legacy system)"),
    )
    first_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("First name (maps to Vorname in legacy system)"),
    )
    last_name = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Last name (maps to Name1 in legacy system)"),
    )
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Company name (maps to Name2 in legacy system)"),
    )
    street = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Street address (maps to Strasse in legacy system)"),
    )
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text=_("Country code (maps to Land in legacy system)"),
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Postal code (maps to PLZ in legacy system)"),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("City (maps to Ort in legacy system)"),
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Phone number (maps to Telefon in legacy system)"),
    )
    fax = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Fax number (maps to Fax in legacy system)"),
    )
    email = models.EmailField(
        blank=True,
        help_text=_("Email address (maps to e_Mail in legacy system)"),
    )
    contact_person = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Contact person (maps to Ansprechp in legacy system)"),
    )
    formal_salutation = models.CharField(
        max_length=200,
        blank=True,
        help_text=_(
            "Formal salutation (maps to Briefanrede in legacy system)"
        ),
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        app_label = "sales"
        indexes = [
            models.Index(fields=["customer"]),
            models.Index(fields=["legacy_id"]),
            models.Index(fields=["postal_code"]),
            models.Index(fields=["email"]),
        ]
        constraints = [
            # Ensure only one primary address per customer
            models.UniqueConstraint(
                fields=["customer"],
                condition=models.Q(is_primary=True),
                name=(
                    "unique_primary_address_per_customer"
                ),
            ),
        ]

    def __str__(self):
        if self.company_name:
            return f"{self.company_name}, {self.city}"
        return f"{self.first_name} {self.last_name}, {self.city}"


def get_sales_status():
    """
    A safe helper function that can be imported to check if the sales module is working.
    This will be used by other modules that might attempt to import from sales.
    """
    try:
        from django.db import connection

        cursor = connection.cursor()
        cursor.close()
        return "Sales module database connection is working"
    except OperationalError:
        return "Sales module found but database is not available"
    except Exception as e:
        return f"Sales module error: {e!s}"


class PaymentTerms(SalesModel):
    """Payment terms for sales records."""
    name = models.CharField(max_length=50)
    days_due = models.IntegerField()
    discount_days = models.IntegerField(default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Payment Terms")
        verbose_name_plural = _("Payment Terms")
        app_label = "sales"
        unique_together = [('days_due', 'discount_days', 'discount_percent')]

    def __str__(self):
        if self.discount_percent > 0:
            return f"{self.discount_percent}% discount if paid within {self.discount_days} days, net {self.days_due} days"
        return f"Net {self.days_due} days"


class PaymentMethod(SalesModel):
    """Payment method for sales records."""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    requires_authorization = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")
        app_label = "sales"
        unique_together = [('name', 'code')]

    def __str__(self):
        return self.name


class ShippingMethod(SalesModel):
    """Shipping method for sales records."""
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    default_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Shipping Method")
        verbose_name_plural = _("Shipping Methods")
        app_label = "sales"
        unique_together = [('name', 'code')]

    def __str__(self):
        return self.name


class SalesRecord(SalesModel):
    """
    Sales record model representing invoices, proposals, delivery notes, etc.
    Maps to the Belege table in the legacy system.
    """
    RECORD_TYPE_CHOICES = [
        ('INVOICE', _('Invoice')),
        ('PROPOSAL', _('Proposal')),
        ('DELIVERY_NOTE', _('Delivery Note')),
        ('CREDIT_NOTE', _('Credit Note')),
        ('ORDER_CONFIRMATION', _('Order Confirmation')),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PAID', _('Paid')),
        ('OVERDUE', _('Overdue')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    record_number = models.CharField(
        max_length=50,
        help_text=_("Document number (maps to PapierNr in legacy system)"),
    )
    record_date = models.DateField(
        help_text=_("Document date (maps to Datum in legacy system)"),
    )
    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='INVOICE',
        help_text=_("Type of document (maps to Papierart in legacy system)"),
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.PROTECT,
        related_name='sales_records',
        null=True,
        blank=True,
        help_text=_("Customer associated with this record"),
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Subtotal amount before tax (maps to Netto in legacy system)"),
    )
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Tax amount (maps to MWST_EUR in legacy system)"),
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Shipping cost (maps to Frachtkosten in legacy system)"),
    )
    handling_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Handling fee (maps to Bearbeitungskos in legacy system)"),
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Total amount including tax (maps to Endbetrag in legacy system)"),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text=_("Payment status (derived from bezahlt in legacy system)"),
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date of payment (maps to ZahlungsDat in legacy system)"),
    )
    currency = models.CharField(
        max_length=3,
        default='EUR',
        help_text=_("Currency code (maps to Währung in legacy system)"),
    )
    tax_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Tax type (maps to MWSt_Art in legacy system)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Notes (maps to Text in legacy system)"),
    )
    payment_terms = models.ForeignKey(
        'PaymentTerms',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_records',
        help_text=_("Payment terms for this record"),
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_records',
        help_text=_("Payment method for this record"),
    )
    shipping_method = models.ForeignKey(
        'ShippingMethod',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_records',
        help_text=_("Shipping method for this record"),
    )
    shipping_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT,
        related_name='shipping_records',
        null=True,
        blank=True,
        help_text=_("Shipping address (maps to Lief_Adr in legacy system)"),
    )
    billing_address = models.ForeignKey(
        'Address',
        on_delete=models.PROTECT,
        related_name='billing_records',
        null=True,
        blank=True,
        help_text=_("Billing address (maps to Rech_Adr in legacy system)"),
    )

    class Meta:
        verbose_name = _("Sales Record")
        verbose_name_plural = _("Sales Records")
        app_label = "sales"
        indexes = [
            models.Index(fields=["record_number"]),
            models.Index(fields=["record_date"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["legacy_id"]),
        ]
        unique_together = [('record_number', 'record_type')]

    def __str__(self):
        return f"{self.get_record_type_display()} {self.record_number} ({self.record_date})"


class SalesRecordItem(SalesModel):
    """
    Sales record item model representing line items in sales records.
    Maps to the Belege_Pos table in the legacy system.
    """
    ITEM_TYPE_CHOICES = [
        ('PRODUCT', _('Product')),
        ('SERVICE', _('Service')),
        ('TEXT', _('Text')),
        ('DISCOUNT', _('Discount')),
        ('SHIPPING', _('Shipping')),
        ('FEE', _('Fee')),
    ]
    
    FULFILLMENT_STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('PARTIAL', _('Partially Fulfilled')),
        ('FULFILLED', _('Fulfilled')),
        ('CANCELLED', _('Cancelled')),
    ]
    
    sales_record = models.ForeignKey(
        'SalesRecord',
        on_delete=models.CASCADE,
        related_name='line_items',
        help_text=_("Sales record this item belongs to"),
    )
    position = models.IntegerField(
        help_text=_("Position in the sales record (maps to PosNr in legacy system)"),
    )
    legacy_sku = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Product code (maps to ArtNr in legacy system)"),
    )
    description = models.TextField(
        help_text=_("Item description (maps to Bezeichnung in legacy system)"),
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Quantity (maps to Menge in legacy system)"),
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Unit price (maps to Preis in legacy system)"),
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_("Discount percentage (maps to Rabatt in legacy system)"),
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text=_("Tax rate for this item"),
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Tax amount for this item"),
    )
    line_subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Line subtotal before tax"),
    )
    line_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Line total including tax (maps to Pos_Betrag in legacy system)"),
    )
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        default='PRODUCT',
        help_text=_("Type of item (maps to Art in legacy system)"),
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Notes for this item"),
    )
    fulfillment_status = models.CharField(
        max_length=20,
        choices=FULFILLMENT_STATUS_CHOICES,
        default='PENDING',
        help_text=_("Fulfillment status (derived from Picking_ok in legacy system)"),
    )
    fulfilled_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Fulfilled quantity (maps to Pick_Menge in legacy system)"),
    )
    product = models.ForeignKey(
        'products.VariantProduct',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_record_items',
        help_text=_("Product associated with this item"),
    )

    class Meta:
        verbose_name = _("Sales Record Item")
        verbose_name_plural = _("Sales Record Items")
        app_label = "sales"
        indexes = [
            models.Index(fields=["sales_record"]),
            models.Index(fields=["legacy_sku"]),
            models.Index(fields=["legacy_id"]),
        ]
        unique_together = [('sales_record', 'position')]
        ordering = ['sales_record', 'position']

    def __str__(self):
        return f"{self.sales_record} - Line {self.position}: {self.description} ({self.quantity} x {self.unit_price})"
