#!/usr/bin/env python
"""
Dependency Scanner for Django Project

This script scans Django settings files and other project files
to automatically detect required dependencies and ensure they are
properly included in requirements files.
"""

import os
import re
import ast
import sys
from pathlib import Path

def find_settings_files(base_dir):
    """Find all Django settings files in the project."""
    settings_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') and ('settings' in file or 'settings' in root):
                settings_files.append(os.path.join(root, file))
    return settings_files

def scan_file_for_imports(file_path):
    """Extract all imports from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            # Check for regular imports
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name.split('.')[0])
            # Check for from ... import ...
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imports.append(node.module.split('.')[0])
        
        return set(imports)
    except SyntaxError:
        print(f"Syntax error in {file_path}, skipping...")
        return set()

def scan_settings_for_backends(file_path):
    """Extract backend strings from Django settings files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    backends = []
    
    # Regular expression patterns for common Django backend settings
    patterns = [
        r"'BACKEND':\s*'([\w_.]+)'",
        r'"BACKEND":\s*"([\w_.]+)"',
    ]
    
    for pattern in patterns:
        backends.extend(re.findall(pattern, content))
    
    # Convert backend paths to package names
    packages = set()
    for backend in backends:
        parts = backend.split('.')
        if len(parts) > 1:
            # Take first part of backend path as package name
            packages.add(parts[0])
    
    return packages

def read_requirements_file(file_path):
    """Read and parse a requirements file."""
    if not os.path.exists(file_path):
        return set()
    
    packages = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('-r'):
                continue
            # Extract package name (without version specifications)
            package_name = re.split(r'[=<>~]', line)[0].strip()
            packages.add(package_name)
    
    return packages

def add_missing_package(requirements_file, package, version=">=1.0.0"):
    """Add a missing package to a requirements file."""
    with open(requirements_file, 'a', encoding='utf-8') as f:
        f.write(f"\n# Added automatically by dependency scanner\n{package}{version}\n")
    print(f"Added {package} to {requirements_file}")

def main():
    # Get base directory (project root)
    try:
        # When run directly
        base_dir = Path(__file__).resolve().parent.parent
    except NameError:
        # When executed with exec()
        import os
        base_dir = Path(os.getcwd())
    
    # Find all settings files
    settings_files = find_settings_files(base_dir)
    
    # Collect all required packages from imports and backends
    required_packages = set()
    for file_path in settings_files:
        imports = scan_file_for_imports(file_path)
        backends = scan_settings_for_backends(file_path)
        required_packages.update(imports)
        required_packages.update(backends)
    
    # Filter out standard library modules
    try:
        import stdlib_list
        std_libs = stdlib_list.stdlib_list()
        required_packages = {pkg for pkg in required_packages if pkg not in std_libs}
    except ImportError:
        # If stdlib_list is not available, use a simpler approach
        std_libs = {'os', 'sys', 'datetime', 're', 'json', 'math', 'random', 'time', 
                   'collections', 'pathlib', 'typing', 'itertools'}
        required_packages = {pkg for pkg in required_packages if pkg not in std_libs}
    
    # Read current requirements
    requirements_base = os.path.join(base_dir, 'requirements', 'base.in')
    current_packages = read_requirements_file(requirements_base)
    
    # Specific Django package mappings (module name -> package name)
    package_mappings = {
        'rest_framework': 'djangorestframework',
        'allauth': 'django-allauth',
        'corsheaders': 'django-cors-headers',
        'celery': 'celery',
        'redis': 'redis',
        'storages': 'django-storages',
        'django_redis': 'django-redis',
    }
    
    # Check for missing packages
    missing_packages = []
    for package in required_packages:
        # Skip Django itself
        if package == 'django':
            continue
            
        # Check if the package or its mapping is already in requirements
        mapped_package = package_mappings.get(package, package)
        if mapped_package.lower() not in {p.lower() for p in current_packages}:
            missing_packages.append(mapped_package)
    
    # Report missing packages
    if missing_packages:
        print("Missing packages detected:")
        for package in sorted(missing_packages):
            print(f" - {package}")
        
        if input("Add missing packages to requirements/base.in? (y/n): ").lower() == 'y':
            for package in missing_packages:
                add_missing_package(requirements_base, package)
            print("Dependencies updated successfully!")
        else:
            print("No changes made to requirements files.")
    else:
        print("All dependencies are properly included in requirements files!")

if __name__ == "__main__":
    main() 