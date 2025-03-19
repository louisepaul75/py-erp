#!/usr/bin/env python
"""
Test runner script for pyERP.

This script provides a convenient way to run tests for the pyERP project.
It supports running specific test modules or all tests, and can generate
coverage reports.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for pyERP")
    parser.add_argument(
        "test_paths",
        nargs="*",
        default=["tests/"],
        help="Paths to test files or directories",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report",
    )
    parser.add_argument(
        "--xml",
        action="store_true",
        help="Generate XML coverage report",
    )
    parser.add_argument(
        "--output-dir",
        default="htmlcov",
        help="Directory for coverage reports",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Generate JSON report for test results",
    )
    parser.add_argument(
        "--skip-celery",
        action="store_true",
        help="Skip Celery imports to avoid circular import issues",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show more detailed debug output",
    )
    return parser.parse_args()


def setup_env(skip_celery=False):
    """Set up the test environment."""
    # Configure Django settings before running tests
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.test")
    
    # Skip Celery import if needed (to avoid circular imports)
    if skip_celery:
        os.environ.setdefault("SKIP_CELERY_IMPORT", "1")
        
    # Set PYTEST_RUNNING flag
    os.environ.setdefault("PYTEST_RUNNING", "1")
    
    # Add project root to Python path if needed
    project_root = Path(__file__).parent.parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def get_test_categories():
    """Return a list of test categories based on directory structure."""
    test_dir = Path("tests").absolute()
    
    # Get top-level categories
    top_categories = [
        d.name
        for d in test_dir.iterdir()
        if (d.is_dir() and not d.name.startswith((".", "__", "coverage", "htmlcov", "logs", ".pytest_cache")))
    ]
    
    # Also check for subcategories in unit tests
    subcategories = []
    if "unit" in top_categories:
        unit_dir = test_dir / "unit"
        for d in unit_dir.iterdir():
            if d.is_dir() and not d.name.startswith((".", "__")):
                subcategories.append(f"unit/{d.name}")
    
    return sorted(top_categories + subcategories)


def print_test_files(category_path):
    """List all python test files in the given path."""
    path = Path(category_path)
    test_files = []
    
    if path.is_dir():
        for file in path.glob("**/*.py"):
            if file.name.startswith("test_") or file.name.endswith("_test.py"):
                test_files.append(str(file))
    
    return test_files


def run_direct_pytest(category_path, args):
    """Run pytest directly to test a specific path."""
    # Build command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test path
    cmd.append(category_path)
    
    # Add verbosity
    cmd.append("-v")
    
    # Add Django settings
    cmd.append("--ds=pyerp.config.settings.test")
    
    # Add coverage options if requested
    if args.coverage:
        cmd.extend(["--cov=pyerp", "--cov-report=term"])
    
    print(f"Running direct pytest command: {' '.join(cmd)}")
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    # Print output
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    
    return result.returncode == 0


def run_category_tests(category, args, cmd_base):
    """Run tests for a specific category and return results."""
    category_path = f"tests/{category}"
    if not Path(category_path).exists():
        print(f"Path {category_path} does not exist")
        return None

    # Print test files for debugging
    if args.debug:
        print(f"Test files in {category_path}:")
        test_files = print_test_files(category_path)
        for tf in test_files:
            print(f"  - {tf}")
        print(f"Found {len(test_files)} test files")

    # Create category-specific results directory if needed
    Path("tests/coverage").mkdir(parents=True, exist_ok=True)
    
    # Build category-specific command
    cmd = cmd_base.copy()
    cmd.extend(
        [
            category_path,
            "--json-report",
            f"--json-report-file=tests/coverage/{category.replace('/', '-')}-results.json",
        ]
    )
    
    # Print the command being executed for debugging
    print(f"Running command: {' '.join(cmd)}")

    # Run tests for this category
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    if args.debug and result.returncode != 0:
        print("Command failed with the following output:")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        
        # Try direct pytest for more info
        print("Trying direct pytest command for more info...")
        run_direct_pytest(category_path, args)

    try:
        # Try to read the JSON results
        with open(f"tests/coverage/{category.replace('/', '-')}-results.json") as f:
            json_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON results: {e}")
        json_results = None

    return {
        "returncode": result.returncode,
        "output": result.stdout,
        "error": result.stderr,
        "json_results": json_results,
    }


def get_coverage_for_category(category):
    """Get coverage information for a specific category."""
    try:
        if '/' in category:
            # For subcategories like unit/core, include all files in that directory
            main_category, subcategory = category.split('/')
            include_pattern = f"pyerp/{subcategory}/*"
        else:
            # For top-level categories
            include_pattern = f"pyerp/{category}/*"
        
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "report",
            f"--include={include_pattern}",
            "--omit=*/migrations/*,*/tests/*,*/__pycache__/*",
            "--format=json",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        try:
            coverage_data = json.loads(result.stdout)
            return coverage_data.get("totals", {}).get("percent_covered", 0)
        except json.JSONDecodeError:
            # Fall back to parsing the percentage from the text output
            for line in result.stdout.splitlines():
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            return float(parts[-1].rstrip('%'))
                        except ValueError:
                            pass
            return 0
    except subprocess.SubprocessError:
        return 0


def print_category_summary(category, results, coverage):
    """Print a summary for a specific test category."""
    if not results or not results.get("json_results"):
        print(f"\n{category.upper()} Tests: No results available")
        if results:
            print("Command exit code:", results.get("returncode"))
            if results.get("error"):
                print("Error output:")
                print(results.get("error"))
        return

    json_results = results["json_results"]
    tests_total = json_results.get("summary", {}).get("total", 0)
    tests_passed = json_results.get("summary", {}).get("passed", 0)
    tests_failed = json_results.get("summary", {}).get("failed", 0)
    tests_skipped = json_results.get("summary", {}).get("skipped", 0)

    print(f"\n{category.upper()} Tests:")
    print("-" * 40)
    print(f"Total Tests: {tests_total}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"⚠️ Skipped: {tests_skipped}")
    print(f"📊 Coverage: {coverage:.1f}%")

    # Print failed test details if any
    if tests_failed > 0 and "tests" in json_results:
        print("\nFailed Tests:")
        for test in json_results["tests"]:
            if test.get("outcome") == "failed":
                test_id = test.get("nodeid", "Unknown test")
                error_msg = test.get("call", {}).get("longrepr", "No details available")
                print(f"  - {test_id}: {error_msg}")


def run_tests(args):
    """Run the tests with the specified arguments."""
    # Set up the environment
    setup_env(skip_celery=args.skip_celery)
    
    # Create coverage directory if it doesn't exist
    Path("tests/coverage").mkdir(parents=True, exist_ok=True)

    # Print python and pytest versions for debugging
    if args.debug:
        subprocess.run([sys.executable, "--version"], check=False)
        subprocess.run([sys.executable, "-m", "pytest", "--version"], check=False)
        print(f"Python path: {sys.path}")
        print(f"Working directory: {Path.cwd()}")

    # Build the base pytest command
    cmd_base = [sys.executable, "-m", "pytest"]

    # Add coverage options if requested
    if args.coverage:
        cmd_base.extend(["--cov=pyerp", "--cov=scripts"])

        # Add coverage report formats
        if args.html:
            cmd_base.append(f"--cov-report=html:{args.output_dir}")
        if args.xml:
            cmd_base.append("--cov-report=xml")
        cmd_base.append("--cov-report=term")

    # Add verbosity
    if args.verbose:
        cmd_base.append("-v")
        
    # Always collect test output
    cmd_base.append("-v")
        
    # Add the Django settings module explicitly
    cmd_base.extend(["--ds=pyerp.config.settings.test"])

    # Get test categories - if specific paths were provided, use those
    if args.test_paths and args.test_paths != ["tests/"]:
        categories = args.test_paths
    else:
        categories = get_test_categories()
        
    if args.debug:
        print(f"Categories to test: {categories}")

    # Store results for each category
    category_results = {}
    overall_passed = True

    print("Running pyERP Test Suite")
    print("=" * 80)

    # Run tests for each category
    for category in categories:
        print(f"\nRunning tests for {category}...")
        results = run_category_tests(category, args, cmd_base)
        if results:
            category_results[category] = results
            if results["returncode"] != 0:
                overall_passed = False

    # Print comprehensive summary
    print("\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)

    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for category in categories:
        if category in category_results:
            results = category_results[category]
            coverage = get_coverage_for_category(category)
            print_category_summary(category, results, coverage)

            if results.get("json_results"):
                summary = results["json_results"].get("summary", {})
                total_tests += summary.get("total", 0)
                total_passed += summary.get("passed", 0)
                total_failed += summary.get("failed", 0)
                total_skipped += summary.get("skipped", 0)

    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"Total Test Cases: {total_tests}")
    print(f"✅ Total Passed: {total_passed}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"⚠️ Total Skipped: {total_skipped}")

    if args.coverage:
        print("\nOverall Coverage Report:")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "coverage",
                "report",
                "--include=pyerp/*,scripts/*",
                "--omit=*/migrations/*,*/tests/*",
            ],
            check=False,
        )

    status = "✅ PASSED" if overall_passed else "❌ FAILED"
    print("\nTest Execution Status:", status)

    if args.coverage and args.html:
        print(
            f"\nDetailed coverage report available at: {args.output_dir}/index.html"
        )

    return 0 if overall_passed else 1


def main():
    """Main entry point."""
    args = parse_args()
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
