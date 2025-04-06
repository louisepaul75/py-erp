"""
Environment variable loader utility for pyERP.

This module provides a standardized way to load environment variables from
the appropriate .env file based on the current environment.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def get_project_root():
    """Get the project root directory."""
    current_path = Path(__file__).resolve().parent.parent.parent
    return current_path


def get_environment():
    """Get the current environment (dev, prod)."""
    pyerp_env = os.environ.get("PYERP_ENV")
    if pyerp_env:
        return pyerp_env

    # If not set, determine from DJANGO_SETTINGS_MODULE
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")
    if "production" in settings_module:
        return "prod"
    return "dev"  # Default to development


def get_settings_module(env_name=None):
    """
    Get the appropriate Django settings module for the current environment.

    Args:
        env_name (str, optional): Environment name. If not provided,
            will be determined.

    Returns:
        str: The Django settings module path
    """
    if env_name is None:
        env_name = get_environment()

    settings_mapping = {
        "prod": "pyerp.config.settings.production",
        "test": "pyerp.config.settings.test",
        "dev": "pyerp.config.settings.development",
    }

    return settings_mapping.get(env_name, settings_mapping["dev"])


def load_environment_variables(verbose=False):
    """
    Load the appropriate environment variables file based on the current
    environment.

    Args:
        verbose (bool): Whether to print debug information

    Returns:
        bool: True if environment variables were loaded successfully,
            False otherwise
    """
    env_name = get_environment()
    project_root = get_project_root()

    # Always use .env.dev for tests and development
    if env_name in ["test", "dev"]:
        env_name = "dev"

    # Define environment file paths with priority
    env_paths = [
        project_root / "config" / "env" / ".env.dev",  # First priority for development
        project_root / "config" / "env" / f".env.{env_name}",  # Second priority
        project_root / "config" / "env" / ".env",  # Third priority
        project_root / ".env",  # Fourth priority
    ]

    success = False
    # Try to load from each path in order
    for env_path in env_paths:
        if verbose:
            print(f"Checking for environment file at: {env_path}")
        if env_path.exists():
            if verbose:
                print(f"Loading environment from {env_path}")
            load_dotenv(str(env_path), override=True)  # Added override=True to ensure variables are set
            success = True
            break

    if not success and verbose:
        print(f"Warning: No environment file found for {env_name} environment")
        print(f"Searched paths: {[str(p) for p in env_paths]}")

    # Always set these core environment variables
    os.environ["PYERP_ENV"] = env_name
    os.environ["DJANGO_SETTINGS_MODULE"] = get_settings_module(env_name)

    return success
