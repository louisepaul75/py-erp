#!/usr/bin/env python
import os
import django
import sys

# Set environment variables for SQLite testing
os.environ["DJANGO_SETTINGS_MODULE"] = "pyerp.config.settings.test"
os.environ["SKIP_DB_CHECK"] = "1"  # Skip database check

# Initialize Django
django.setup()

# Run the tests with Django test runner
from django.test.runner import DiscoverRunner

test_runner = DiscoverRunner()
failures = test_runner.run_tests(["pyerp.business_modules.products"])
sys.exit(bool(failures)) 