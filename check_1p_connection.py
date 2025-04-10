#!/usr/bin/env python3
"""
Test script to check 1Password Connect API integration.
"""

import os
import sys

try:
    from onepasswordconnectsdk import client
    from onepasswordconnectsdk.models import Field, Item
except ImportError:
    print("Error: onepasswordconnectsdk is not installed.")
    print("Install it with: pip install onepasswordconnectsdk")
    sys.exit(1)

def fetch_item_details(op_client, vault_uuid, item_name):
    """Helper function to fetch and display item details from 1Password."""
    print(f"\nAttempting to fetch item '{item_name}' from vault '{vault_uuid}'...")
    
    try:
        # Get all items in the vault
        items = op_client.get_items(vault_uuid)
        
        # Find the item with the matching title
        target_item = None
        for item in items:
            if item.title == item_name:
                target_item = item
                break
        
        if target_item:
            # Get the complete item with all fields
            full_item = op_client.get_item(target_item.id, vault_uuid)
            print(f"\nSuccessfully retrieved item: {full_item.title}")
            print("Fields with detailed information:")
            for field in full_item.fields:
                # Print all field information except password value
                field_value = field.value
                if field.label and (field.label.lower() == "password" or field.purpose == "PASSWORD"):
                    field_value = "********"
                
                print(f"  - Label: '{field.label}' | ID: '{field.id}' | Type: '{field.type}' | Purpose: '{field.purpose}' | Value: '{field_value}'")
            return True
        else:
            print(f"Item '{item_name}' not found in vault.")
            return False
                
    except Exception as e:
        print(f"Error fetching item '{item_name}': {e}")
        return False

def main():
    # Get 1Password Connect credentials from environment
    op_connect_host = os.environ.get("OP_CONNECT_HOST")
    op_connect_token = os.environ.get("OP_CONNECT_TOKEN")
    
    if not op_connect_host or not op_connect_token:
        print("Error: OP_CONNECT_HOST or OP_CONNECT_TOKEN environment variables are not set.")
        sys.exit(1)
    
    print(f"OP_CONNECT_HOST: {op_connect_host}")
    print(f"OP_CONNECT_TOKEN: {op_connect_token[:8]}...{op_connect_token[-5:] if len(op_connect_token) > 10 else ''}")
    
    try:
        # Initialize the client
        print("Initializing 1Password Connect client...")
        op_client = client.new_client(op_connect_host, op_connect_token)
        
        # Test connection by listing vaults
        print("Listing available vaults...")
        vaults = op_client.get_vaults()
        print(f"Found {len(vaults)} vaults:")
        
        # Find the dev vault UUID
        vault_uuid = None
        for vault in vaults:
            print(f"  - {vault.name} (ID: {vault.id})")
            if vault.name == "dev":
                vault_uuid = vault.id
        
        if not vault_uuid:
            print("Error: Could not find a vault named 'dev'")
            sys.exit(1)
        
        # Show all items in the vault
        items = op_client.get_items(vault_uuid)
        print(f"\nFound {len(items)} items in the vault:")
        for item in items:
            print(f"  - {item.title} (ID: {item.id})")
            
        # Fetch and display postgres_db credentials    
        db_success = fetch_item_details(op_client, vault_uuid, "postgres_db")
        
        # Fetch and display image_cms_api credentials
        img_success = fetch_item_details(op_client, vault_uuid, "image_cms_api")
        
        if db_success and img_success:
            print("\n✅ Connection test SUCCESSFUL for all items!")
        else:
            print("\n⚠️ Connection test PARTIALLY SUCCESSFUL - some items could not be retrieved.")
            
    except Exception as e:
        print(f"Error initializing 1Password client: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 