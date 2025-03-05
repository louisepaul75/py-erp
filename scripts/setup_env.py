#!/usr/bin/env python
"""
Environment Setup Script for pyERP

This script creates a .env symlink in the project root pointing to the
appropriate environment file in config/env/ based on the specified environment.

Usage:
    python scripts/setup_env.py [dev|prod|test]

Example:
    python scripts/setup_env.py dev  # Set up development environment
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Set up environment for pyERP')
    parser.add_argument('environment', choices=['dev', 'prod', 'test'], 
                        help='Environment to set up (dev, prod, or test)')
    parser.add_argument('--force', action='store_true', 
                        help='Force overwrite existing .env file or symlink')
    
    args = parser.parse_args()
    
    # Get project root directory
    project_root = Path(__file__).resolve().parent.parent
    
    # Define paths
    env_dir = project_root / 'config' / 'env'
    source_file = env_dir / f'.env.{args.environment}'
    target_file = project_root / '.env'
    
    # Verify that source file exists
    if not source_file.exists():
        print(f"Error: Source environment file {source_file} does not exist.")
        sys.exit(1)
    
    # Check if target file already exists
    if target_file.exists() or target_file.is_symlink():
        if args.force:
            # Remove existing file or symlink
            if target_file.is_symlink():
                target_file.unlink()
                print(f"Removed existing symlink {target_file}")
            else:
                target_file.unlink()
                print(f"Removed existing file {target_file}")
        else:
            print(f"Error: Target file {target_file} already exists. Use --force to overwrite.")
            sys.exit(1)
    
    # Create the symlink or copy the file
    try:
        # Try to create a symlink first
        if hasattr(os, 'symlink'):
            # Use relative path for the symlink
            relative_source = os.path.relpath(source_file, project_root)
            os.symlink(relative_source, target_file)
            print(f"Created symlink: {target_file} -> {relative_source}")
        else:
            # On systems without symlink support (e.g., Windows without admin privileges),
            # copy the file instead
            shutil.copy2(source_file, target_file)
            print(f"Copied {source_file} to {target_file}")
            
        # Set environment variable
        os.environ['PYERP_ENV'] = args.environment
        print(f"Environment set to: {args.environment}")
        
    except Exception as e:
        print(f"Error setting up environment: {e}")
        sys.exit(1)
    
    print("Environment setup complete.")

if __name__ == '__main__':
    main() 