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
    # Create scripts directory if it doesn't exist
    os.makedirs("scripts", exist_ok=True)
    
    # Directory containing requirements files
    req_dir = "requirements"
    
    # Input files to process
    input_files = ["base.in", "production.in", "development.in"]
    
    # Compile each input file
    for input_file in input_files:
        input_path = os.path.join(req_dir, input_file)
        output_path = os.path.join(req_dir, input_file.replace(".in", ".txt"))
        
        print(f"Compiling {input_path} to {output_path}...")
        
        # Add --upgrade flag to get latest versions
        subprocess.run([
            "pip-compile", 
            "--upgrade", 
            "--verbose",
            input_path,
            "--output-file", 
            output_path
        ], check=True)
        
        print(f"Successfully compiled {input_path} to {output_path}")
    
    # Generate update summary
    generate_update_summary()

def generate_update_summary():
    """Generate a summary of dependency changes from git diff."""
    print("Generating dependency update summary...")
    
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
    summary_path = "dependency_update_summary.md"
    with open(summary_path, "w") as f:
        f.write(f"# Dependency Update Summary\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        
        if not changes:
            f.write("No dependency changes detected.\n")
            print("No dependency changes detected.")
            return
            
        f.write("## Changes\n\n")
        for package, versions in changes.items():
            f.write(f"- **{package}**: {versions['old']} → {versions['new']}\n")
    
    print(f"Summary written to {summary_path}")
    print(f"Found {len(changes)} package updates")

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