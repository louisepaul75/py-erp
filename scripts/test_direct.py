#!/usr/bin/env python
import os
import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pyerp.utils.env_loader import load_environment_variables

# Add project root to path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the centralized environment loader

# Load environment variables
load_environment_variables(verbose=True)

# Get credentials from environment variables
api_url = os.environ.get("IMAGE_API_URL", "https://webapp.zinnfiguren.de/api/")
api_username = os.environ.get("IMAGE_API_USERNAME")
api_password = os.environ.get("IMAGE_API_PASSWORD")

print(f"\nAPI Configuration:")  # noqa: F541
print(f"URL: {api_url}")
print(f"Username: {api_username}")
print(f"Password: {'*' * len(api_password) if api_password else 'Not set'}")

# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=0.5,  # wait 0.5s * (2 ** (retry - 1)) between retries
    status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
)

# Create a session with the retry strategy
session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Make API request
print("\nFetching first page of all images...")
try:
    response = session.get(
        f"{api_url.rstrip('/')}/all-files-and-articles/",
        params={"page": 1, "page_size": 5},
        auth=(api_username, api_password),
        timeout=60,  # Increased timeout to 60 seconds
    )

    print(f"\nAPI Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Successfully retrieved data")  # noqa: F541
        print(f"Response data: {data}")
    else:
        print(f"Error response: {response.text}")
except requests.exceptions.Timeout:
    print(
        "Request timed out after 60 seconds. The server might be slow or unresponsive.",
    )
except requests.exceptions.ConnectionError:
    print(
        "Failed to connect to the server. Please check your internet connection and the API URL.",
    )
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e!s}")
finally:
    session.close()
