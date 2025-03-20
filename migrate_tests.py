#!/usr/bin/env python
"""
Test Migration Script for PyERP

This script automates the migration of tests from the centralized tests/ directory
to co-located tests in each Django app/module directory.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Migrate tests from centralized to co-located structure"
    )
    parser.add_argument(
        "--module",
        help="Specific module to migrate (default: all modules)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    return parser.parse_args()


def get_modules():
    """Get a list of all PyERP modules."""
    pyerp_dir = Path("pyerp")
    modules = []
    
    # Add main directories 
    for item in pyerp_dir.iterdir():
        if item.is_dir() and not item.name.startswith(("__", ".")):
            # Skip non-module directories
            if item.name in ("templates", "staticfiles", "static", "logs", "locale"):
                continue
            modules.append(item.name)
            
    # Also check business_modules if it exists
    business_modules_dir = pyerp_dir / "business_modules"
    if business_modules_dir.exists() and business_modules_dir.is_dir():
        for item in business_modules_dir.iterdir():
            if item.is_dir() and not item.name.startswith(("__", ".")):
                modules.append(f"business_modules/{item.name}")
    
    return sorted(modules)


def create_module_test_dir(module, dry_run=False, verbose=False):
    """Create a tests directory for a module if it doesn't exist."""
    if "/" in module:
        # Handle business module case
        parent, child = module.split("/")
        test_dir = Path(f"pyerp/{parent}/{child}/tests")
    else:
        test_dir = Path(f"pyerp/{module}/tests")
    
    if test_dir.exists():
        if verbose:
            print(f"Test directory already exists: {test_dir}")
        return test_dir, False
    
    if not dry_run:
        test_dir.mkdir(parents=True, exist_ok=True)
        # Create __init__.py
        init_path = test_dir / "__init__.py"
        with open(init_path, "w") as f:
            f.write('"""Tests for the {} module."""\n'.format(module.replace("/", ".")))
    
    if verbose:
        print(f"Created test directory: {test_dir}")
    
    return test_dir, True


def find_module_tests(module):
    """Find tests for a specific module in the centralized test directory."""
    tests_dir = Path("tests")
    module_tests = []
    
    # Match module name to directory name (handle business modules)
    if "/" in module:
        parent, child = module.split("/")
        module_name = child
    else:
        module_name = module
    
    # Check unit tests for module-specific tests
    unit_dir = tests_dir / "unit" / module_name
    if unit_dir.exists() and unit_dir.is_dir():
        for test_file in unit_dir.glob("test_*.py"):
            module_tests.append((test_file, f"unit/{module_name}/{test_file.name}"))
    
    # Check other test categories
    for category in ["api", "core", "backend"]:
        category_dir = tests_dir / category
        if category_dir.exists() and category_dir.is_dir():
            # Look for module-specific tests in the category
            for test_file in category_dir.glob(f"test_{module_name}_*.py"):
                module_tests.append((test_file, f"{category}/{test_file.name}"))
            
            # Check subdirectories with module name
            module_category_dir = category_dir / module_name
            if module_category_dir.exists() and module_category_dir.is_dir():
                for test_file in module_category_dir.glob("test_*.py"):
                    module_tests.append((test_file, f"{category}/{module_name}/{test_file.name}"))
    
    # Look for direct module tests in the unit tests directory
    unit_tests_dir = tests_dir / "unit"
    for test_file in unit_tests_dir.glob(f"test_{module_name}_*.py"):
        module_tests.append((test_file, f"unit/{test_file.name}"))
    
    return module_tests


