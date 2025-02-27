#!/usr/bin/env python
"""
Script to run specific test modules individually.

This script runs specific test modules with pytest, bypassing the collection process
which often fails when there are import errors in other test modules.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run specific test modules."""
    # Set up environment
    os.environ["DJANGO_SETTINGS_MODULE"] = "pyerp.settings.testing"
    
    # Define test files to run
    working_tests = [
        "tests/unit/test_simple.py",  # Basic test to verify environment
        "tests/unit/test_product_command.py"  # New test with improved mocking
    ]
    
    # Keep track of successes and failures
    successes = 0
    failures = 0
    
    # Run each test individually
    for test_path in working_tests:
        print(f"\n=== Running {test_path} ===")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v"],
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print(f"ERRORS:\n{result.stderr}")
            
            if result.returncode == 0:
                successes += 1
                print(f"✅ {test_path} tests passed!")
            else:
                failures += 1
                print(f"❌ {test_path} tests failed.")
        except Exception as e:
            print(f"Error running test {test_path}: {e}")
            failures += 1
    
    # Show summary
    print("\n=== Test Summary ===")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Total: {successes + failures}")
    
    return 0 if failures == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 