#!/usr/bin/env python
"""
Script to test connection to the external image database API.
"""
import os
import sys
import json
import logging
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_api_connection():
    """Test connection to the image API."""
    try:
        # Get settings from environment variables
        api_url = os.environ.get('IMAGE_API_URL')
        username = os.environ.get('IMAGE_API_USERNAME')
        password = os.environ.get('IMAGE_API_PASSWORD')
        timeout = int(os.environ.get('IMAGE_API_TIMEOUT', '30'))

        # Check if required settings are available
        if not all([api_url, username, password]):
            logger.error("Missing required environment variables")
            logger.error(
                "Please set IMAGE_API_URL, IMAGE_API_USERNAME, and "
                "IMAGE_API_PASSWORD"
            )
            return False

        # Ensure API URL ends with a slash
        api_url = api_url.rstrip('/') + '/'

        # Create session with retry strategy
        session = requests.Session()
        session.auth = HTTPBasicAuth(username, password)

        # Make request to the API
        endpoint = "all-files-and-articles/"
        params = {
            "page": 1,
            "page_size": 1
        }

        response = session.get(
            f"{api_url}{endpoint}",
            params=params,
            timeout=timeout
        )

        if response.status_code != 200:
            logger.error(
                "Failed to connect to the API. Status: %d, Response: %s",
                response.status_code,
                response.text
            )
            return False

        data = response.json()
        if not isinstance(data, dict) or 'count' not in data:
            logger.error("Invalid response format from API")
            return False

        logger.info("Successfully connected to the image API")
        logger.info("Total records available: %d", data['count'])
        
        if data.get('results'):
            logger.info("\nSample data (first record):")
            print(json.dumps(data['results'][0], indent=2))

        return True

    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", str(e))
        return False
    except json.JSONDecodeError as e:
        logger.error("Failed to parse JSON response: %s", str(e))
        return False
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
