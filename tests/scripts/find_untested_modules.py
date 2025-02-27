#!/usr/bin/env python
"""
Find modules that don't have corresponding test files.

This script identifies Python modules in the 'pyerp' package that don't have
corresponding test files in the 'tests' directory.
"""
import os
import sys
import re
from pathlib import Path


def find_project_modules(base_dir):
    """Find all Python modules in the pyerp package."""
    modules = []
    for root, _, files in os.walk(os.path.join(base_dir, 'pyerp')):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                rel_path = os.path.relpath(os.path.join(root, file), base_dir)
                modules.append(rel_path)
    return modules


def find_test_files(base_dir):
    """Find all test files in the tests directory."""
    test_files = []
    for root, _, files in os.walk(os.path.join(base_dir, 'tests')):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    return test_files


def extract_module_names(test_files):
    """Extract module names being tested from test files."""
    tested_modules = set()
    
    for test_file in test_files:
        # Extract module name from test file name
        # Example: test_validators.py -> validators
        module_name = os.path.basename(test_file)[5:-3]  # Remove 'test_' and '.py'
        tested_modules.add(module_name)
        
        # Also check imports in the file to detect tested modules
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                # Look for imports from pyerp
                imports = re.findall(r'from pyerp\.(\w+)\.(\w+) import', content)
                for app, module in imports:
                    tested_modules.add(f"{app}/{module}")
        except Exception as e:
            print(f"Warning: Could not read {test_file}: {e}")
    
    return tested_modules


def main():
    """Main function to find untested modules."""
    # Get project root directory (assumes script is in the tests directory)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find all modules in the pyerp package
    modules = find_project_modules(base_dir)
    
    # Find all test files
    test_files = find_test_files(base_dir)
    
    # Extract module names being tested
    tested_modules = extract_module_names(test_files)
    
    # Find untested modules
    untested_modules = []
    for module in modules:
        # Skip __init__.py files
        if '__init__.py' in module:
            continue
            
        # Get module name without extension and check if it's tested
        module_name = os.path.basename(module)[:-3]  # Remove '.py'
        module_dir = os.path.dirname(module).replace('pyerp/', '')
        
        # Check multiple possible naming schemes
        if (module_name not in tested_modules and
            f"{module_dir}/{module_name}" not in tested_modules):
            untested_modules.append(module)
    
    # Group by directory
    untested_by_dir = {}
    for module in untested_modules:
        dir_name = os.path.dirname(module)
        if dir_name not in untested_by_dir:
            untested_by_dir[dir_name] = []
        untested_by_dir[dir_name].append(os.path.basename(module))
    
    # Print results
    print(f"Found {len(modules)} total modules and {len(test_files)} test files")
    print(f"Found {len(untested_modules)} untested modules")
    print("\nUntested modules by directory:")
    
    for dir_name, files in sorted(untested_by_dir.items()):
        print(f"\n{dir_name} ({len(files)} untested):")
        for file in sorted(files):
            print(f"  - {file}")
    
    # Output priorities based on module types
    print("\n\nSuggested Testing Priorities:")
    
    # Define priority categories and their patterns
    priorities = {
        "Critical Business Logic": [r'pyerp/(core|products)/.*\.py'],
        "Views and APIs": [r'.*views\.py', r'.*api\.py'],
        "Forms and Validation": [r'.*forms\.py', r'.*validators\.py'],
        "Management Commands": [r'pyerp/management/commands/.*\.py'],
        "Models": [r'.*models\.py'],
        "Utilities": [r'.*utils\.py', r'.*helpers\.py'],
    }
    
    # Categorize modules
    for category, patterns in priorities.items():
        matching_modules = []
        for module in untested_modules:
            if any(re.match(pattern, module) for pattern in patterns):
                matching_modules.append(module)
        
        if matching_modules:
            print(f"\n{category} ({len(matching_modules)}):")
            for module in sorted(matching_modules):
                print(f"  - {module}")


if __name__ == "__main__":
    main() 