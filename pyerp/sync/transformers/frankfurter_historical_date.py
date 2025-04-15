# pyerp/sync/transformers/frankfurter_exchange.py

from .base import BaseTransformer
from pyerp.business_modules.currency.models import Currency
from decimal import Decimal, ROUND_HALF_UP

class FrankfurterHistoricalRateTransformer(BaseTransformer): 
    def transform(self, record):
        result = {
            "base_currency": Currency.objects.get(code=record["base"]),
            "target_currency": Currency.objects.get(code=record["target"]),
            "rate": Decimal(record["rate"]).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP),
            "date": record["date"]
        }
        return result
