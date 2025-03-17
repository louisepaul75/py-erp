#!/bin/bash
# Script to run the sync tests specifically

# Set up environment
export PYTHONPATH=$(pwd)
export DJANGO_SETTINGS_MODULE=pyerp.config.settings.test

# Run the sync tests
echo "Running sync tests..."
cd tests && python -m pytest backend/sync/ -v

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Sync tests passed successfully!"
else
    echo "Some sync tests failed. Please check the output above."
fi 