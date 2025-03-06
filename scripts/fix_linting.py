#!/usr/bin/env python
"""
Script to automatically fix linting issues in Python files using Ruff.

This script leverages Ruff to automatically fix
common linting issues in Python files.
It replaces the previous manual fixes
with Ruff's automated fixing capabilities.

Benefits:
- Uses the same configuration as defined in pyproject.toml
- More consistent with the pre-commit workflow
- Faster and more reliable than manual regex-based fixes
- Handles a wider range of linting issues
"""

import argparse
import glob
import os
import subprocess
import sys


def find_python_files(directory: str = "pyerp") -> list[str]:
    """Find all Python files in the given directory.

    Args:
        directory: Directory to search for Python files

    Returns:
        List of paths to Python files found in the directory
    """
    return glob.glob(f"{directory}/**/*.py", recursive=True)


def run_ruff_check(files: list[str], *, enable_verbose: bool = False) -> None:
    """Run Ruff check on the specified files.

    Args:
        files: List of Python files to check
        enable_verbose: Whether to enable verbose output

    Returns:
        None
    """
    if not files:
        print("No Python files found to check.")
        return

    print(f"Running Ruff check on {len(files)} files...")

    # Build the command
    cmd = ["ruff", "check"]
    if enable_verbose:
        cmd.append("--verbose")
    cmd.extend(files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("Ruff found issues:")
            print(result.stdout)
        else:
            print("No issues found by Ruff check.")

    except Exception as e:
        print(f"Error running Ruff check: {e}")


def run_ruff_fix(files: list[str], *, enable_verbose: bool = False) -> None:
    """Run Ruff fix on the specified files.

    Args:
        files: List of Python files to fix
        enable_verbose: Whether to enable verbose output

    Returns:
        None
    """
    if not files:
        print("No Python files found to fix.")
        return

    print(f"Running Ruff fix on {len(files)} files...")

    # Build the command
    cmd = ["ruff", "check", "--fix"]
    if enable_verbose:
        cmd.append("--verbose")
    cmd.extend(files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("Ruff fix completed with some remaining issues:")
            print(result.stdout)
        else:
            print("Ruff fix completed successfully.")

    except Exception as e:
        print(f"Error running Ruff fix: {e}")


def run_ruff_format(files: list[str], *, enable_verbose: bool = False) -> None:
    """Run Ruff format on the specified files.

    Args:
        files: List of Python files to format
        enable_verbose: Whether to enable verbose output

    Returns:
        None
    """
    if not files:
        print("No Python files found to format.")
        return

    print(f"Running Ruff format on {len(files)} files...")

    # Build the command
    cmd = ["ruff", "format"]
    if enable_verbose:
        cmd.append("--verbose")
    cmd.extend(files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("Ruff format completed with some issues:")
            print(result.stdout)
        else:
            print("Ruff format completed successfully.")

    except Exception as e:
        print(f"Error running Ruff format: {e}")


def ensure_ruff_installed() -> bool:
    """Ensure Ruff is installed, and install it if not.

    Returns:
        bool: True if Ruff is installed or was successfully installed,
            False if installation failed
    """
    try:
        subprocess.run(
            ["ruff", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Ruff not found. Attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "ruff"],
                check=True,
            )
            print("Ruff installed successfully.")
            return True
        except subprocess.SubprocessError as e:
            print(f"Failed to install Ruff: {e}")
            return False


def main() -> None:
    """Main function to process all Python files.

    This function handles command line arguments and orchestrates the linting
    process:
    1. Ensures Ruff is installed
    2. Finds Python files to process
    3. Runs Ruff check, fix, and format operations based on arguments
    """
    parser = argparse.ArgumentParser(description="Fix linting issues")
    parser.add_argument(
        "--directory",
        "-d",
        default="pyerp",
        help="Directory to search for Python files (default: pyerp)",
    )
    parser.add_argument(
        "--check-only",
        "-c",
        action="store_true",
        help="Only check for issues without fixing",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--files",
        "-f",
        nargs="+",
        help="Specific Python files to process",
    )

    args = parser.parse_args()

    # Ensure Ruff is installed
    if not ensure_ruff_installed():
        sys.exit(1)

    # Get files to process
    if args.files:
        python_files = [
            f for f in args.files if f.endswith(".py") and os.path.exists(f)
        ]
    else:
        python_files = find_python_files(args.directory)

    if not python_files:
        print(f"No Python files found in {args.directory}")
        sys.exit(0)

    print(f"Found {len(python_files)} Python files to process.")

    # Run Ruff
    if args.check_only:
        run_ruff_check(python_files, enable_verbose=args.verbose)
    else:
        run_ruff_fix(python_files, enable_verbose=args.verbose)
        run_ruff_format(python_files, enable_verbose=args.verbose)

        # Run a final check to see if any issues remain
        print("\nChecking for remaining issues...")
        run_ruff_check(python_files, enable_verbose=args.verbose)

    print("Linting process completed!")


if __name__ == "__main__":
    main()
