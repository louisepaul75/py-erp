#!/usr/bin/env python
import os
import requests
from pathlib import Path
import dotenv

# Load environment variables from config/env/.env file
env_file = Path('.') / 'config' / 'env' / '.env'
if env_file.exists():
    print(f"Loading environment from {env_file}")
    # Load environment variables directly from the file
    with open(env_file) as f:
        env_vars = {}
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value

    # Get credentials from parsed environment variables
    api_url = env_vars.get('IMAGE_API_URL', 'http://webapp.zinnfiguren.de/api/')
    api_username = env_vars.get('IMAGE_API_USERNAME')
    api_password = env_vars.get('IMAGE_API_PASSWORD')
else:
    print(f"Warning: Environment file not found at {env_file}")
    api_url = 'http://webapp.zinnfiguren.de/api/'
    api_username = None
    api_password = None

print(f"\nAPI Configuration:")
print(f"URL: {api_url}")
print(f"Username: {api_username}")
print(f"Password: {'*' * len(api_password) if api_password else 'Not set'}")

# Make API request
print("\nFetching first page of all images...")
response = requests.get(
    f"{api_url.rstrip('/')}/all-files-and-articles/",
    params={'page': 1, 'page_size': 5},
    auth=(api_username, api_password),
    timeout=30
)

print(f"\nAPI Response Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Successfully retrieved data")
    print(f"Response data: {data}")
else:
    print(f"Error response: {response.text}") 