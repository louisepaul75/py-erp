#!/usr/bin/env python
"""
Docker Dependency Checker

This script checks for missing dependencies in a running Docker container
by attempting to import them and printing the result.
"""

from pathlib import Path


def create_check_script():
    """Create a Python script to check for dependencies."""
    check_script = """#!/usr/bin/env python
import sys
import importlib.util

# List of packages to check
packages = [
    'django',
    'django_redis',
    'celery',
    'redis',
    'rest_framework',
    'django_filter',
    'corsheaders',
    'storages'
]

missing = []
found = []

for package in packages:
    try:
        importlib.import_module(package)
        found.append(package)
    except ImportError:
        missing.append(package)

print("Found packages:")
for pkg in found:
    print(f"  ✓ {pkg}")

print("\\nMissing packages:")
if missing:
    for pkg in missing:
        print(f"  ✗ {pkg}")
    sys.exit(1)
else:
    print("  None")
    sys.exit(0)
"""
    base_dir = Path(__file__).resolve().parent.parent
    script_path = base_dir / "docker" / "check_deps.py"

    with open(script_path, "w") as f:
        f.write(check_script)

    return script_path


def add_check_to_start_script():
    """Add dependency checking to the Docker start script."""
    base_dir = Path(__file__).resolve().parent.parent
    start_script_path = base_dir / "docker" / "start.sh"

    if not start_script_path.exists():
        print(f"Start script not found at {start_script_path}")
        return False

    with open(start_script_path) as f:
        content = f.read()

    if "check_deps.py" in content:
        print("Dependency check already present in start.sh")
        return True

    # Add the dependency check after the shebang
    import_check = """
# Check for missing dependencies
echo "Checking for dependencies..."
python /app/docker/check_deps.py
if [ $? -ne 0 ]; then
    echo "ERROR: Missing dependencies detected! See log above."
    echo "Fix the Dockerfile to include all required packages."
    # Continue anyway but dependencies might be missing
    echo "Continuing despite missing dependencies..."
fi
"""

    # Insert after the shebang line
    if content.startswith("#!/"):
        first_line_end = content.find("\n") + 1
        new_content = content[:first_line_end] + import_check + content[first_line_end:]

        with open(start_script_path, "w") as f:
            f.write(new_content)

        print("Added dependency check to start.sh")
        return True
    print("Could not find proper location to insert dependency check")
    return False


def main():
    """Main function."""
    print("Creating dependency check script...")
    script_path = create_check_script()
    print(f"Created dependency check script at {script_path}")

    print("\nUpdating Docker start script...")
    if add_check_to_start_script():
        print("Docker start script updated successfully!")
    else:
        print("Failed to update Docker start script.")

    print("\nYou can now rebuild your Docker image. The container will automatically")
    print("check for missing dependencies on startup and warn you if any are missing.")


if __name__ == "__main__":
    main()
