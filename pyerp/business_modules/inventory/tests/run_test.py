#!/usr/bin/env python
"""
Test runner script for inventory tests that properly initializes Django.
"""

import os
import sys
import signal
import django
from django.conf import settings
from django.test.utils import get_runner

def timeout_handler(signum, frame):
    """Handle test timeout by raising an exception."""
    raise TimeoutError("Test execution timed out after 30 seconds")

if __name__ == "__main__":
    try:
        # Set up timeout handler
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)  # Set 30 second timeout

        # Set up Django environment
        os.environ['DJANGO_SETTINGS_MODULE'] = 'pyerp.config.settings.testing'
        django.setup()

        # Get the test runner with interactive=False to avoid prompts
        TestRunner = get_runner(settings)
        test_runner = TestRunner(
            interactive=False,
            verbosity=2,
            keepdb=True  # Keep the test database between runs
        )

        # Run the specific test
        test_path = (
            'pyerp.business_modules.inventory.tests.test_inventory_views.'
            'TestInventoryViewsErrorHandling.test_add_product_to_box_service_error'
        )
        failures = test_runner.run_tests([test_path])
        
        # Cancel the alarm
        signal.alarm(0)
        
        sys.exit(bool(failures))
    except TimeoutError as e:
        print(f"\nTest execution failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed with error: {e}")
        sys.exit(1)
    finally:
        # Ensure alarm is cancelled even if an error occurs
        signal.alarm(0) 