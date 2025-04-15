# pyerp/buchhaltungsbutler/client.py

import requests
import logging
from requests.auth import HTTPBasicAuth

from django.conf import settings

from .exceptions import (
    BuchhaltungsButlerError,
    AuthenticationError,
    APIRequestError,
    RateLimitError
)

logger = logging.getLogger(__name__)

# TODO: Confirm the correct base URL
DEFAULT_BASE_URL = "https://app.buchhaltungsbutler.de/api/v1/"
# TODO: Implement more robust rate limiting if needed
# API allows 100 requests per customer per minute.

class BuchhaltungsButlerClient:
    """Client for interacting with the BuchhaltungsButler API."""

    def __init__(self, base_url=None):
        creds = settings.BUCHHALTUNGSBUTLER_API
        self.api_client = creds.get("API_CLIENT")
        self.api_secret = creds.get("API_SECRET")
        self.customer_api_key = creds.get("CUSTOMER_API_KEY")
        self.base_url = base_url or DEFAULT_BASE_URL

        if not all([self.api_client, self.api_secret, self.customer_api_key]):
            logger.error(
                "BuchhaltungsButler API credentials (API_CLIENT, API_SECRET, "
                "CUSTOMER_API_KEY) are not fully configured in settings."
            )
            # Optionally raise an error or handle incomplete config
            raise BuchhaltungsButlerError("API credentials not fully configured.")

        self.auth = HTTPBasicAuth(self.api_client, self.api_secret)

    def _request(self, method, endpoint, params=None, data=None, json=None):
        """Makes a request to the BuchhaltungsButler API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Add the customer-specific API key to the request data/params
        # Documentation mentions 'form field', implying 'data'
        request_data = data.copy() if data else {}
        request_data['api_key'] = self.customer_api_key

        headers = {
            'Accept': 'application/json',
            'User-Agent': f'pyERP/{settings.APP_VERSION}'
        }

        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=headers,
                params=params, # Use params for GET request query parameters
                data=request_data, # Use data for POST/PUT form data
                json=json, # Use json for sending JSON payload if needed
                timeout=30 # Standard timeout
            )

            # Check for common error status codes
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Check API Client/Secret.")
            if response.status_code == 403:
                # Could be auth error or invalid customer api_key
                 raise AuthenticationError(
                     f"Forbidden (403). Check credentials and customer API key. "
                     f"Response: {response.text[:200]}"
                 )
            if response.status_code == 429:
                # TODO: Implement proper backoff/retry logic
                logger.warning("Rate limit likely exceeded (429).")
                raise RateLimitError("API rate limit exceeded.")

            # Raise exception for other non-2xx status codes
            response.raise_for_status()

            # Handle potential empty response body for success codes like 204
            if response.status_code == 204:
                return None
            return response.json()

        except requests.exceptions.HTTPError as e:
            # Raised by response.raise_for_status() for 4xx/5xx
            logger.error(
                "HTTP error during BuchhaltungsButler API request to %s: %s - %s",
                url, e.response.status_code, e.response.text,
                exc_info=True
            )
            raise APIRequestError(e.response.status_code, e.response.text) from e
        except requests.exceptions.RequestException as e:
            # Catch other requests errors (timeout, connection error, etc.)
            logger.error(
                "Error during BuchhaltungsButler API request to %s: %s",
                url, e, exc_info=True
            )
            raise BuchhaltungsButlerError(f"Request failed: {e}") from e
        except Exception as e:
            # Catch unexpected errors
            logger.error(
                "Unexpected error during BuchhaltungsButler API request: %s",
                e, exc_info=True
            )
            raise BuchhaltungsButlerError(f"An unexpected error occurred: {e}") from e

    # --- Public Methods (Examples) ---

    def get(self, endpoint, params=None):
        """Perform a GET request."""
        # Note: api_key should likely be in params for GET, not data.
        # Adjusting _request or this method might be needed based on API behavior.
        # For now, assuming _request handles adding api_key correctly, even to params if needed.
        # If GET requires api_key in query string, update _request.
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, json=None):
        """Perform a POST request."""
        return self._request("POST", endpoint, data=data, json=json)

    # Add other methods like put, delete, patch as needed

# Example usage (for testing/demonstration - remove later)
# if __name__ == '__main__':
#     # This requires Django settings to be configured
#     # You might run this via 'python -m pyerp.buchhaltungsbutler.client'
#     # after setting up DJANGO_SETTINGS_MODULE environment variable.
#     try:
#         client = BuchhaltungsButlerClient()
#         # Replace with a real endpoint once known
#         # data = client.get('some_endpoint')
#         # print(data)
#         print("Client initialized successfully.")
#     except Exception as e:
#         print(f"Error: {e}") 