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
import socket
import time

from pyerp.direct_api.exceptions import (
    DirectAPIError, AuthenticationError, ConnectionError, 
    ResponseError, DataError, ServerUnavailableError
)
from pyerp.direct_api.auth import get_session, invalidate_session
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
            ServerUnavailableError: If the server is unavailable or unreachable
            ConnectionError: If unable to connect to the API due to other connection issues
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
                elif response.status_code == 401 or response.status_code == 403 or response.status_code == 404:
                    # Authentication error - invalidate session, refresh and retry
                    logger.warning(f"Authentication failed with status {response.status_code}, invalidating session and refreshing")
                    invalidate_session(self.environment)
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
                    
            except requests.exceptions.ConnectTimeout as e:
                # Specifically handle connection timeouts - likely server unavailable
                last_error = e
                logger.warning(f"Connection timeout during API request: {e}")
                retries += 1
                
                if retries <= API_MAX_RETRIES:
                    backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                    logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    logger.error(f"Server appears to be unavailable after {retries-1} retries")
                    raise ServerUnavailableError(
                        f"Legacy ERP server at {self._get_base_url()} is unavailable (connection timeout)",
                        inner_exception=last_error
                    )
                    
            except requests.exceptions.ConnectionError as e:
                # Handle connection refused and similar errors
                last_error = e
                logger.warning(f"Connection error during API request: {e}")
                
                # Check if this is a connection refused error, which indicates server unavailability
                if "Connection refused" in str(e) or "Failed to establish a new connection" in str(e):
                    retries += 1
                    if retries <= API_MAX_RETRIES:
                        backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                        logger.info(f"Server appears to be down. Retrying in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                        time.sleep(backoff)
                    else:
                        logger.error(f"Server is unreachable after {retries-1} retries")
                        raise ServerUnavailableError(
                            f"Legacy ERP server at {self._get_base_url()} is unavailable (connection refused)",
                            inner_exception=last_error
                        )
                else:
                    # Handle other connection errors
                    retries += 1
                    if retries <= API_MAX_RETRIES:
                        backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                        logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                        time.sleep(backoff)
                    else:
                        logger.error(f"API request failed after {retries-1} retries")
                        raise ConnectionError(f"Unable to connect to the API after {retries-1} retries") from last_error
                    
            except socket.gaierror as e:
                # Handle DNS resolution errors or invalid hostnames
                last_error = e
                logger.warning(f"DNS resolution error: {e}")
                retries += 1
                
                if retries <= API_MAX_RETRIES:
                    backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
                    logger.info(f"Retrying request in {backoff:.2f} seconds (attempt {retries}/{API_MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    logger.error(f"Cannot resolve server hostname after {retries-1} retries")
                    raise ServerUnavailableError(
                        f"Cannot resolve legacy ERP server at {self._get_base_url()} (DNS error)",
                        inner_exception=last_error
                    )
            
            except requests.RequestException as e:
                # Handle other request exceptions
                last_error = e
                logger.warning(f"Request error during API request: {e}")
                
                # Calculate backoff time for retry
                retries += 1
                
                if retries <= API_MAX_RETRIES:
                    backoff = API_RETRY_BACKOFF_FACTOR * (2 ** retries)
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
            
            # Handle 4D API response format
            if isinstance(data, dict) and '__ENTITIES' in data:
                # Extract entities from the 4D API response
                entities = data['__ENTITIES']
                logger.info(f"Extracted {len(entities)} entities from 4D API response")
                
                # Check if pagination is enabled and more data is available
                total_count = data.get('__COUNT', 0)
                current_count = len(entities)
                
                if API_PAGINATION_ENABLED and current_count < total_count and current_count == top:
                    logger.debug(f"Fetched {current_count} of {total_count} records, pagination needed")
                    
                    # Use the fetched data as the starting point
                    result_data = entities
                    current_skip = skip + top
                    
                    # Fetch additional pages if available
                    while current_skip < total_count and len(result_data) < total_count:
                        # Update pagination parameters
                        params['$skip'] = current_skip
                        
                        # Fetch the next page
                        try:
                            page_response = self._make_request('GET', table_name, params=params)
                            page_data = page_response.json()
                            
                            # Check if we got data in the expected format
                            if isinstance(page_data, dict) and '__ENTITIES' in page_data:
                                page_entities = page_data['__ENTITIES']
                                
                                # Add to our result data
                                result_data.extend(page_entities)
                                logger.debug(f"Fetched additional {len(page_entities)} records, total: {len(result_data)}")
                                
                                # Update for next page
                                current_skip += len(page_entities)
                                
                                # Break if we got fewer records than requested (last page)
                                if len(page_entities) < top:
                                    break
                            else:
                                # Unexpected format
                                logger.warning(f"Unexpected format in pagination response: {type(page_data)}")
                                break
                                
                        except Exception as e:
                            logger.warning(f"Error fetching additional pages: {e}")
                            break
                    
                    # Use the combined data
                    all_data = result_data
                else:
                    all_data = entities
                
                # Convert to DataFrame
                df = pd.DataFrame(all_data)
                logger.info(f"Successfully fetched {len(df)} records from {table_name}")
                return df
            elif isinstance(data, list):
                # Handle direct list response (less common)
                df = pd.DataFrame(data)
                logger.info(f"Successfully fetched {len(df)} records from {table_name}")
                return df
            else:
                # Unexpected format
                raise DataError(f"Unexpected data format: {type(data)}. Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
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