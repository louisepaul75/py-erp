# pyerp/sync/extractors/frankfurter_exchange.py

import requests
from datetime import datetime
from .base import BaseExtractor

class FrankfurterHistoricalRateExtractor(BaseExtractor):
    def connect(self):
        # No persistent connection needed for a simple API call
        pass

    @classmethod
    def get_required_config_fields(cls):
        # Define fields expected in the config (if any)
        return []
    
    def extract(self, query_params=None, fail_on_filter_error=True):
        base_currency = query_params.get("base", "EUR")
        start_date= "2025-04-01"
        end_date = datetime.today().strftime('%Y-%m-%d')
        response = requests.get(f"https://api.frankfurter.dev/v1/{start_date}..{end_date}")
        response.raise_for_status()
        data = response.json()

        base = data["base"]
        result = []

        # Handle time series or single-date response
        if "rates" in data and isinstance(data["rates"], dict):
            for date, daily_rates in data["rates"].items():
                for target, rate in daily_rates.items():
                    result.append({
                        "base": base,
                        "target": target,
                        "rate": rate,
                        "date": date,
                    })
        return result
