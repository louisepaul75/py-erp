"""JSON utilities for handling serialization and deserialization."""

import json
from datetime import date, datetime

import pandas as pd
from django.utils import timezone


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime, date objects and pandas objects."""
    
    def default(self, obj):
        """Convert datetime/date objects to ISO format strings."""
        if isinstance(obj, (datetime, timezone.datetime)):
            return obj.isoformat() if obj else None
        elif isinstance(obj, date):
            return obj.isoformat() if obj else None
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat() if pd.notna(obj) else None
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (float)) and pd.isna(obj):
            return None
        return super().default(obj)


def json_serialize(obj):
    """Serialize an object to a JSON-safe dict/list structure.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-safe representation of the object
    """
    try:
        # First try to use the custom encoder
        json_string = json.dumps(obj, cls=DateTimeEncoder)
        return json.loads(json_string)
    except (TypeError, ValueError):
        # If that fails, try a more robust approach with manual conversion
        if isinstance(obj, dict):
            return {k: json_serialize(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [json_serialize(v) for v in obj]
        elif isinstance(obj, (datetime, timezone.datetime, date)):
            return obj.isoformat() if obj else None
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat() if pd.notna(obj) else None
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (int, float, str, bool, type(None))):
            # Handle NaN values in floats
            if isinstance(obj, float) and pd.isna(obj):
                return None
            return obj
        else:
            # For any other types, convert to string
            return str(obj) 