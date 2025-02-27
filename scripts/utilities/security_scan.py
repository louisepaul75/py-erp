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
    os.makedirs("scripts", exist_ok=True)
    
    print("Scanning dependencies for security vulnerabilities...")
    
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