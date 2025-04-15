from django.db import models
from django.utils.translation import gettext_lazy as _


class CalculatedExchangeRate(models.Model):
   
    base_currency = models.ForeignKey(
        "Currency",  # ← string reference to the model
        on_delete=models.CASCADE,
        related_name="calculated_base_rates",
        limit_choices_to={'code': 'EUR'},
        default=None,
        help_text=_("Base currency (always EUR)")
    )
    target_currency = models.ForeignKey(
        "Currency",  # ← string reference here too
        on_delete=models.CASCADE,
        related_name="calculated_target_rates",
        help_text=_("Target currency for the calculated rate")
    )
    rate = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text=_("Real-time exchange rate")
    )
    calculation_rate_stored = models.DecimalField(
        max_digits=20,
        decimal_places=6,
        help_text=_("Calculation exchange rate")
    )
    date = models.DateTimeField(
        auto_now=True,
        help_text=_("Timestamp when this rate was stored")
    )

    class Meta:
        verbose_name = _("Calculated Exchange Rate")
        verbose_name_plural = _("Calculated Exchange Rates")
        unique_together = ("base_currency", "target_currency")
        ordering = ["-date"]

    def __str__(self):
        return f"1 {self.base_currency.code} = {self.rate} {self.target_currency.code} (calc: {self.calculation_rate_stored})"

class Currency(models.Model):
    """
    Model to store available currencies supported by the Frankfurter API.
    """
    code = models.CharField(
        max_length=3,
        unique=True,
        help_text=_("ISO 4217 currency code, e.g., USD, EUR, GBP"),
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Currency full name, e.g., United States Dollar"),
    )

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ExchangeRate(models.Model):
    """
    Model to store exchange rates between currencies.
    Rates are always stored with a reference date.
    """
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="base_rates",
        help_text=_("Base currency (1 unit of this currency)"),
    )
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="target_rates",
        help_text=_("Target currency (converted value)"),
    )
    rate = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text=_("Exchange rate from base to target currency"),
    )
    date = models.DateField(
        help_text=_("Date when the exchange rate was recorded"),
    )

    class Meta:
        verbose_name = _("Exchange Rate")
        verbose_name_plural = _("Exchange Rates")
        unique_together = ("base_currency", "target_currency", "date")
        ordering = ["-date", "base_currency__code", "target_currency__code"]

    def __str__(self):
        return f"1 {self.base_currency.code} = {self.rate} {self.target_currency.code} on {self.date}"

class HistoricalExchangeRate(models.Model):
    """
    Model to store historical exchange rates between currencies.
    Useful for timeseries analysis.
    """
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="historical_base_rates",
        help_text=_("Base currency (1 unit of this currency)"),
    )
    target_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="historical_target_rates",
        help_text=_("Target currency (converted value)"),
    )
    rate = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text=_("Exchange rate from base to target currency"),
    )
    date = models.DateField(
        help_text=_("Date for the historical exchange rate"),
    )

    class Meta:
        verbose_name = _("Historical Exchange Rate")
        verbose_name_plural = _("Historical Exchange Rates")
        unique_together = ("base_currency", "target_currency", "date")
        ordering = ["-date", "base_currency__code", "target_currency__code"]

    def __str__(self):
        return f"[HIST] 1 {self.base_currency.code} = {self.rate} {self.target_currency.code} on {self.date}"
