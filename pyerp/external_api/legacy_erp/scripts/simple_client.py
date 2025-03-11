"""
Simple API client for the legacy ERP system.

This module provides a simplified version of the LegacyERPClient for use
in extraction tasks, maintaining compatibility with the previous
SimpleAPIClient.
"""

import logging
from typing import Optional

import pandas as pd

from pyerp.external_api.legacy_erp.base import BaseAPIClient
from pyerp.external_api.legacy_erp.exceptions import LegacyERPError

# Configure logging
logger = logging.getLogger(__name__)


class SimpleAPIClient(BaseAPIClient):
    """
    Simple client for the legacy ERP API with a subset of functionality.
    
    This class maintains compatibility with the
    direct_api.scripts.getTable.SimpleAPIClient interface to avoid breaking
    existing code that depends on it.
    """
    
    def __init__(self, environment: str = "live", timeout: int = None):
        """
        Initialize a new simple API client.
        
        Args:
            environment: The API environment to use ('live', 'test', etc.)
            timeout: Optional timeout for API requests in seconds
        """
        super().__init__(environment=environment, timeout=timeout)
        # Don't use username/password for this client
        self.username = None
        self.password = None
        logger.debug(
            "Initialized SimpleAPIClient for environment: %s",
            environment,
        )
    
    def login(self):
        """Attempt to log in and get a new session cookie without basic auth."""
        try:
            logger.info("------ LOGGING IN ------")
            self.session.cookies.clear()
            logger.info("Cleared existing cookies")

            # Attempt to access an endpoint that will set a cookie
            url = f"{self.base_url}/rest/$info"
            logger.info(f"Login request URL: {url}")

            # Make the request without basic auth
            response = self.session.get(url)

            # Log response details
            logger.info(f"Login response status: {response.status_code}")
            self._log_response_cookies(response)

            # Check if we got cookies in the response
            wasid_cookie = None
            for cookie in response.cookies:
                if cookie.name == "WASID4D":
                    wasid_cookie = cookie.value
                    break

            dsid_cookie = self.session.cookies.get("4DSID_WSZ-DB")

            # Log what we found
            logger.info(f"Found WASID4D cookie: {'Yes' if wasid_cookie else 'No'}")
            logger.info(f"Found 4DSID_WSZ-DB cookie: {'Yes' if dsid_cookie else 'No'}")

            # Use either cookie (prefer WASID4D)
            if wasid_cookie:
                self.session.cookies.clear()
                self.session_id = wasid_cookie
                self.session.cookies.set("WASID4D", wasid_cookie)
                safe_id = (
                    f"{wasid_cookie[:5]}...{wasid_cookie[-5:]}"
                    if len(wasid_cookie) > 10
                    else wasid_cookie
                )
                logger.info(f"Set single WASID4D cookie: {safe_id}")
                self.save_session_cookie()
                return True
            if dsid_cookie:
                self.session.cookies.clear()
                self.session_id = dsid_cookie
                self.session.cookies.set("WASID4D", dsid_cookie)
                safe_id = (
                    f"{dsid_cookie[:5]}...{dsid_cookie[-5:]}"
                    if len(dsid_cookie) > 10
                    else dsid_cookie
                )
                logger.info(f"Set single WASID4D cookie using 4DSID value: {safe_id}")
                self.save_session_cookie()
                return True
            logger.warning("No session cookies received during login attempt")
            return False
        except Exception as e:
            logger.warning(f"Login failed: {e}")
            return False
    
    def validate_session(self):
        """Validate the current session by making a simple API request."""
        try:
            logger.info("------ VALIDATING SESSION ------")
            self._log_cookies("Cookies before validation")

            # Try a simple API request to check if our session is valid
            url = f"{self.base_url}/rest/$info"
            logger.info(f"Validation request URL: {url}")

            # Make the request, ensuring the session cookie is used
            response = self.session.get(url)

            # Log response and cookies
            logger.info(f"Validation response status: {response.status_code}")
            self._log_response_cookies(response)

            # Check if we got a successful response
            if response.status_code == 200:
                logger.info("Session validated successfully")

                # Get the new session cookie from the response
                wasid_cookie = None
                for cookie in response.cookies:
                    if cookie.name == "WASID4D":
                        wasid_cookie = cookie.value
                        logger.info(
                            f"Found new session cookie in response: {cookie.name}"
                        )
                        break

                # If we received a new cookie, update our session
                if wasid_cookie:
                    logger.info("Updating session with new cookie from response")
                    self.session.cookies.clear()
                    logger.info("Cleared all existing cookies")

                    # Set the new cookie value
                    self.session_id = wasid_cookie
                    self.session.cookies.set("WASID4D", wasid_cookie)
                    logger.info(
                        "Set single new cookie WASID4D with value from response"
                    )

                    # Save the updated cookie
                    self.save_session_cookie()
                else:
                    logger.info("No new session cookie received, keeping existing one")
                    if self.session_id and not self.session.cookies.get("WASID4D"):
                        logger.info("Re-adding existing session cookie")
                        self.session.cookies.clear()
                        self.session.cookies.set("WASID4D", self.session_id)

                return True
            logger.warning(f"Session validation failed: {response.status_code}")
            if response.text:
                logger.warning(f"Response text: {response.text[:200]}...")
            return False
        except Exception as e:
            logger.warning(f"Session validation failed with exception: {e}")
            return False
    
    def ensure_session(self):
        """Ensure we have a valid session, attempting login if needed."""
        if not self.session_id:
            logger.info("No session ID loaded, attempting login")
            return self.login()

        # Clear all cookies and start fresh
        self.session.cookies.clear()

        # Set just our session ID cookie
        self.session.cookies.set("WASID4D", self.session_id)
        safe_id = (
            f"{self.session_id[:5]}...{self.session_id[-5:]}"
            if len(self.session_id) > 10
            else self.session_id
        )
        logger.info(f"Set single WASID4D cookie: {safe_id}")

        # Validate the session
        if self.validate_session():
            return True

        # If validation failed, try to log in
        logger.info("Session validation failed, attempting to get a new session")
        return self.login()
    
    def check_connection(self) -> bool:
        """
        Check if the connection to the legacy ERP API is working.
        
        This method is used by the health check system to verify 
        that the API is accessible and responding correctly.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Raises:
            LegacyERPError: If an unexpected error occurs during validation
        """
        try:
            logger.info("Checking connection to legacy ERP API")
            return self.validate_session()
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            raise LegacyERPError(f"Failed to check connection: {e}")
    
    def fetch_table(
        self,
        table_name: str,
        top: int = 100,
        skip: int = 0,
        filter_query: Optional[str] = None,
        all_records: bool = False,
        fail_on_filter_error: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch records from a table in the legacy ERP system.
        
        Args:
            table_name: Name of the table to fetch records from
            top: Maximum number of records to fetch (page size)
            skip: Number of records to skip (for pagination)
            filter_query: OData filter query string
            all_records: Whether to fetch all records (ignore pagination)
            fail_on_filter_error: If True, raise an error if filter doesn't work
            
        Returns:
            DataFrame containing the fetched records
        """
        try:
            return super().fetch_table(
                table_name=table_name,
                top=top,
                skip=skip,
                filter_query=filter_query,
                all_records=all_records,
                fail_on_filter_error=fail_on_filter_error,
            )
        except Exception as e:
            raise LegacyERPError(f"Failed to fetch table: {e}") 