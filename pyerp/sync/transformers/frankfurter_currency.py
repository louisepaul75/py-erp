from .base import BaseTransformer

class FrankfurterCurrencyTransformer(BaseTransformer):
    def transform(self, record: dict) -> list[dict]:
        # In case extractor sends records like {"USD": "US Dollar"},
        # first confirm what "record" looks like.

        if "code" in record and "name" in record:
            return record  # Already in correct shape

        # 2️⃣ If your extractor returns {"USD": "US Dollar"} (one key-value pair), fix like this:
        if len(record) == 1:
            code, name = list(record.items())[0]
            return {"code": code, "name": name}

        return []
