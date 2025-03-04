#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

import dotenv


def main():
    """Run administrative tasks."""
    # Load environment variables from config/env/.env file
    env_file = Path('.') / 'config' / 'env' / '.env'
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        dotenv.load_dotenv(str(env_file))
    else:
        print(f"Warning: Environment file not found at {env_file}")

    # Set the default Django settings module if not defined
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main() 