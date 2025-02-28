#!/usr/bin/env python
"""
Test each dependency from a requirements file individually
to identify which one is causing installation problems.
"""

import os
import sys
import subprocess
import tempfile

def parse_requirements(file_path):
    """Parse a requirements file and extract package specifications."""
    packages = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('-r '):
                continue
            packages.append(line)
    return packages

def test_package(package):
    """Test if a package can be processed by pip-compile."""
    with tempfile.NamedTemporaryFile('w', suffix='.in', delete=False) as temp:
        temp.write(package + '\n')
        temp_path = temp.name
    
    try:
        print(f"\n\nTesting package: {package}")
        result = subprocess.run(
            ['pip-compile', '--verbose', temp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"ERROR with {package}:")
            print(result.stderr)
            return False
        
        print(f"SUCCESS with {package}")
        return True
    finally:
        os.unlink(temp_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_deps.py <requirements_file>")
        sys.exit(1)
    
    req_file = sys.argv[1]
    packages = parse_requirements(req_file)
    
    print(f"Testing {len(packages)} packages from {req_file}")
    
    failures = []
    for package in packages:
        if not test_package(package):
            failures.append(package)
    
    if failures:
        print("\n\nThe following packages failed:")
        for package in failures:
            print(f"  - {package}")
        sys.exit(1)
    else:
        print("\n\nAll packages passed!")

if __name__ == "__main__":
    main() 