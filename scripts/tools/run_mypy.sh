#!/bin/bash

# Script to run mypy with the new configuration

echo "Running mypy with the new configuration..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# First, install the type stubs if they haven't been installed yet
if [ ! -f "$SCRIPT_DIR/.type_stubs_installed" ]; then
    echo "Installing type stubs..."
    bash "$SCRIPT_DIR/install_type_stubs.sh"
fi

# Run mypy with the new configuration
mypy --config-file "$SCRIPT_DIR/mypy.ini" .

# Check the exit code
if [ $? -eq 0 ]; then
    echo "mypy check passed successfully!"
else
    echo "mypy check failed. Please fix the remaining errors."
fi
