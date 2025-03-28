#!/usr/bin/env python
"""
Temporary fix for customer sync issues.

This script modifies the SyncMapping record to move the environment and table_name
fields to the top level of the configuration for the Legacy API Extractor.
"""

import os
import sys
import yaml
from pathlib import Path


# Run the fixed customer sync directly
def run_fixed_customer_sync(debug=False, force_update=False):
    """Run the customer sync with fixed configurations."""
    print("Starting customer sync process with fixed configuration...")
    
    try:
        # Load configuration
        config_path = Path(__file__).resolve().parent / "pyerp/sync/config/customers_sync.yaml"
        print(f"Loading config from: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        # Run the direct sync command
        cmd = ["python", "manage.py", "run_sync", "--entity-type", "customer"]
        
        if debug:
            cmd.append("--debug")
            print("Debug mode enabled")
        
        if force_update:
            cmd.append("--force-update")
            print("Force update enabled")
        
        # Set required environment variables
        os.environ["LEGACY_ERP_TABLE_NAME"] = "Kunden"
        os.environ["LEGACY_ERP_ENVIRONMENT"] = "live"
        
        # Print the command for debugging
        print(f"Running command: {' '.join(cmd)}")
        
        # Use os.system to run the command
        exit_code = os.system(" ".join(cmd))
        
        if exit_code == 0:
            print("Customer sync completed successfully")
            return True
        else:
            print(f"Customer sync failed with exit code: {exit_code}")
            return False
    
    except Exception as e:
        print(f"Error running customer sync: {e}")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    debug = '--debug' in sys.argv
    force_update = '--force-update' in sys.argv
    
    # Run the fixed sync
    success = run_fixed_customer_sync(debug=debug, force_update=force_update)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 