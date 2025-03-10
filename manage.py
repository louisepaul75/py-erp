#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys
from pathlib import Path

# Make sure pyerp module is in path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    """Run administrative tasks."""
    # Import and use the centralized environment loader
    from pyerp.utils.env_loader import load_environment_variables

    load_environment_variables(verbose=True)

    # Set the default Django settings module if not defined
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "pyerp.config.settings.development"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?",
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
