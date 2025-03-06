#!/usr/bin/env python
"""
Dependency Update Script

This script automates the process of:
1. Scanning the codebase for required dependencies using check_dependencies.py
2. Generating pinned requirements.txt files
3. Creating wheel files for faster Docker builds
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    try:
        # Split the command into a list of arguments if it's a string
        cmd_args = command if isinstance(command, list) else command.split()

        result = subprocess.run(
            cmd_args,
            shell=False,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd,
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Command failed with error: {e.stderr}"


def check_dependencies():
    """Check for common dependencies that might be missing."""
    base_dir = Path(__file__).resolve().parent.parent
    requirements_base = base_dir / "requirements" / "base.in"

    # List of common dependencies that might be missing
    common_dependencies = [
        "django-redis>=5.4.0,<5.5.0",
        "django-storages>=1.14.0,<1.15.0",
        "django-cors-headers>=4.3.0,<4.4.0",
        "django-filter>=23.5,<24.0",
        "djangorestframework-simplejwt>=5.3.0,<5.4.0",
        "drf-yasg>=1.21.0,<1.22.0",
    ]

    with open(requirements_base) as f:
        current_content = f.read()

    missing = []
    for dep in common_dependencies:
        pkg_name = dep.split(">=")[0].split("<")[0].strip()
        if pkg_name not in current_content:
            missing.append(dep)

    if missing:
        print("Adding missing dependencies:")
        for dep in missing:
            print(f" - {dep}")

        with open(requirements_base, "a") as f:
            f.write("\n# Added automatically by dependency scanner\n")
            for dep in missing:
                f.write(f"{dep}\n")

        print("Dependencies updated successfully!")
    else:
        print("All common dependencies are already included!")

    return True


def generate_pinned_requirements():
    """Generate pinned requirements files from .in files."""
    base_dir = Path(__file__).resolve().parent.parent
    requirements_dir = base_dir / "requirements"

    if not requirements_dir.exists():
        print("Requirements directory not found.")
        return False

    # Process each .in file
    in_files = list(requirements_dir.glob("*.in"))
    for in_file in in_files:
        out_file = in_file.with_suffix(".txt")
        print(f"Installing packages from {in_file.name}...")

        # First install the packages
        success, output = run_command(
            f"pip install -r {in_file}",
            cwd=base_dir,
        )

        if not success:
            print(f"Failed to install packages from {in_file.name}: {output}")
            return False

        # Then freeze the installed packages to the .txt file
        print(f"Generating {out_file.name} by freezing installed packages...")
        success, output = run_command(
            f"pip freeze > {out_file}",
            cwd=base_dir,
        )

        if not success:
            print(f"Failed to freeze packages to {out_file.name}: {output}")
            return False

    return True


def generate_wheels():
    """Generate wheel files for all dependencies."""
    base_dir = Path(__file__).resolve().parent.parent
    wheels_dir = base_dir / "wheels"

    # Create wheels directory if it doesn't exist
    wheels_dir.mkdir(exist_ok=True)

    # Generate wheels for production dependencies
    # We use the most recent pip freeze output instead of requiring production.txt
    temp_req = base_dir / "temp_requirements.txt"

    # Generate temporary requirements file with pip freeze
    print("Generating temporary requirements file...")
    success, output = run_command(
        f"pip freeze > {temp_req}",
        cwd=base_dir,
    )

    if not success:
        print(f"Failed to generate temporary requirements: {output}")
        return False

    print(f"Generating wheels in {wheels_dir}...")
    success, output = run_command(
        f"pip wheel --no-cache-dir --wheel-dir={wheels_dir} -r {temp_req}",
        cwd=base_dir,
    )

    # Clean up the temporary file
    if temp_req.exists():
        os.remove(temp_req)

    if not success:
        print(f"Failed to generate wheels: {output}")
        return False

    print(f"Successfully generated wheels in {wheels_dir}")
    return True


def main():
    """Main function to run all dependency update steps."""
    print("=== Running Dependency Update Script ===")

    print("\n1. Checking for missing dependencies...")
    if not check_dependencies():
        print("Failed to check dependencies. Continuing anyway...")

    print("\n2. Generating pinned requirements files...")
    if not generate_pinned_requirements():
        print("Failed to generate pinned requirements.")
        return 1

    print("\n3. Generating wheel files...")
    if not generate_wheels():
        print("Failed to generate wheel files.")
        return 1

    print("\n=== Dependency update completed successfully! ===")
    print("Your requirements are now up-to-date and wheels have been generated.")
    print("This will speed up Docker builds and ensure all dependencies are included.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
