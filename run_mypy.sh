#!/bin/bash

# Script to run mypy with the new configuration

echo "Running mypy with the new configuration..."

# First, install the type stubs if they haven't been installed yet
if [ ! -f ".type_stubs_installed" ]; then
    echo "Installing type stubs..."
    bash install_type_stubs.sh
    touch .type_stubs_installed
fi

# Run mypy with the new configuration
mypy --config-file mypy.ini .

# Check the exit code
if [ $? -eq 0 ]; then
    echo "mypy check passed successfully!"
else
    echo "mypy check failed. Please fix the remaining errors."
fi 