# Dependency Management Implementation Plan

## Overview

This document outlines the technical implementation plan for enhancing dependency management in the pyERP project. The goal is to provide a robust, reproducible, and secure approach to managing Python dependencies across development and production environments.

## Current State

The project currently uses:
- Docker and Docker Compose for development
- Pinned dependencies in requirements.txt and requirements-dev.txt
- Environment variables for configuration
- Pre-commit hooks for code quality

## Implementation Plan

### 1. Implement pip-tools for Dependency Management

#### Background
[pip-tools](https://github.com/jazzband/pip-tools) consists of two commands: `pip-compile` and `pip-sync`. It enables more maintainable dependency management by separating direct dependencies from the complete dependency tree.

#### Implementation Steps

1. **Create Requirements Input Files**:
   ```bash
   # Create base.in with minimal core dependencies
   touch requirements/base.in

   # Create production.in that extends base
   touch requirements/production.in

   # Create development.in that extends production
   touch requirements/development.in
   ```

2. **Populate Input Files**:
   - `base.in`: Core dependencies like Django, DRF, database clients
   - `production.in`: Production-specific dependencies like gunicorn, monitoring tools
   - `development.in`: Development-specific dependencies like debugging tools, testing frameworks

3. **Install pip-tools**:
   ```bash
   pip install pip-tools
   ```

4. **Compile Requirements Files**:
   ```bash
   # Compile the base requirements
   pip-compile requirements/base.in --output-file=requirements/base.txt

   # Compile production requirements
   pip-compile --generate-hashes requirements/production.in --output-file=requirements/production.txt

   # Compile development requirements
   pip-compile requirements/development.in --output-file=requirements/development.txt
   ```

5. **Update Docker Configuration**:
   - Update Dockerfile.dev to use the new requirement files
   - Create a script to automate dependency updates

6. **Document Workflow**:
   - Create documentation on how to add/update dependencies
   - Define when to update dependencies and how to test changes

### 2. Create Production-Optimized Dockerfile

#### Implementation Steps

1. **Create Multi-Stage Dockerfile.prod**:
   ```dockerfile
   # Build stage
   FROM python:3.11-slim AS builder

   WORKDIR /app

   # Install build dependencies
   RUN apt-get update && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       libpq-dev

   # Install pip-tools
   RUN pip install pip-tools

   # Copy requirements files
   COPY requirements/production.txt .

   # Install dependencies
   RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r production.txt

   # Final stage
   FROM python:3.11-slim

   # Create non-root user
   RUN useradd -m appuser

   # Install runtime dependencies only
   RUN apt-get update && apt-get install -y --no-install-recommends \
       libpq5 \
       # WeasyPrint runtime dependencies
       libcairo2 \
       libpango-1.0-0 \
       libpangocairo-1.0-0 \
       libgdk-pixbuf2.0-0 \
       shared-mime-info \
       && apt-get clean \
       && rm -rf /var/lib/apt/lists/*

   WORKDIR /app

   # Copy wheels from builder
   COPY --from=builder /app/wheels /wheels
   RUN pip install --no-cache /wheels/*

   # Copy application code
   COPY . .

   # Set permissions
   RUN chown -R appuser:appuser /app

   # Use non-root user
   USER appuser

   # Environment configuration
   ENV DJANGO_SETTINGS_MODULE=pyerp.settings.production

   # Create required directories with proper permissions
   RUN mkdir -p /app/static /app/media /app/logs

   # Run gunicorn
   CMD ["gunicorn", "pyerp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
   ```

2. **Create Production docker-compose.yml**:
   Create a separate docker-compose file for production deployment with appropriate volumes and environment settings.

3. **Document Production Deployment Process**:
   Create step-by-step documentation for building and deploying production images.

### 3. Implement Dependency Monitoring and Updates

#### Implementation Steps

1. **Set Up Dependabot or Similar Tool**:
   - Configure GitHub Dependabot (if using GitHub)
   - Or set up a custom script to check for updates

2. **Create Update Automation Script**:
   ```python
   #!/usr/bin/env python
   """
   Dependency update script.

   This script:
   1. Updates each requirements.in file
   2. Re-compiles all requirements files
   3. Creates a summary of changes
   """

   import subprocess
   import os
   import re
   from datetime import datetime

   def update_dependencies():
       """Update all dependencies and compile requirements files."""
       # Directory containing requirements files
       req_dir = "requirements"

       # Input files to process
       input_files = ["base.in", "production.in", "development.in"]

       # Compile each input file
       for input_file in input_files:
           input_path = os.path.join(req_dir, input_file)
           output_path = os.path.join(req_dir, input_file.replace(".in", ".txt"))

           # Add --upgrade flag to get latest versions
           subprocess.run([
               "pip-compile",
               "--upgrade",
               "--generate-hashes",
               input_path,
               "--output-file",
               output_path
           ], check=True)

           print(f"Compiled {input_path} to {output_path}")

       # Generate update summary
       generate_update_summary()

   def generate_update_summary():
       """Generate a summary of dependency changes from git diff."""
       # Get git diff for requirements txt files
       result = subprocess.run(
           ["git", "diff", "requirements/*.txt"],
           capture_output=True,
           text=True,
           check=False
       )

       # Parse diff to extract package changes
       changes = parse_requirements_diff(result.stdout)

       # Write summary to file
       with open("dependency_update_summary.md", "w") as f:
           f.write(f"# Dependency Update Summary\n\n")
           f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

           if not changes:
               f.write("No dependency changes detected.\n")
               return

           f.write("## Changes\n\n")
           for package, versions in changes.items():
               f.write(f"- **{package}**: {versions['old']} → {versions['new']}\n")

   def parse_requirements_diff(diff_text):
       """Parse git diff output to extract package version changes."""
       changes = {}
       package_pattern = re.compile(r'[-+](.+)==(.+)')

       for line in diff_text.split('\n'):
           if line.startswith('-') and '==' in line and not line.startswith('--'):
               match = package_pattern.match(line)
               if match:
                   package, version = match.groups()
                   if package not in changes:
                       changes[package] = {}
                   changes[package]['old'] = version

           elif line.startswith('+') and '==' in line and not line.startswith('++'):
               match = package_pattern.match(line)
               if match:
                   package, version = match.groups()
                   if package not in changes:
                       changes[package] = {}
                   changes[package]['new'] = version

       # Remove entries that don't have both old and new versions
       return {k: v for k, v in changes.items() if 'old' in v and 'new' in v}

   if __name__ == "__main__":
       update_dependencies()
   ```

3. **Add CI Workflow for Dependency Updates**:
   - Create GitHub Action or GitLab CI job to run update script
   - Configure it to create PRs with update summaries
   - Set up automatic testing of updated dependencies

### 4. Implement Dependency Security Scanning

#### Implementation Steps

1. **Add Safety to Development Requirements**:
   ```
   # Add to requirements/development.in
   safety==2.3.5
   ```

2. **Create Security Scanning Script**:
   ```python
   #!/usr/bin/env python
   """
   Dependency security scanner.

   Checks for security vulnerabilities in Python dependencies.
   """

   import subprocess
   import json
   import os
   import sys
   from datetime import datetime

   def scan_dependencies():
       """Scan dependencies for security vulnerabilities."""
       # Run safety check and capture JSON output
       result = subprocess.run(
           ["safety", "check", "--full-report", "--json"],
           capture_output=True,
           text=True,
           check=False
       )

       try:
           data = json.loads(result.stdout)

           # Generate report
           report_path = "security_scan_report.md"
           generate_report(data, report_path)

           # Exit with error code if vulnerabilities found
           if data['vulnerabilities']:
               print(f"Found {len(data['vulnerabilities'])} vulnerability issues.")
               print(f"See {report_path} for details.")
               return len(data['vulnerabilities'])

           print("No security vulnerabilities found.")
           return 0

       except json.JSONDecodeError:
           print("Error parsing safety output")
           print(result.stdout)
           return 1

   def generate_report(data, report_path):
       """Generate a markdown report from safety scan results."""
       with open(report_path, "w") as f:
           f.write(f"# Security Vulnerability Report\n\n")
           f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")

           if not data['vulnerabilities']:
               f.write("No security vulnerabilities found.\n")
               return

           f.write(f"## Vulnerabilities ({len(data['vulnerabilities'])})\n\n")

           # Group by severity if available
           by_severity = {}
           for vuln in data['vulnerabilities']:
               severity = vuln.get('severity', 'Unknown')
               if severity not in by_severity:
                   by_severity[severity] = []
               by_severity[severity].append(vuln)

           # Write vulnerabilities by severity
           for severity in sorted(by_severity.keys(), reverse=True):
               f.write(f"### {severity} Severity ({len(by_severity[severity])})\n\n")

               for vuln in by_severity[severity]:
                   package_name = vuln.get('package_name', 'Unknown')
                   affected_version = vuln.get('vulnerable_spec', 'Unknown')
                   summary = vuln.get('advisory', 'No details available')

                   f.write(f"#### {package_name} ({affected_version})\n\n")
                   f.write(f"{summary}\n\n")

                   if 'fix_version' in vuln and vuln['fix_version']:
                       f.write(f"**Fix available:** Update to version {vuln['fix_version']} or later\n\n")
                   else:
                       f.write(f"**No fix available yet**\n\n")

   if __name__ == "__main__":
       sys.exit(scan_dependencies())
   ```

3. **Add CI Job for Security Scanning**:
   - Create GitHub Action or GitLab CI job to run security scanner
   - Configure notifications for critical vulnerabilities
   - Set up periodic scans (weekly)

4. **Add Pre-Commit Hook for Security Scanning**:
   Update `.pre-commit-config.yaml` to include safety checks

### 5. Document Dependency Management Procedures

#### Implementation Steps

1. **Create Dependency Management Guide**:
   - Create a markdown document in the docs folder
   - Cover all aspects of dependency management workflow

2. **Create Upgrade Guidelines**:
   - Document the process for reviewing and approving updates
   - Define criteria for accepting/rejecting updates
   - Explain testing requirements for dependency changes

3. **Create Onboarding Documentation**:
   - Include dependency management in developer onboarding
   - Provide examples of common scenarios (adding dependencies, etc.)

## Timeline

| Task | Estimated Duration | Dependencies |
|------|-------------------|--------------|
| Implement pip-tools | 2 days | None |
| Create Production Dockerfile | 3 days | pip-tools implementation |
| Dependency Monitoring | 2 days | pip-tools implementation |
| Security Scanning | 1 day | None |
| Documentation | 2 days | All other tasks |

## Success Criteria

1. Developers can set up environments consistently with a single command
2. Production deployments use optimized, secure containers
3. Dependencies are automatically checked for updates and security issues
4. Clear documentation exists for all dependency management procedures
5. CI/CD pipeline includes dependency validation and security scanning
