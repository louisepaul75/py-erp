#!/usr/bin/env python
"""
Simple script to run validator tests in isolation.

This script allows testing the form validation framework without 
requiring a full Django test setup with database migrations.
"""

import sys
import unittest
import os
import importlib.util
import importlib

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Make sure Django settings are configured
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.test")

# Mock Django's translation functions to avoid dependencies
import django.utils.translation
django.utils.translation.gettext = lambda x: x
django.utils.translation.gettext_lazy = lambda x: x

# Directly import test modules
test_modules = [
    'pyerp.core.tests.test_validator_edge_cases',
    'pyerp.core.tests.test_custom_validators',
    'pyerp.core.tests.test_validator_composition',
    'pyerp.core.tests.test_form_business_rules',
]

# Import the test modules
for module_name in test_modules:
    try:
        importlib.import_module(module_name)
        # Import all symbols from the module into the current namespace
        exec(f"from {module_name} import *")
    except ImportError as e:
        print(f"Warning: Could not import {module_name}: {e}")

# Replace Django's TestCase with unittest.TestCase
from django.test import TestCase
TestCase.setUp = unittest.TestCase.setUp
TestCase.tearDown = unittest.TestCase.tearDown
TestCase.assertIn = unittest.TestCase.assertIn
TestCase.assertNotIn = unittest.TestCase.assertNotIn
TestCase.assertTrue = unittest.TestCase.assertTrue
TestCase.assertFalse = unittest.TestCase.assertFalse
TestCase.assertEqual = unittest.TestCase.assertEqual
TestCase.assertGreater = unittest.TestCase.assertGreater

# Create and run the test suite
def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Add test cases from modules
    for module_name in test_modules:
        try:
            module = sys.modules[module_name]
            test_suite.addTests(test_loader.loadTestsFromModule(module))
        except KeyError:
            print(f"Warning: Module {module_name} not found")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite)

if __name__ == "__main__":
    print("Running validator tests...")
    result = run_tests()
    sys.exit(not result.wasSuccessful()) 