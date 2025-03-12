"""
1Password Connect integration for pyERP.

This module provides utilities for retrieving secrets from a 1Password Connect server.
"""

import os
import logging
from onepasswordconnectsdk.client import Client, new_client_from_environment

logger = logging.getLogger('onepassword')

# Default Connect server URL and token from environment variables
DEFAULT_CONNECT_SERVER = os.environ.get('OP_CONNECT_HOST', 'http://192.168.73.65:8080')
DEFAULT_CONNECT_TOKEN = os.environ.get('OP_CONNECT_TOKEN', '')
DEFAULT_CONNECT_VAULT = os.environ.get('OP_CONNECT_VAULT', 'dev')

# Cache for the 1Password client to avoid creating a new client for each request
_op_client = None


def get_op_client(server_url=None, access_token=None):
    """
    Get a 1Password Connect client.
    
    Args:
        server_url (str, optional): The URL of the 1Password Connect server.
            Defaults to the value of OP_CONNECT_HOST environment variable or 'http://192.168.73.65:8080'.
        access_token (str, optional): The access token for the 1Password Connect server.
            Defaults to the value of OP_CONNECT_TOKEN environment variable.
            
    Returns:
        Client: A 1Password Connect client.
    """
    global _op_client
    
    if _op_client is not None:
        return _op_client
    
    try:
        # Try to create a client from environment variables first
        if server_url is None and access_token is None:
            try:
                _op_client = new_client_from_environment()
                logger.info("Created 1Password client from environment variables")
                return _op_client
            except Exception as e:
                logger.warning(f"Failed to create 1Password client from environment: {str(e)}")
        
        # Fall back to explicit parameters
        server_url = server_url or DEFAULT_CONNECT_SERVER
        access_token = access_token or DEFAULT_CONNECT_TOKEN
        
        if not access_token:
            logger.error("No 1Password Connect access token provided")
            return None
        
        _op_client = Client(server_url, access_token)
        logger.info(f"Created 1Password client for server: {server_url}")
        return _op_client
    
    except Exception as e:
        logger.error(f"Error creating 1Password client: {str(e)}")
        return None


def get_secret(item_name, field_name=None, vault=None, server_url=None, access_token=None):
    """
    Get a secret from 1Password.
    
    Args:
        item_name (str): The name of the item in 1Password.
        field_name (str, optional): The name of the field to retrieve. 
            If not provided, returns the password field.
        vault (str, optional): The name or UUID of the vault containing the item.
            Defaults to the value of OP_CONNECT_VAULT environment variable or 'dev'.
        server_url (str, optional): The URL of the 1Password Connect server.
        access_token (str, optional): The access token for the 1Password Connect server.
        
    Returns:
        str: The secret value, or None if not found or an error occurred.
    """
    try:
        client = get_op_client(server_url, access_token)
        if client is None:
            return None
        
        vault = vault or DEFAULT_CONNECT_VAULT
        
        # Get the item
        item = client.get_item_by_title(item_name, vault)
        if item is None:
            logger.error(f"Item '{item_name}' not found in vault '{vault}'")
            return None
        
        # In 1Password Connect SDK, fields is a list of Field objects
        field_id = field_name or "password"
        
        # Find the field with the matching id
        for field in item.fields:
            if field.id == field_id:
                return field.value
        
        # If we get here, the field was not found
        logger.error(f"Field '{field_id}' not found in item '{item_name}'")
        return None
    
    except Exception as e:
        logger.error(f"Error retrieving secret from 1Password: {str(e)}")
        return None


def get_email_password(email_username=None, item_name=None, vault=None, server_url=None, access_token=None):
    """
    Get the email password from 1Password.
    
    Args:
        email_username (str, optional): The email username to use as the item name if item_name is not provided.
        item_name (str, optional): The name of the item in 1Password. 
            If not provided, uses the email_username.
        vault (str, optional): The name or UUID of the vault containing the item.
        server_url (str, optional): The URL of the 1Password Connect server.
        access_token (str, optional): The access token for the 1Password Connect server.
        
    Returns:
        str: The email password, or None if not found or an error occurred.
    """
    if not item_name and not email_username:
        logger.error("Either item_name or email_username must be provided")
        return None
    
    item_name = item_name or email_username
    return get_secret(item_name, "password", vault, server_url, access_token) 