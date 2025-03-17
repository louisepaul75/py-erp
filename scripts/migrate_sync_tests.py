#!/usr/bin/env python
"""
Script to migrate sync tests from the old location to the new standardized
location.

This script helps convert unittest-based sync tests to pytest format and
moves them to the standardized location in tests/backend/sync/.
"""
import os
import re
from pathlib import Path


def ensure_directory_exists(directory):
    """Ensure the directory exists, creating it if necessary."""
    os.makedirs(directory, exist_ok=True)


def convert_unittest_to_pytest(content):
    """Convert unittest-style tests to pytest-style tests."""
    # Replace imports
    content = re.sub(
        r'import unittest\n',
        'import pytest\n',
        content
    )
    
    # Replace class definition with module docstring
    content = re.sub(
        r'class TestSync\w+\(unittest\.TestCase\):\n\s+"""(.*?)"""',
        '"""\n\\1\n"""',
        content
    )
    
    # Replace self.assertEqual with assert
    content = re.sub(
        r'self\.assertEqual\((.*?), (.*?)\)',
        r'assert \1 == \2',
        content
    )
    
    # Replace self.assertTrue with assert
    content = re.sub(
        r'self\.assertTrue\((.*?)\)',
        r'assert \1',
        content
    )
    
    # Replace self.assertFalse with assert not
    content = re.sub(
        r'self\.assertFalse\((.*?)\)',
        r'assert not \1',
        content
    )
    
    # Replace self.assertIn with assert in
    content = re.sub(
        r'self\.assertIn\((.*?), (.*?)\)',
        r'assert \1 in \2',
        content
    )
    
    # Replace self.assertRaises with pytest.raises
    content = re.sub(
        r'with self\.assertRaises\((.*?)\):',
        r'with pytest.raises(\1):',
        content
    )
    
    # Replace setUp method with fixtures
    content = re.sub(
        r'def setUp\(self\):(.*?)def ',
        lambda match: convert_setup_to_fixtures(match.group(1)) + 'def ',
        content,
        flags=re.DOTALL
    )
    
    # Replace test methods
    content = re.sub(
        r'def (test_\w+)\(self\):',
        r'def \1():',
        content
    )
    
    # Replace self references
    content = re.sub(
        r'self\.(\w+)',
        r'\1',
        content
    )
    
    return content


def convert_setup_to_fixtures(setup_content):
    """Convert setUp method content to pytest fixtures."""
    fixtures = []
    
    # Extract variable assignments
    assignments = re.findall(
        r'self\.(\w+) = (.*?)$', 
        setup_content, 
        re.MULTILINE
    )
    
    for var_name, value in assignments:
        fixture_content = f"""
@pytest.fixture
def {var_name}():
    \"\"\"Fixture for {var_name}.\"\"\"
    return {value}
"""
        fixtures.append(fixture_content)
    
    return ''.join(fixtures)


def migrate_test_file(source_path, target_path):
    """Migrate a test file from source to target path, converting to pytest format."""
    print(f"Migrating {source_path} to {target_path}")
    
    # Read the source file
    with open(source_path, 'r') as f:
        content = f.read()
    
    # Convert to pytest format
    content = convert_unittest_to_pytest(content)
    
    # Write to the target file
    with open(target_path, 'w') as f:
        f.write(content)


def main():
    """Main function to migrate sync tests."""
    # Define source and target directories
    source_dir = Path('pyerp/sync/tests')
    target_dir = Path('tests/backend/sync')
    
    # Ensure target directory exists
    ensure_directory_exists(target_dir)
    
    # Get list of test files to migrate
    test_files = [
        f for f in source_dir.glob('test_*.py') 
        if f.name != 'test_settings.py'
    ]
    
    # Migrate each test file
    for source_file in test_files:
        target_file = target_dir / source_file.name
        migrate_test_file(source_file, target_file)
    
    msg = f"Migration complete. {len(test_files)} files migrated."
    print(msg)
    print("Please review the migrated files and make any necessary adjustments.")
    print("Remember to update imports and fix any issues with the automated conversion.")


if __name__ == '__main__':
    main() 