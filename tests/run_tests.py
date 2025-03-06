#!/usr/bin/env python
"""
Test runner script for pyERP.

This script provides a convenient way to run tests for the pyERP project.
It supports running specific test modules or all tests, and can generate
coverage reports.
"""

import argparse
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
    return parser.parse_args()


def run_tests(args):
    """Run the tests with the specified arguments."""
    # Build the pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add coverage options if requested
    if args.coverage:
        cmd.extend(["--cov=pyerp"])

        # Add coverage report formats
        if args.html:
            cmd.append(f"--cov-report=html:{args.output_dir}")
        else:
            cmd.append("--cov-report=html")

        if args.xml:
            cmd.append("--cov-report=xml")

        cmd.append("--cov-report=term")

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add test paths
    cmd.extend(args.test_paths)

    # Print the command being run
    print("Running command:", " ".join(cmd))
    print("=" * 80)

    # Run the tests
    result = subprocess.run(cmd, check=False)

    # Print a summary
    print("=" * 80)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code {result.returncode}")

    # Print coverage report location
    if args.coverage:
        print("\nCoverage report generated in htmlcov/ directory")
        print("Open htmlcov/index.html in a browser to view the report")

        # Parse and display coverage summary
        try:
            # Try to extract the coverage percentage from the output
            coverage_file = Path(".coverage")
            if coverage_file.exists():
                # Use coverage module to get a summary
                summary_cmd = [
                    sys.executable,
                    "-m",
                    "coverage",
                    "report",
                    "--include=pyerp/*",
                    "--omit=*/migrations/*,*/tests/*",
                    "--format=text",
                    "--skip-empty",
                ]
                print("\nCoverage Summary:")
                print("-" * 40)
                subprocess.run(summary_cmd, check=False)
                print("-" * 40)
        except Exception as e:
            print(f"Could not generate coverage summary: {e}")

    return result.returncode


def main():
    """Main entry point."""
    args = parse_args()
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
