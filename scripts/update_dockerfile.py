#!/usr/bin/env python
"""
Update Dockerfile Script

This script ensures that the Dockerfile includes all necessary dependencies,
especially those that might be causing errors in the Docker deployment.
"""

import re
from pathlib import Path


def update_dockerfile():
    """
    Update the Dockerfile to include explicit installation of critical packages.
    This helps prevent missing dependency errors in Docker deployments.
    """
    base_dir = Path(__file__).resolve().parent.parent
    dockerfile_path = base_dir / "docker" / "Dockerfile.prod"

    if not dockerfile_path.exists():
        print(f"Dockerfile not found at {dockerfile_path}")
        return False

    # Read current Dockerfile
    with open(dockerfile_path) as f:
        dockerfile_content = f.read()

    # Critical packages to ensure are explicitly installed
    critical_packages = [
        "django-redis>=5.4.0,<5.5.0",
        "redis>=5.0.0,<5.1.0",
    ]

    # Check if a verify section already exists
    verify_section_exists = (
        'echo "Verifying critical packages..."' in dockerfile_content
    )

    if not verify_section_exists:
        # Find the position to insert the verification section - after the base requirements installation
        install_pattern = (
            r"(pip install -r requirements/production\.in.*?)(?:\n\n|\n# Build wheels)"
        )
        match = re.search(install_pattern, dockerfile_content, re.DOTALL)

        if match:
            install_section = match.group(1)
            verification_section = (
                install_section
                + '\n\n# Verify critical packages are installed\nRUN echo "Verifying critical packages..." && \\\n'
            )

            for package in critical_packages:
                package_name = package.split(">=")[0].split("<")[0].strip()
                version_spec = package.split(package_name)[1].strip()
                verification_section += (
                    f'    pip install "{package_name}{version_spec}" && \\\n'
                )

            # Remove trailing " && \\n"
            verification_section = verification_section[:-6] + "\n"

            # Replace the original section with the new one including verification
            dockerfile_content = re.sub(
                install_pattern,
                verification_section,
                dockerfile_content,
                flags=re.DOTALL,
            )

            # Write the updated content back
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)

            print(
                f"Dockerfile updated to verify critical packages: {', '.join([p.split('>=')[0] for p in critical_packages])}",
            )
            return True
        print("Could not find a suitable position to insert verification section")
        return False
    print("Dockerfile already contains package verification section")
    return True


if __name__ == "__main__":
    print("Updating Dockerfile to ensure all critical dependencies are installed...")
    if update_dockerfile():
        print("Dockerfile successfully updated!")
    else:
        print("Failed to update Dockerfile.")
