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
