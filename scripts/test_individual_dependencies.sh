#!/bin/bash
# Test Individual Dependencies
# This script helps manually test a specific dependency or all dependencies in a requirements file

set -e  # Exit on error

# ANSI color codes
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test a single package with pip
test_package() {
    local package="$1"
    echo -e "\n${CYAN}Testing package: $package${NC}"

    # Try installing the package
    if pip install "$package" --dry-run; then
        echo -e "${GREEN}Package $package can be installed successfully${NC}"
        return 0
    else
        echo -e "${RED}Package $package has installation issues${NC}"
        return 1
    fi
}

# Function to test all packages in a requirements file
test_all_packages() {
    local req_file="$1"
    echo -e "${CYAN}Testing all packages in $req_file${NC}"

    # Parse the requirements file to extract package specifications
    while read -r line; do
        # Skip empty lines, comments, and -r includes
        if [[ -z "$line" || "$line" == \#* || "$line" == -r* ]]; then
            continue
        fi

        # Test each package
        if ! test_package "$line"; then
            failed_packages+=("$line")
        fi
    done < "$req_file"

    # Report results
    if [ ${#failed_packages[@]} -eq 0 ]; then
        echo -e "\n${GREEN}All packages can be installed successfully!${NC}"
    else
        echo -e "\n${RED}The following packages have installation issues:${NC}"
        for pkg in "${failed_packages[@]}"; do
            echo " - $pkg"
        done
        return 1
    fi
}

# Main script
if [ $# -eq 0 ]; then
    echo "Usage: $0 [requirements_file] [package_spec]"
    echo "Examples:"
    echo "  $0 requirements/development.in            # Test all packages in file"
    echo "  $0 package \"django>=5.1.0,<5.2.0\"         # Test specific package"
    exit 1
fi

# Initialize array for failed packages
declare -a failed_packages

# Check first argument
if [ "$1" = "package" ]; then
    # Test a specific package
    if [ -z "$2" ]; then
        echo -e "${RED}Error: Package specification is required${NC}"
        exit 1
    fi
    test_package "$2"
    exit $?
else
    # Test all packages in a file
    if [ ! -f "$1" ]; then
        echo -e "${RED}Error: Requirements file $1 not found${NC}"
        exit 1
    fi
    test_all_packages "$1"
    exit $?
fi
