from collections import namedtuple
from datetime import datetime
import json

# Mock the _clean_for_json method
def _clean_for_json(data):
    """Clean data to ensure it can be JSON serialized."""
    if isinstance(data, dict):
        return {k: _clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_clean_for_json(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, (int, float, str, bool, type(None))):
        return data
    elif hasattr(data, '_asdict') and callable(data._asdict):
        # Handle NamedTuple objects like LoadResult
        return _clean_for_json(data._asdict())
    else:
        return str(data)

# Create a NamedTuple similar to LoadResult
LoadResult = namedtuple('LoadResult', ['created', 'updated', 'skipped', 'errors', 'error_details'])

# Create a test instance
result = LoadResult(
    created=5,
    updated=3,
    skipped=2,
    errors=1,
    error_details=[{'error': 'Test error'}]
)

# Clean the NamedTuple for JSON
cleaned = _clean_for_json(result)

# Print the result
print("Original:", result)
print("Cleaned:", cleaned)
print("JSON:", json.dumps(cleaned, indent=2))

# Test with nested data
TestResult = namedtuple('TestResult', ['created', 'updated'])
test_data = {
    'string': 'test',
    'int': 42,
    'float': 3.14,
    'bool': True,
    'none': None,
    'list': [1, 'two', 3.0],
    'dict': {'key': 'value'},
    'datetime': datetime(2025, 3, 9, 12, 0, 0),
    'namedtuple': TestResult(created=5, updated=3)
}

# Clean the nested data for JSON
cleaned_nested = _clean_for_json(test_data)

# Print the result
print("\nNested data:")
print("JSON:", json.dumps(cleaned_nested, indent=2)) 