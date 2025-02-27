#!/usr/bin/env python
"""
Script to run specific test files that should work correctly.

This script runs tests in two ways:
1. Unit tests with pytest for non-Django specific tests
2. Django tests using manage.py test for tests that require Django setup
"""
import os
import sys
import subprocess

def main():
    """Run the working tests."""
    # Set up environment
    os.environ["DJANGO_SETTINGS_MODULE"] = "pyerp.settings.testing"
    
    # Run Django tests
    print("\n=== Running Django tests ===")
    django_result = subprocess.run(
        [sys.executable, "manage.py", "test", "tests/unit", "--settings=pyerp.settings.testing"], 
        capture_output=True,
        text=True
    )
    print(django_result.stdout)
    if django_result.stderr:
        print(f"DJANGO TEST ERRORS:\n{django_result.stderr}")
    
    print(f"Django tests exit code: {django_result.returncode}")
    
    # Show a summary of the test results
    print("\n=== Test Summary ===")
    print(f"Django Tests: {'PASSED' if django_result.returncode == 0 else 'FAILED'}")
    
    return 0 if django_result.returncode == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 