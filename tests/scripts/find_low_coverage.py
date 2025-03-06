import json
import os
from collections import defaultdict


def find_coverage_files():
    """Find the coverage data file."""
    coverage_file = ".coverage"
    if os.path.exists(coverage_file):
        return coverage_file

    # Try to find in htmlcov directory
    json_file = "htmlcov/coverage.json"
    if os.path.exists(json_file):
        return json_file

    return None


def analyze_coverage():
    """Analyze coverage data and identify modules with low coverage."""
    coverage_file = find_coverage_files()
    if not coverage_file:
        print("Error: No coverage data found. Run tests with coverage first.")
        return

    # If we're using the .coverage file, we need to run coverage json to convert it
    if coverage_file == ".coverage":
        print("Converting .coverage to JSON format...")
        os.system("coverage json")
        coverage_file = "coverage.json"

    # Read the coverage data
    try:
        with open(coverage_file) as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading coverage data: {e}")
        return

    # Extract file coverage information
    modules = []

    for filename, file_data in data.get("files", {}).items():
        if "pyerp" not in filename:
            continue

        # Calculate metrics
        total_statements = len(file_data.get("executed_lines", [])) + len(
            file_data.get("missing_lines", []),
        )
        executed_statements = len(file_data.get("executed_lines", []))

        if total_statements == 0:
            coverage_percentage = 0
        else:
            coverage_percentage = (executed_statements / total_statements) * 100

        modules.append(
            {
                "filename": filename,
                "coverage": coverage_percentage,
                "total_statements": total_statements,
                "executed_statements": executed_statements,
                "missing_statements": total_statements - executed_statements,
            },
        )

    # Sort by coverage percentage (ascending)
    modules.sort(key=lambda x: (x["coverage"], -x["total_statements"]))

    # Group modules by directory
    dir_coverage = defaultdict(list)
    for module in modules:
        parts = module["filename"].split("/")
        if len(parts) >= 2:
            dir_name = parts[-2]  # Get the directory name
            dir_coverage[dir_name].append(module)

    # Print results
    print("\n=== Modules with Lowest Coverage ===")
    for i, module in enumerate(modules[:15]):
        print(f"{i + 1}. {module['filename']}")
        print(
            f"   Coverage: {module['coverage']:.1f}% ({module['executed_statements']}/{module['total_statements']} statements)",
        )
        print()

    print("\n=== Coverage by Directory ===")
    for dir_name, dir_modules in dir_coverage.items():
        total_stmts = sum(m["total_statements"] for m in dir_modules)
        executed_stmts = sum(m["executed_statements"] for m in dir_modules)
        if total_stmts > 0:
            dir_percentage = (executed_stmts / total_stmts) * 100
        else:
            dir_percentage = 0

        print(
            f"{dir_name}: {dir_percentage:.1f}% ({executed_stmts}/{total_stmts} statements)",
        )


if __name__ == "__main__":
    analyze_coverage()
