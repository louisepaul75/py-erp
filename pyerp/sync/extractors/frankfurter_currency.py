import requests
from .base import BaseExtractor

class FrankfurterCurrencyExtractor(BaseExtractor):
    def connect(self):
        # No persistent connection needed for a simple API call
        pass

    @classmethod
    def get_required_config_fields(cls):
        # Define fields expected in the config (if any)
        return []
    
    def extract(self, query_params=None, fail_on_filter_error=True):
        response = requests.get("https://api.frankfurter.dev/v1/currencies")
        response.raise_for_status()
        data = response.json()
        result = [{"code": code, "name": name} for code, name in data.items()]
        return result