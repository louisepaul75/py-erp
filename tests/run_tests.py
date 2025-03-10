#!/usr/bin/env python
"""
Test runner script for pyERP.

This script provides a convenient way to run tests for the pyERP project.
It supports running specific test modules or all tests, and can generate
coverage reports.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run tests for pyERP"
    )
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
    return parser.parse_args()


def get_test_categories():
    """Return a list of test categories based on directory structure."""
    test_dir = Path("tests")
    categories = [
        d.name 
        for d in test_dir.iterdir() 
        if (d.is_dir() and 
            not d.name.startswith((".", "__")))
    ]
    return sorted(categories)


def run_category_tests(category, args, cmd_base):
    """Run tests for a specific category and return results."""
    category_path = f"tests/{category}"
    if not Path(category_path).exists():
        return None

    # Build category-specific command
    cmd = cmd_base.copy()
    cmd.extend([
        category_path,
        "--json-report",
        f"--json-report-file=tests/coverage/{category}-results.json",
    ])

    # Run tests for this category
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    
    try:
        # Try to read the JSON results
        with open(f"tests/coverage/{category}-results.json") as f:
            json_results = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        json_results = None

    return {
        "returncode": result.returncode,
        "output": result.stdout,
        "json_results": json_results,
    }


def get_coverage_for_category(category):
    """Get coverage information for a specific category."""
    try:
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "report",
            "--include=pyerp/*",
            f"--include=scripts/{category}/*",
            "--omit=*/migrations/*,*/tests/*",
            "--format=json",
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
        coverage_data = json.loads(result.stdout)
        return coverage_data.get("totals", {}).get("percent_covered", 0)
    except (json.JSONDecodeError, subprocess.SubprocessError):
        return 0


def print_category_summary(category, results, coverage):
    """Print a summary for a specific test category."""
    if not results or not results.get("json_results"):
        print(f"\n{category.upper()} Tests: No results available")
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
                error_msg = test.get("call", {}).get(
                    "longrepr", "No details available"
                )
                print(f"  - {test_id}: {error_msg}")


def run_tests(args):
    """Run the tests with the specified arguments."""
    # Create coverage directory if it doesn't exist
    Path("tests/coverage").mkdir(parents=True, exist_ok=True)

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

    # Get test categories
    categories = get_test_categories()
    
    # Store results for each category
    category_results = {}
    overall_passed = True

    print("Running pyERP Test Suite")
    print("=" * 80)

    # Run tests for each category
    for category in categories:
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
            check=False
        )

    status = "✅ PASSED" if overall_passed else "❌ FAILED"
    print("\nTest Execution Status:", status)

    if args.coverage:
        print(
            f"\nDetailed coverage report available at: "
            f"{args.output_dir}/index.html"
        )

    return 0 if overall_passed else 1


def main():
    """Main entry point."""
    args = parse_args()
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
