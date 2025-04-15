# pyerp/sync/extractors/frankfurter_exchange.py

import requests
from datetime import datetime
from .base import BaseExtractor

class FrankfurterExchangeRateExtractor(BaseExtractor):
    def connect(self):
        # No persistent connection needed for a simple API call
        pass

    @classmethod
    def get_required_config_fields(cls):
        # Define fields expected in the config (if any)
        return []
    
    def extract(self, query_params=None, fail_on_filter_error=True):
        base_currency = query_params.get("base", "EUR")
        today = datetime.today().strftime('%Y-%m-%d')
        response = requests.get(f"https://api.frankfurter.dev/v1/latest?", params={"base": base_currency})
        response.raise_for_status()
        data = response.json()
        base = data["base"]
        date = data["date"]
        result = [{
            "base": base,
            "target": k,
            "rate": v,
            "date": date
        } for k, v in data["rates"].items()]
        return result