def update_imports(content, module):
    """Update imports in test files to work with the new location."""
    # Update relative imports
    # From: from tests.unit.core import ...
    # To: from pyerp.core.tests import ...
    
    if "/" in module:
        parent, child = module.split("/")
        module_path = f"pyerp.{parent}.{child}"
    else:
        module_path = f"pyerp.{module}"
    
    # Update imports from tests directory
    content = re.sub(
        r'from tests\.(unit|api|core|backend)\.{}\b'.format(module.replace("/", ".")), 
        f'from {module_path}.tests', 
        content
    )
    
    # Update imports from other test modules
    content = re.sub(
        r'from tests\.(unit|api|core|backend)(?:\.\w+)?\b', 
        r'from pyerp.\1.tests', 
        content
    )
    
    # Replace conftest imports
    content = re.sub(
        r'from tests\.conftest\b', 
        'from conftest',  # We'll copy the global conftest to the project root
        content
    )
    
    return content


def copy_conftest_files(module, dry_run=False, verbose=False):
    """Copy and adapt conftest files for the module."""
    if "/" in module:
        parent, child = module.split("/")
        module_test_dir = Path(f"pyerp/{parent}/{child}/tests")
    else:
        module_test_dir = Path(f"pyerp/{module}/tests")
        
    # Check if there's a module-specific conftest in the centralized tests
    unit_module_dir = Path(f"tests/unit/{module.split('/')[-1]}")
    conftest_source = None
    
    if unit_module_dir.exists():
        unit_conftest = unit_module_dir / "conftest.py"
        if unit_conftest.exists():
            conftest_source = unit_conftest
    
    if conftest_source is None:
        # Use general unit conftest
        conftest_source = Path("tests/unit/conftest.py")
        if not conftest_source.exists():
            if verbose:
                print(f"No conftest.py found for module {module}")
            return
    
    target_conftest = module_test_dir / "conftest.py"
    
    if target_conftest.exists() and not args.force:
        if verbose:
            print(f"Conftest already exists for {module}, skipping")
        return
    
    if verbose:
        print(f"Copying conftest from {conftest_source} to {target_conftest}")
    
    if not dry_run:
        with open(conftest_source, "r") as src_file:
            content = src_file.read()
        
        # Update imports
        content = update_imports(content, module)
        
        # Add module-specific docstring
        content = re.sub(
            r'""".*?"""',
            f'"""Pytest configuration and fixtures for the {module} module tests."""',
            content,
            count=1,
            flags=re.DOTALL,
        )
        
        with open(target_conftest, "w") as dst_file:
            dst_file.write(content)


def migrate_test_file(test_file, rel_path, module, args):
    """Migrate a single test file to the new location."""
    if "/" in module:
        parent, child = module.split("/")
        target_dir = Path(f"pyerp/{parent}/{child}/tests")
    else:
        target_dir = Path(f"pyerp/{module}/tests")
    
    # Create subdirectory if needed
    rel_dir = os.path.dirname(rel_path)
    if rel_dir and rel_dir != "unit":
        category = rel_dir.split("/")[0]
        if category != module.split("/")[-1]:  # Don't create duplicate directory
            sub_dir = target_dir / category
            if not sub_dir.exists() and not args.dry_run:
                sub_dir.mkdir(parents=True, exist_ok=True)
                # Create __init__.py
                with open(sub_dir / "__init__.py", "w") as f:
                    f.write('"""Tests for the {} module {}."""\n'.format(module.replace("/", "."), category))
    
    # Determine target file
    if rel_dir.endswith(module.split("/")[-1]) and rel_dir != module.split("/")[-1]:
        # If the file is already in a subdirectory with the module name, avoid duplication
        target_file = target_dir / test_file.name
    else:
        category = rel_dir.split("/")[0] if rel_dir else ""
        if category not in ["unit", module.split("/")[-1]] and category:
            target_file = target_dir / category / test_file.name
        else:
            target_file = target_dir / test_file.name
    
    if target_file.exists() and not args.force:
        if args.verbose:
            print(f"Target file exists, skipping: {target_file}")
        return False
    
    if args.verbose:
        print(f"Migrating {test_file} to {target_file}")
    
    if not args.dry_run:
        # Make parent directory if it doesn't exist
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py in subdirectories
        if target_file.parent != target_dir:
            init_file = target_file.parent / "__init__.py"
            if not init_file.exists():
                with open(init_file, "w") as f:
                    f.write('"""Tests for the {} module."""\n'.format(module.replace("/", ".")))
        
        # Read and update the test file content
        with open(test_file, "r") as src_file:
            content = src_file.read()
        
        # Update imports
        content = update_imports(content, module)
        
        # Write updated file
        with open(target_file, "w") as dst_file:
            dst_file.write(content)
    
    return True


