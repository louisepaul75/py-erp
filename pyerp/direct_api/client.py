"""
Main API client for interacting with the legacy 4D-based ERP system.

This module provides the DirectAPIClient class which handles all interactions
with the legacy API, including data retrieval and updates.
"""

import logging
import requests
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from pyerp.direct_api.exceptions import (
    DirectAPIError, AuthenticationError, ConnectionError, 
    ResponseError, DataError
)
from pyerp.direct_api.auth import get_session
from pyerp.direct_api.settings import (
    API_ENVIRONMENTS,
    API_REST_ENDPOINT,
    API_REQUEST_TIMEOUT,
    API_MAX_RETRIES,
    API_RETRY_BACKOFF_FACTOR,
    API_PAGINATION_ENABLED,
    API_PAGINATION_SIZE
)

# Configure logging
logger = logging.getLogger(__name__)


class DirectAPIClient:
    """
    Client for directly interacting with the legacy 4D-based ERP system.
    
    This class provides methods for fetching data from and pushing data to
    the legacy system, replacing the WSZ_api package with a direct implementation.
    """
    
    def __init__(self, environment: str = 'live', timeout: int = None):
        """
        Initialize the API client.
        
        Args:
            environment: The environment to use ('live', 'test', etc.)
            timeout: Request timeout in seconds (overrides the default)
        """
        self.environment = environment
        self.timeout = timeout or API_REQUEST_TIMEOUT
        
        # Load environment configuration
        try:
            self.config = API_ENVIRONMENTS[environment]
        except KeyError:
            raise ValueError(f"Unknown environment: {environment}. "
                           f"Available environments: {', '.join(API_ENVIRONMENTS.keys())}")
        
        # Check if we have required configuration
        if not self.config.get('base_url'):
            raise ValueError(f"Missing base_url in environment configuration for {environment}")
    
    def _get_base_url(self) -> str:
        """Get the base URL for API requests."""
        return self.config['base_url']
    
    def _get_session(self):
        """Get a session for the current environment."""
        return get_session(self.environment)
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build a URL for the specified endpoint.
        
        Args:
            endpoint: The API endpoint to access
            
        Returns:
            str: The complete URL for the API request
        """
        base_url = self._get_base_url()
        api_path = urljoin(base_url, API_REST_ENDPOINT)
        return urljoin(f"{api_path}/", endpoint)
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method ('GET', 'POST', etc.)
            endpoint: API endpoint to access
            params: URL parameters
            data: Request body data
            headers: HTTP headers
            
        Returns:
            requests.Response: The API response
            
        Raises:
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
        """
        url = self._build_url(endpoint)
        
        # Get the session cookie
        cookie = self._get_session().get_cookie()
        
        # Prepare headers
        request_headers = {
            'Cookie': cookie,
            'Accept': 'application/json'
        }
        if headers:
            request_headers.update(headers)
        
        # Prepare for retries
        retries = 0
        last_error = None
        
        while retries <= API_MAX_RETRIES:
            try:
                # Make the request
                logger.debug(f"{method} request to {url}")
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    timeout=self.timeout
                )
                
                # Check for successful response
                if 200 <= response.status_code < 300:
                    return response
                elif response.status_code == 401:
                    # Authentication error - refresh session and retry
                    logger.warning("Authentication failed, refreshing session")
                    self._get_session().refresh()
                    cookie = self._get_session().get_cookie()
                    request_headers['Cookie'] = cookie
                    retries += 1
                    continue
                else:
                    # Handle other error responses
                    error_msg = f"API request failed with status {response.status_code}"
                    logger.error(error_msg)
                    raise ResponseError(response.status_code, error_msg, response.text)
                    
            except requests.RequestException as e:
                # Handle connection errors
                last_error = e
                logger.warning(f"Connection error during API request: {e}")
                
                # Calculate backoff time for retry
                import time
                backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                retries += 1
                
                if retries <= API_MAX_RETRIES:
                    logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    logger.error(f"API request failed after {retries-1} retries")
                    raise ConnectionError(f"Unable to connect to the API after {retries-1} retries") from last_error
                    
            except Exception as e:
                # Handle other exceptions
                logger.error(f"Unexpected error during API request: {e}")
                raise
        
        # This should not be reached due to the retry logic above, but just in case
        if last_error:
            raise ConnectionError(f"Unable to connect to the API") from last_error
    
    def fetch_table(
        self,
        table_name: str,
        top: int = 100,
        skip: int = 0,
        new_data_only: bool = True,
        date_created_start: Optional[str] = None,
        filter_query: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch data from a table in the legacy system.
        
        Args:
            table_name: The name of the table to fetch data from
            top: The number of records to fetch (max per page)
            skip: The number of records to skip (for pagination)
            new_data_only: If True, fetch only records with modified_date > threshold
            date_created_start: Optional start date for filtering by creation date
            filter_query: Optional filter query string
            
        Returns:
            pd.DataFrame: A pandas DataFrame containing the fetched data
            
        Raises:
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
            DataError: If there's an issue with the data format
        """
        # Initialize parameters
        params = {
            '$top': top,
            '$skip': skip,
        }
        
        # Add optional filters
        if new_data_only:
            params['new_data_only'] = 'true'
        
        if date_created_start:
            params['date_created_start'] = date_created_start
            
        if filter_query:
            params['$filter'] = filter_query
        
        try:
            # Make the API request
            response = self._make_request('GET', table_name, params=params)
            
            # Parse the response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                raise DataError(f"Invalid JSON response: {e}") from e
            
            # Check if pagination is enabled and more data is available
            all_data = data
            
            if API_PAGINATION_ENABLED and isinstance(data, list) and len(data) == top:
                logger.debug(f"Fetched {len(data)} records, pagination may be needed")
                
                # Use the fetched data as the starting point
                result_data = data
                current_skip = skip + top
                
                # Fetch additional pages if available
                while True:
                    # Update pagination parameters
                    params['$skip'] = current_skip
                    
                    # Fetch the next page
                    try:
                        page_response = self._make_request('GET', table_name, params=params)
                        page_data = page_response.json()
                        
                        # Check if we got data
                        if isinstance(page_data, list) and len(page_data) > 0:
                            # Add to our result data
                            result_data.extend(page_data)
                            logger.debug(f"Fetched additional {len(page_data)} records, total: {len(result_data)}")
                            
                            # Update for next page
                            current_skip += len(page_data)
                            
                            # Break if we got fewer records than requested (last page)
                            if len(page_data) < top:
                                break
                        else:
                            # No more data
                            break
                            
                    except Exception as e:
                        logger.warning(f"Error fetching additional pages: {e}")
                        break
                
                # Use the combined data
                all_data = result_data
            
            # Convert to DataFrame
            if isinstance(all_data, list):
                df = pd.DataFrame(all_data)
                logger.info(f"Successfully fetched {len(df)} records from {table_name}")
                return df
            else:
                raise DataError(f"Unexpected data format: {type(all_data)}")
                
        except (ConnectionError, ResponseError) as e:
            # Re-raise these exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            logger.error(f"Failed to fetch data from {table_name}: {e}")
            raise DirectAPIError(f"Error fetching data: {e}") from e
    
    def push_field(
        self,
        table_name: str,
        record_id: Union[int, str],
        field_name: str,
        field_value: Any
    ) -> bool:
        """
        Push a field value to the legacy system.
        
        Args:
            table_name: The name of the table to update
            record_id: The ID of the record to update
            field_name: The name of the field to update
            field_value: The new value for the field
            
        Returns:
            bool: True if the update was successful
            
        Raises:
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
        """
        try:
            # Construct the endpoint
            endpoint = f"{table_name}/{record_id}/{field_name}"
            
            # Prepare the data
            data = {'value': field_value}
            
            # Make the API request
            response = self._make_request('PUT', endpoint, data=data)
            
            # Check for success
            return response.status_code == 200
            
        except (ConnectionError, ResponseError) as e:
            # Re-raise these exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            logger.error(f"Failed to push {field_name}={field_value} to {table_name}/{record_id}: {e}")
            raise DirectAPIError(f"Error updating data: {e}") from e
    
    def fetch_record(
        self,
        table_name: str,
        record_id: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Fetch a single record by ID.
        
        Args:
            table_name: The name of the table
            record_id: The ID of the record to fetch
            
        Returns:
            Dict[str, Any]: The record data as a dictionary
            
        Raises:
            ConnectionError: If unable to connect to the API
            ResponseError: If the API returns an error response
            DataError: If there's an issue with the data format
        """
        try:
            # Construct the endpoint
            endpoint = f"{table_name}/{record_id}"
            
            # Make the API request
            response = self._make_request('GET', endpoint)
            
            # Parse the response
            try:
                data = response.json()
                return data
            except json.JSONDecodeError as e:
                raise DataError(f"Invalid JSON response: {e}") from e
                
        except (ConnectionError, ResponseError, DataError) as e:
            # Re-raise these exceptions
            raise
        except Exception as e:
            # Wrap other exceptions
            logger.error(f"Failed to fetch record {record_id} from {table_name}: {e}")
            raise DirectAPIError(f"Error fetching record: {e}") from e 