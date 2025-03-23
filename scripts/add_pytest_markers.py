#!/usr/bin/env python
"""
Script to add pytest markers to test files.

This script traverses through the project directory and adds appropriate pytest markers
to test files based on their location.
"""
import os
import re
import sys


MARKER_MAPPING = {
    'core': 'core',
    'api': 'api',
    'database': 'database',
    'ui': 'ui',
    'unit': 'unit',
    'backend': 'backend',
}


def get_marker_for_file(file_path):
    """Determine the appropriate marker for a test file based on its path."""
    for marker_key, marker_name in MARKER_MAPPING.items():
        if f'/{marker_key}/' in file_path or file_path.startswith(f'{marker_key}/'):
            return marker_name
    
    # Default to unit tests if no specific category is found
    return 'unit'


def add_marker_to_test_file(file_path, marker_name):
    """Add a pytest marker to a test file if it doesn't already have it."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {file_path}")
        return False

    # Skip if the file already has this marker
    marker_pattern = rf'@pytest\.mark\.{marker_name}'
    if re.search(marker_pattern, content):
        print(f"Skipping: {file_path} already has marker @pytest.mark.{marker_name}")
        return False

    # Check if the file imports pytest
    if 'import pytest' not in content:
        content = re.sub(
            r'(import .*?\n)',
            r'\1import pytest\n',
            content, 
            count=1
        )
    
    # Find classes and add markers where appropriate
    # We'll add markers to TestCase classes or classes starting with 'Test'
    class_pattern = r'class\s+(Test[^\s(:]*)\s*(?:\([^)]*\))?:'
    
    # Find functions starting with test_ that are not inside a class
    standalone_test_pattern = r'^def\s+(test_[^\s(:]*).*:'
    
    # Add markers to classes
    modified_content = re.sub(
        class_pattern,
        f'@pytest.mark.{marker_name}\nclass \\1:',
        content,
        flags=re.MULTILINE
    )
    
    # Add markers to standalone test functions
    modified_content = re.sub(
        standalone_test_pattern,
        f'@pytest.mark.{marker_name}\ndef \\1:',
        modified_content,
        flags=re.MULTILINE
    )
    
    # Check if content was modified
    if content == modified_content:
        print(f"No changes needed for {file_path}")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"Added marker @pytest.mark.{marker_name} to {file_path}")
    return True


def process_directory(directory):
    """Process all test files in a directory and its subdirectories."""
    num_files_modified = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                file_path = os.path.join(root, file)
                marker_name = get_marker_for_file(file_path)
                if add_marker_to_test_file(file_path, marker_name):
                    num_files_modified += 1
    
    return num_files_modified


def main():
    """Main function to add pytest markers to test files."""
    if len(sys.argv) > 1:
        directories = sys.argv[1:]
    else:
        # Default directories to process
        directories = [
            'pyerp',
            'tests'
        ]
    
    total_files_modified = 0
    for directory in directories:
        if os.path.exists(directory):
            print(f"Processing {directory}...")
            num_files_modified = process_directory(directory)
            total_files_modified += num_files_modified
            print(f"Modified {num_files_modified} files in {directory}")
        else:
            print(f"Directory {directory} does not exist, skipping.")
    
    print(f"Total files modified: {total_files_modified}")


if __name__ == '__main__':
    main() 