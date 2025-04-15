# pyerp/buchhaltungsbutler/client.py

import requests
import logging
import json  # Keep for potential use, though direct JSON payload preferred now
from requests.auth import HTTPBasicAuth

from django.conf import settings

from pyerp.external_api.buchhaltungsbutler.exceptions import (
    BuchhaltungsButlerError,
    AuthenticationError,
    APIRequestError,
    RateLimitError
)

logger = logging.getLogger(__name__)

# Correct base URL based on the working example
DEFAULT_BASE_URL = "https://webapp.buchhaltungsbutler.de/api/v1/"
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
            raise BuchhaltungsButlerError(msg)

        self.auth = HTTPBasicAuth(self.api_client, self.api_secret)

    def _request(
        self, method, endpoint, params=None, data=None, json_payload=None
    ):
        """Makes a request to the BuchhaltungsButler API."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Add api_key to payload or params consistently
        # The example shows api_key needed *in addition* to Basic Auth
        payload_to_send = json_payload.copy() if json_payload else {}
        form_data_to_send = data.copy() if data else {} # Keep for potential non-JSON POSTs

        if method.upper() in ["POST", "PUT", "PATCH"]:
            if payload_to_send:
                payload_to_send['api_key'] = self.customer_api_key
            elif form_data_to_send:
                 form_data_to_send['api_key'] = self.customer_api_key
            else:
                # If sending empty POST/PUT/PATCH, add api_key to json_payload
                payload_to_send = {'api_key': self.customer_api_key}

        elif params:
            if 'api_key' not in params:
                params['api_key'] = self.customer_api_key
        else:
             params = {'api_key': self.customer_api_key}


        headers = {
            'Accept': 'application/json',
            'User-Agent': f'pyERP/{settings.APP_VERSION}'
        }
        # Set Content-Type if sending JSON
        if payload_to_send:
            headers['Content-Type'] = 'application/json'
        # requests might set Content-Type for form data automatically if needed


        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=headers,
                params=params,            # For GET/DELETE query parameters
                data=form_data_to_send,   # For POST/PUT form data (use sparingly)
                json=payload_to_send,     # For sending JSON payload (preferred for POST/PUT)
                timeout=30                # Standard timeout
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

            # Handle potential empty response for success with no content
            if not response.content:
                 return None # Or return {} if an empty dict is preferred

            return response.json()

        except requests.exceptions.HTTPError as e:
            # Raised by response.raise_for_status() for 4xx/5xx
            status = e.response.status_code
            # Try to get JSON error details first
            try:
                error_details = e.response.json()
                text = json.dumps(error_details) # Format JSON for logging
            except json.JSONDecodeError:
                text = e.response.text # Fallback to raw text

            logger.error(
                "HTTP error during BuchhaltungsButler API request "
                "to %s: %s - %s",
                url, status, text,
                exc_info=True # Add traceback only for HTTP errors
            )
            raise APIRequestError(status, text) from e
        except requests.exceptions.RequestException as e:
            # Catch other requests errors (timeout, connection error, etc.)
            logger.error(
                "Error during BuchhaltungsButler API request to %s: %s",
                url, e, exc_info=True # Add traceback for request exceptions
            )
            raise BuchhaltungsButlerError(f"Request failed: {e}") from e
        except Exception as e:
            # Catch unexpected errors
            msg = f"An unexpected error occurred: {e}"
            logger.error(
                "Unexpected error during BuchhaltungsButler API request: %s",
                msg, exc_info=True # Add traceback for general exceptions
            )
            raise BuchhaltungsButlerError(msg) from e

    # --- Public Methods ---\

    def get(self, endpoint, params=None):
        """Perform a GET request."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, json_payload=None):
        """Perform a POST request. Prefers sending json_payload if provided."""
        if json_payload is not None:
             return self._request("POST", endpoint, json_payload=json_payload)
        elif data is not None:
             # Fallback for form data if explicitly needed, though JSON is preferred
             logger.warning("Sending POST request with form data to %s. "
                            "Consider using json_payload.", endpoint)
             return self._request("POST", endpoint, data=data)
        else:
             # POST request with no body (just api_key added in _request)
             return self._request("POST", endpoint)


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
        """Gets receipts based on specified criteria using POST with JSON body.

        Args:
            list_direction (str): Required. 'inbound' or 'outbound'.
            payment_status (str, optional): 'paid' or 'unpaid'.
            counterparty (str, optional): Filter by counterparty name.
            date_from (str, optional): Start date filter (YYYY-MM-DD).
            date_to (str, optional): End date filter (YYYY-MM-DD).
            limit (int, optional): Max number of results (default 500 in API).
            offset (int, optional): Pagination offset (default 0).
            order (dict, optional): Sorting criteria, e.g., {'field': 'date',
                                    'sort': 'ASC'}.
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
            # Pass the dict directly, it will be JSON encoded
            if not isinstance(order, dict):
                 raise ValueError("Invalid format for 'order' parameter, must be a dict")
            payload["order"] = order
        if include_offers is not None:
            payload["include_offers"] = include_offers
        if deleted is not None:
            payload["deleted"] = deleted
        if invoicenumber is not None:
            payload["invoicenumber"] = invoicenumber
        if due_date is not None:
            payload["due_date"] = due_date

        logger.debug("Listing receipts with payload: %s", payload)
        # Use post method which now defaults to sending JSON payload
        return self.post(endpoint, json_payload=payload)

    def list_postings(
        self,
        date_from,
        date_to,
        limit=None,
        offset=None,
        # Add other relevant filters based on API docs if needed
    ):
        """Gets postings within a date range using POST with JSON body.

        Args:
            date_from (str): Required. Start date filter (YYYY-MM-DD).
            date_to (str): Required. End date filter (YYYY-MM-DD).
            limit (int, optional): Max number of results.
            offset (int, optional): Pagination offset.

        Returns:
            dict: The API response containing the list of postings.

        Raises:
            BuchhaltungsButlerError: For API or request errors.
        """
        endpoint = "/postings/get"
        payload = {
            "date_from": date_from,
            "date_to": date_to,
        }
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset

        logger.debug("Listing postings with payload: %s", payload)
        return self.post(endpoint, json_payload=payload)

    def get_posting_accounts(self, limit=None, offset=None):
        """Gets posting accounts (chart of accounts) using POST with JSON body.

        Args:
            limit (int, optional): Max number of results.
            offset (int, optional): Pagination offset.

        Returns:
            dict: The API response containing the list of posting accounts.

        Raises:
            BuchhaltungsButlerError: For API or request errors.
        """
        endpoint = "/settings/get/postingaccounts"
        payload = {}
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset

        logger.debug("Getting posting accounts with payload: %s", payload)
        # Even if payload is empty, post() handles adding api_key correctly
        return self.post(endpoint, json_payload=payload)

    def get_all_posting_accounts(self, limit=500):
        """Gets ALL posting accounts by handling pagination automatically.

        Args:
            limit (int, optional): The number of items to fetch per page.
                                 Defaults to 500.

        Returns:
            list: A list containing all posting account dictionaries.

        Raises:
            BuchhaltungsButlerError: For API or request errors during fetching.
        """
        import time # Import time for sleep

        all_accounts = []
        offset = 0
        logger.info("Starting fetch for all posting accounts with limit=%d...", limit)

        while True:
            try:
                logger.debug("Fetching posting accounts page: offset=%d, limit=%d",
                             offset, limit)
                response = self.get_posting_accounts(limit=limit, offset=offset)

                # Check response structure
                if not isinstance(response, dict) or 'data' not in response:
                    logger.error(
                        "Unexpected response format received: %s", response
                    )
                    # Optionally raise an error or return partial results
                    raise BuchhaltungsButlerError(
                        "Unexpected response format from get_posting_accounts"
                    )

                current_page_accounts = response.get('data', [])

                if not current_page_accounts:
                    logger.info("No more accounts found. Fetch complete.")
                    break # No more accounts on this page

                logger.info("Fetched %d accounts from offset %d.",
                            len(current_page_accounts), offset)
                all_accounts.extend(current_page_accounts)

                # Check if this was the last page
                if len(current_page_accounts) < limit:
                    logger.info("Last page reached (fetched < limit).")
                    break

                # Prepare for the next page
                offset += limit
                time.sleep(0.5) # Small delay to be kind to the API

            except BuchhaltungsButlerError as e:
                logger.error(
                    "API error fetching posting accounts at offset %d: %s",
                    offset, e, exc_info=True
                )
                raise # Re-raise the exception to signal failure
            except Exception as e:
                logger.error(
                    "Unexpected error fetching posting accounts at offset %d: %s",
                    offset, e, exc_info=True
                )
                raise BuchhaltungsButlerError(
                    f"Unexpected error during pagination: {e}"
                ) from e

        logger.info("Successfully fetched a total of %d posting accounts.",
                    len(all_accounts))
        return all_accounts

    def get_creditors(self, limit=None, offset=None):
        """Gets creditors using POST with JSON body.

        Args:
            limit (int, optional): Max number of results.
            offset (int, optional): Pagination offset.

        Returns:
            dict: The API response containing the list of creditors.

        Raises:
            BuchhaltungsButlerError: For API or request errors.
        """
        endpoint = "/settings/get/creditors"
        payload = {}
        if limit is not None:
            payload["limit"] = limit
        if offset is not None:
            payload["offset"] = offset

        logger.debug("Getting creditors with payload: %s", payload)
        return self.post(endpoint, json_payload=payload)

    def get_all_creditors(self, limit=500):
        """Gets ALL creditors by handling pagination automatically.

        Args:
            limit (int, optional): The number of items to fetch per page.
                                 Defaults to 500.

        Returns:
            list: A list containing all creditor dictionaries.

        Raises:
            BuchhaltungsButlerError: For API or request errors during fetching.
        """
        import time

        all_creditors = []
        offset = 0
        logger.info("Starting fetch for all creditors with limit=%d...", limit)

        while True:
            try:
                logger.debug("Fetching creditors page: offset=%d, limit=%d",
                             offset, limit)
                response = self.get_creditors(limit=limit, offset=offset)

                if not isinstance(response, dict) or 'data' not in response:
                    logger.error(
                        "Unexpected response format received for creditors: %s", response
                    )
                    raise BuchhaltungsButlerError(
                        "Unexpected response format from get_creditors"
                    )

                current_page_creditors = response.get('data', [])

                if not current_page_creditors:
                    logger.info("No more creditors found. Fetch complete.")
                    break

                logger.info("Fetched %d creditors from offset %d.",
                            len(current_page_creditors), offset)
                all_creditors.extend(current_page_creditors)

                if len(current_page_creditors) < limit:
                    logger.info("Last page reached (fetched < limit).")
                    break

                offset += limit
                time.sleep(0.5) # Be kind to the API

            except BuchhaltungsButlerError as e:
                logger.error(
                    "API error fetching creditors at offset %d: %s",
                    offset, e, exc_info=True
                )
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error fetching creditors at offset %d: %s",
                    offset, e, exc_info=True
                )
                raise BuchhaltungsButlerError(
                    f"Unexpected error during creditor pagination: {e}"
                ) from e

        logger.info("Successfully fetched a total of %d creditors.",
                    len(all_creditors))
        return all_creditors

    # Add other methods like put, delete, patch as needed


# Example usage (for testing/demonstration - requires Django setup)
if __name__ == '__main__':
    # This requires Django settings to be configured
    # You might run this via 'python -m
    # pyerp.external_api.buchhaltungsbutler.client'
    # after setting up DJANGO_SETTINGS_MODULE environment variable.
    import os
    # Use the base settings file which handles .env loading and 1Password
    # Force the setting instead of using setdefault to override external env vars
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pyerp.config.settings.base'
    print(f"DJANGO_SETTINGS_MODULE forced to: {os.environ['DJANGO_SETTINGS_MODULE']}")
    import django
    import sys  # Import sys for exit
    import pprint # Import pprint for better dict printing
    import pandas as pd # Import pandas

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

        # print("\\n--- Testing list_receipts ---")
        # receipts_response = client.list_receipts(list_direction='inbound', limit=5)
        # # Adjust based on actual API response structure - check logs if needed
        # # Assuming response might be {'data': [...], 'rows': X} or just [...]
        # if isinstance(receipts_response, dict):
        #     receipts_list = receipts_response.get('data', [])
        #     total_rows = receipts_response.get('rows', 'N/A')
        #     print(f"Found {total_rows} total receipts (showing {len(receipts_list)}):")
        # elif isinstance(receipts_response, list):
        #      receipts_list = receipts_response
        #      print(f"Found {len(receipts_list)} receipts:")
        # else:
        #      receipts_list = []
        #      print("Unexpected response format for receipts:", receipts_response)
        #
        # for receipt in receipts_list:
        #     print(f" - {receipt.get('filename')} ({receipt.get('date')})")

        # print("\\n--- Testing list_postings ---")
        # # Use appropriate dates
        # postings_response = client.list_postings(date_from="2024-01-01", date_to="2024-12-31", limit=5)
        # if isinstance(postings_response, dict):
        #     postings_list = postings_response.get('data', [])
        #     total_rows = postings_response.get('rows', 'N/A')
        #     print(f"Found {total_rows} total postings (showing {len(postings_list)}):")
        # elif isinstance(postings_response, list):
        #      postings_list = postings_response
        #      print(f"Found {len(postings_list)} postings:")
        # else:
        #      postings_list = []
        #      print("Unexpected response format for postings:", postings_response)
        #
        # for posting in postings_list:
        #     # Print relevant posting info, e.g., description, amount
        #     print(f" - Posting ID: {posting.get('uuid', 'N/A')}, Amount: {posting.get('action_amount', 'N/A')}") # Adjust fields as needed


        print("\\n--- Testing get_all_posting_accounts (with pagination) ---")
        # Use the new method that handles pagination
        all_accounts_list = client.get_all_posting_accounts()

        print(f"\\nSuccessfully fetched {len(all_accounts_list)} total accounts.")

        # Create and print DataFrame
        if all_accounts_list:
            print("\\nAccounts as Pandas DataFrame:")
            df = pd.DataFrame(all_accounts_list)
            # Optionally set display options for better console output
            pd.set_option('display.max_rows', None) # Show all rows
            pd.set_option('display.max_columns', None) # Show all columns
            pd.set_option('display.width', 1000) # Adjust width
            print(df.tail(20)) # Print only the last 20 rows
        else:
            print("\\nCannot create DataFrame: No accounts were retrieved.")

        # --- Previous single-page test (commented out) ---
        # print("\\n--- Testing get_posting_accounts ---")
        # # Use default limit by not specifying it
        # accounts_response = client.get_posting_accounts()
        #
        # # Print the raw response for inspection
        # print("\\nRaw accounts_response:")
        # pprint.pprint(accounts_response)
        #
        # if isinstance(accounts_response, dict):
        #     # Check common keys seen in example or typical API responses
        #     accounts_list = accounts_response.get('data', accounts_response.get('postingaccounts', []))
        #     total_rows = accounts_response.get('rows', 'N/A')
        #     print(f"\\nFound {total_rows} total accounts (showing {len(accounts_list)}):")
        #     if accounts_list:
        #          print("Example account structure:")
        #          pprint.pprint(accounts_list[0]) # Print first account structure
        # elif isinstance(accounts_response, list):
        #      accounts_list = accounts_response
        #      print(f"\\nFound {len(accounts_list)} accounts:")
        #      if accounts_list:
        #          print("Example account structure:")
        #          pprint.pprint(accounts_list[0]) # Print first account structure
        # else:
        #      accounts_list = []
        #      print("\\nUnexpected response format for accounts:", accounts_response)
        #
        # # Keep the loop but print using pprint for better readability if needed
        # # print("\\nAccount Details:")
        # # for account in accounts_list:
        # #     # print(f" - Account: {account.get('postingaccount', 'N/A')} - {account.get('description', 'N/A')}") # Adjust field names if needed
        # #     pprint.pprint(account)
        # #     print("---")

        print("\n--- Testing get_creditors (Sample Request) ---")
        try:
            # Use POST based on pattern for other /get endpoints
            creditors_response = client.post(
                "/settings/get/creditors", 
                json_payload={"limit": 5} # Fetch a small sample
            )
            print("Raw creditors_response:")
            pprint.pprint(creditors_response)
            
            # Try to extract and print the first creditor if available
            if isinstance(creditors_response, dict):
                creditors_list = creditors_response.get('data', [])
                if creditors_list:
                    print("\nExample Creditor Structure:")
                    pprint.pprint(creditors_list[0])
                else:
                    print("\nNo creditors found in the sample response.")
            elif isinstance(creditors_response, list) and creditors_response:
                 print("\nExample Creditor Structure:")
                 pprint.pprint(creditors_response[0])
            else:
                 print("\nUnexpected or empty response format for creditors:")
                 pprint.pprint(creditors_response)
                 
        except BuchhaltungsButlerError as e:
            print(f"API Error fetching creditors: {e}")
            if isinstance(e, APIRequestError):
                 print(f"Status Code: {e.status_code}")
                 print(f"Response Text: {e.text}")


    except BuchhaltungsButlerError as e:
        print(f"API Error: {e}")
        # Log detailed error if available from APIRequestError
        if isinstance(e, APIRequestError):
             print(f"Status Code: {e.status_code}")
             print(f"Response Text: {e.text}")
    except Exception as e:
        print(f"General Error: {e}")
        import traceback
        traceback.print_exc() # Print traceback for unexpected errors
