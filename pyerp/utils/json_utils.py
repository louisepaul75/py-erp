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
    """Serialize an object to a JSON-safe dict/list structure by recursively converting types.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON-safe Python object representation (dict, list, primitives)
    """
    if isinstance(obj, dict):
        return {k: json_serialize(v) for k, v in obj.items()}
    # Handle namedtuples BEFORE lists/tuples
    elif isinstance(obj, tuple) and hasattr(obj, '_asdict'):
        return json_serialize(obj._asdict()) # Convert to dict and recurse
    elif isinstance(obj, (list, tuple)):
        return [json_serialize(v) for v in obj]
    elif isinstance(obj, (datetime, timezone.datetime, date)):
        return obj.isoformat() if obj else None
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat() if pd.notna(obj) else None
    elif isinstance(obj, float) and pd.isna(obj):
        return None # Represent NaN as None
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj # Primitive types are already JSON-safe
    elif pd.isna(obj): # Catch other pandas NA types
        return None
    else:
        # For any other complex types not explicitly handled, convert to string
        # This prevents TypeErrors during final JSON dumping if needed later
        return str(obj)

# Example of how this might be used later if a JSON string is needed:
# safe_object = json_serialize(my_complex_object)
# json_string = json.dumps(safe_object) # Standard json.dumps should now work