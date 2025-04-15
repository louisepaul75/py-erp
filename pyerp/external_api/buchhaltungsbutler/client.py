# pyerp/buchhaltungsbutler/client.py

import requests
import logging
import json  # Added for handling order parameter
from requests.auth import HTTPBasicAuth

from django.conf import settings

from pyerp.external_api.buchhaltungsbutler.exceptions import (
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
            msg = (
                "BuchhaltungsButler API credentials (API_CLIENT, API_SECRET, "
                "CUSTOMER_API_KEY) are not fully configured in settings."
            )
            logger.error(msg)
            # Optionally raise an error or handle incomplete config
            raise BuchhaltungsButlerError(msg)

        self.auth = HTTPBasicAuth(self.api_client, self.api_secret)

    def _request(
        self, method, endpoint, params=None, data=None, json_payload=None
    ):
        """Makes a request to the BuchhaltungsButler API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Prepare data payload for POST/PUT etc.
        request_data = data.copy() if data else {}
        if method.upper() in ["POST", "PUT", "PATCH"]:
            # Add api_key to data payload for POST/PUT/PATCH
            request_data['api_key'] = self.customer_api_key
        elif params:
            # Add api_key to query params for GET/DELETE if not already present
            if 'api_key' not in params:
                params['api_key'] = self.customer_api_key
        else:
            # Add api_key to query params for GET/DELETE if no other params
            params = {'api_key': self.customer_api_key}

        headers = {
            'Accept': 'application/json',
            'User-Agent': f'pyERP/{settings.APP_VERSION}'
        }
        # Content-Type might be needed for POST with form data
        # if method.upper() == 'POST' and request_data:
        #     headers['Content-Type'] = 'application/x-www-form-urlencoded'

        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=headers,
                params=params,         # For GET/DELETE query parameters
                data=request_data,     # For POST/PUT form data
                json=json_payload,       # For sending JSON payload
                timeout=30             # Standard timeout
            )

            # Check for common error status codes
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check API Client/Secret."
                )
            if response.status_code == 403:
                # Could be auth error or invalid customer api_key
                raise AuthenticationError(
                    f"Forbidden (403). Check credentials/customer API key. "
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
            status = e.response.status_code
            text = e.response.text
            logger.error(
                "HTTP error during BuchhaltungsButler API request "
                "to %s: %s - %s",
                url, status, text,
                exc_info=True
            )
            raise APIRequestError(status, text) from e
        except requests.exceptions.RequestException as e:
            # Catch other requests errors (timeout, connection error, etc.)
            logger.error(
                "Error during BuchhaltungsButler API request to %s: %s",
                url, e, exc_info=True
            )
            raise BuchhaltungsButlerError(f"Request failed: {e}") from e
        except Exception as e:
            # Catch unexpected errors
            msg = f"An unexpected error occurred: {e}"
            logger.error(
                "Unexpected error during BuchhaltungsButler API request: %s",
                msg, exc_info=True
            )
            raise BuchhaltungsButlerError(msg) from e

    # --- Public Methods ---

    def get(self, endpoint, params=None):
        """Perform a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, json_payload=None):
        """Perform a POST request."""
        return self._request(
            "POST", endpoint, data=data, json_payload=json_payload
        )

    def list_receipts(
        self,
        list_direction,
        payment_status=None,
        counterparty=None,
        date_from=None,
        date_to=None,
        limit=None,
        offset=None,
        order=None,  # Expects a dict like {"field": "date", "sort": "ASC"}
        include_offers=None,
        deleted=None,
        invoicenumber=None,
        due_date=None
    ):
        """Gets receipts based on specified criteria.

        Args:
            list_direction (str): Required. 'inbound' or 'outbound'.
            payment_status (str, optional): 'paid' or 'unpaid'.
            counterparty (str, optional): Filter by counterparty name.
            date_from (str, optional): Start date filter (YYYY-MM-DD).
            date_to (str, optional): End date filter (YYYY-MM-DD).
            limit (int, optional): Max number of results (default 500).
            offset (int, optional): Pagination offset (default 0).
            order (dict, optional): Sorting criteria, e.g., {'field': 'date',
                                    'sort': 'ASC'}. The dict will be JSON
                                    encoded.
            include_offers (bool, optional): Include offers (default False).
            deleted (bool, optional): Include deleted receipts (default False).
            invoicenumber (str, optional): Filter by invoice number.
            due_date (str, optional): Filter by due date (YYYY-MM-DD).

        Returns:
            dict: The API response containing the list of receipts.

        Raises:
            ValueError: If list_direction is invalid.
            BuchhaltungsButlerError: For API or request errors.
        """
        endpoint = "/receipts/get"
        valid_directions = ["inbound", "outbound"]
        if list_direction not in valid_directions:
            raise ValueError(
                f"Invalid list_direction: '{list_direction}'. "
                f"Must be one of {valid_directions}"
            )

        payload = {
            "list_direction": list_direction,
        }

        # Add optional parameters if provided
        if payment_status is not None:
            payload["payment_status"] = payment_status
        if counterparty is not None:
            payload["counterparty"] = counterparty
        if date_from is not None:
            payload["date_from"] = date_from
        if date_to is not None:
            payload["date_to"] = date_to
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset
        if order is not None:
            # API expects 'order' as a JSON string in the form data
            try:
                payload["order"] = json.dumps(order)
            except TypeError as e:
                raise ValueError(f"Invalid format for 'order' parameter: {e}")
        if include_offers is not None:
            payload["include_offers"] = include_offers
        if deleted is not None:
            payload["deleted"] = deleted
        if invoicenumber is not None:
            payload["invoicenumber"] = invoicenumber
        if due_date is not None:
            payload["due_date"] = due_date

        logger.debug("Listing receipts with payload: %s", payload)
        return self._request("POST", endpoint, data=payload)

    # Add other methods like put, delete, patch as needed


# Example usage (for testing/demonstration - remove later)
if __name__ == '__main__':
    # This requires Django settings to be configured
    # You might run this via 'python -m 
    # pyerp.external_api.buchhaltungsbutler.client'
    # after setting up DJANGO_SETTINGS_MODULE environment variable.
    import os
    # Use the base settings file which handles .env loading and 1Password
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE', 'config.settings.base'
    )
    import django
    import sys  # Import sys for exit

    # Need to configure Django settings explicitly when running script directly
    try:
        django.setup()
    except RuntimeError as e:
        # Handle cases where settings might already be configured 
        # (e.g., if run via manage.py)
        if "Settings already configured" not in str(e):
            print(f"Error configuring Django: {e}")
            sys.exit(1)

    try:
        client = BuchhaltungsButlerClient()
        print("Client initialized successfully.")
        receipts = client.list_receipts(list_direction='inbound', limit=5)
        print(f"Found {receipts.get('rows')} receipts:")
        for receipt in receipts.get('data', []):
            print(f" - {receipt.get('filename')} ({receipt.get('date')})")
    except BuchhaltungsButlerError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