def copy_global_conftest(dry_run=False, verbose=False):
    """Copy the global conftest.py to the project root."""
    source = Path("tests/conftest.py")
    target = Path("conftest.py")
    
    if target.exists() and not args.force:
        if verbose:
            print("Global conftest.py already exists in project root, skipping")
        return
    
    if verbose:
        print("Copying global conftest.py to project root")
    
    if not dry_run:
        shutil.copy2(source, target)


def update_pytest_ini(dry_run=False, verbose=False):
    """Update pytest.ini to recognize the new test locations."""
    ini_path = Path("pytest.ini")
    
    if not ini_path.exists():
        if verbose:
            print("pytest.ini not found, skipping update")
        return
    
    if verbose:
        print("Updating pytest.ini")
    
    if not dry_run:
        with open(ini_path, "r") as f:
            content = f.read()
        
        # Update testpaths to include both old and new locations during migration
        if "testpaths = " in content:
            content = re.sub(
                r"testpaths = .*",
                "testpaths = . pyerp tests",
                content
            )
        else:
            # Add testpaths if it doesn't exist
            content = re.sub(
                r"\[pytest\]",
                "[pytest]\ntestpaths = . pyerp tests",
                content
            )
        
        with open(ini_path, "w") as f:
            f.write(content)


def migrate_module_tests(module, args):
    """Migrate all tests for a specific module."""
    if args.verbose:
        print(f"\nMigrating tests for module: {module}")
    
    # Create module test directory
    test_dir, created = create_module_test_dir(module, args.dry_run, args.verbose)
    
    # Find tests for the module
    module_tests = find_module_tests(module)
    
    if not module_tests:
        if args.verbose:
            print(f"No tests found for module {module}")
        return 0
    
    if args.verbose:
        print(f"Found {len(module_tests)} test files for {module}")
    
    # Copy conftest.py if it exists
    copy_conftest_files(module, args.dry_run, args.verbose)
    
    # Migrate each test file
    migrated_count = 0
    for test_file, rel_path in module_tests:
        if migrate_test_file(test_file, rel_path, module, args):
            migrated_count += 1
    
    if args.verbose:
        print(f"Migrated {migrated_count} test files for {module}")
    
    return migrated_count


def main():
    """Main function to orchestrate the migration."""
    global args
    args = parse_args()
    
    print("PyERP Test Migration Tool")
    print("=========================")
    
    # Get modules to migrate
    if args.module:
        modules = [args.module]
    else:
        modules = get_modules()
    
    if args.dry_run:
        print("*** DRY RUN MODE - No files will be changed ***")
    
    print(f"Found {len(modules)} modules to process")
    
    # Copy global conftest.py
    copy_global_conftest(args.dry_run, args.verbose)
    
    # Update pytest.ini
    update_pytest_ini(args.dry_run, args.verbose)
    
    # Migrate tests for each module
    total_migrated = 0
    for module in modules:
        migrated = migrate_module_tests(module, args)
        total_migrated += migrated
    
    print(f"\nMigration complete. Migrated {total_migrated} test files across {len(modules)} modules.")
    
    if not args.dry_run:
        print("\nNext steps:")
        print("1. Run tests to verify functionality")
        print("2. Update CI/CD configurations")
        print("3. Once all tests pass, you can remove the old tests/ directory")
    

if __name__ == "__main__":
    main() 