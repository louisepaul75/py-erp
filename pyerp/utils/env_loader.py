"""
Environment variable loader utility for pyERP.

This module provides a standardized way to load environment variables from
the appropriate .env file based on the current environment.
"""
import os
import sys  # noqa: F401
from pathlib import Path
from dotenv import load_dotenv


def get_project_root():
    """Get the project root directory."""
    # Handle different entry points by traversing up until we find manage.py
    current_path = Path(__file__).resolve().parent.parent.parent
    return current_path


def get_environment():
    """Get the current environment (dev, prod, test)."""
    # Check for explicitly set environment
    pyerp_env = os.environ.get('PYERP_ENV')
    if pyerp_env:
        return pyerp_env

    # If not set, determine from DJANGO_SETTINGS_MODULE
    settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
    if 'production' in settings_module:
        return 'prod'
    elif 'testing' in settings_module or 'test' in settings_module:
        return 'test'
    else:
        return 'dev'  # Default to development


def load_environment_variables(verbose=False):
    """
    Load the appropriate environment variables file based on the current environment.  # noqa: E501

    Args:
        verbose (bool): Whether to print debug information

    Returns:
        bool: True if environment variables were loaded successfully, False otherwise  # noqa: E501
    """
    env_name = get_environment()
    project_root = get_project_root()

    # Define environment file paths with priority
    env_paths = [
        project_root / 'config' / 'env' / f'.env.{env_name}',  # First priority: config/env/.env.{env}  # noqa: E501
        project_root / 'config' / 'env' / '.env',              # Second priority: config/env/.env  # noqa: E501
        project_root / '.env',                                 # Third priority: .env in project root  # noqa: E501
    ]

    # Try to load from each path in order
    for env_path in env_paths:
        if env_path.exists():
            if verbose:
                print(f"Loading environment from {env_path}")
            load_dotenv(str(env_path))
            # Set PYERP_ENV to ensure consistency
            os.environ['PYERP_ENV'] = env_name
            return True

    if verbose:
        print(f"Warning: No environment file found for {env_name} environment")
        print(f"Searched paths: {[str(p) for p in env_paths]}")

    return False
