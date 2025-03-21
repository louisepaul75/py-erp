#!/bin/bash

# This script runs mutation testing using mutmut on a specific module

# Check if a module path is provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <module_path> [test_path]"
    echo "Example: $0 pyerp/users/models.py tests/unit/users"
    exit 1
fi

# Store the current directory to return to it later
CURRENT_DIR=$(pwd)

# Get module path and test path
MODULE_PATH=$1
TEST_PATH=${2:-"tests"}

# Convert to absolute paths
ABS_MODULE_PATH="$CURRENT_DIR/$MODULE_PATH"
ABS_TEST_PATH="$CURRENT_DIR/$TEST_PATH"

echo "Running mutation testing for $MODULE_PATH"
echo "Using tests in $TEST_PATH"

# Set environment variables for pytest
export PYTHONPATH="${CURRENT_DIR}:${PYTHONPATH:-.}"
export PYTEST_RUNNING=1
export DJANGO_SETTINGS_MODULE=pyerp.config.settings.test

# Run pytest first to make sure tests are collecting and running
echo "Verifying tests are working correctly..."
python -m pytest $TEST_PATH -v

# If tests are working, proceed with mutation testing
if [ $? -eq 0 ]; then
    echo "Tests are running correctly. Preparing for mutation testing..."
    
    # Create a dedicated directory for mutmut
    MUTMUT_DIR="$CURRENT_DIR/mutmut_temp"
    mkdir -p "$MUTMUT_DIR"
    cd "$MUTMUT_DIR"
    
    # Create setup.cfg with absolute paths
    cat > setup.cfg << EOF
[mutmut]
paths_to_mutate=$ABS_MODULE_PATH
backup=False
runner=cd "$CURRENT_DIR" && python -m pytest $TEST_PATH -v
tests_dir=$ABS_TEST_PATH
dict_synonyms=Struct,Bunch
EOF
    
    echo "Created setup.cfg with absolute paths"
    
    # Run mutmut
    echo "Running mutmut from $MUTMUT_DIR..."
    
    # Use python -m to ensure we're running the right mutmut
    python -m mutmut run
    MUTMUT_RESULT=$?
    
    # Return to the original directory
    cd "$CURRENT_DIR"
    
    # Show the results if mutmut ran successfully
    if [ $MUTMUT_RESULT -eq 0 ]; then
        echo -e "\nResults summary:"
        mutmut results
        
        echo -e "\nTo show a specific mutation:"
        echo "mutmut show <id>"
        
        echo -e "\nTo apply a mutation:"
        echo "mutmut apply <id>"
    else
        echo -e "\nMutmut failed with exit code: $MUTMUT_RESULT"
        echo "Check the setup in $MUTMUT_DIR for errors."
    fi
    
    echo -e "\nMutation testing complete."
    
    # Clean up (optional)
    # rm -rf "$MUTMUT_DIR"
    # echo "Temporary directory cleaned up"
else
    echo "Tests are not running correctly. Please fix the tests before running mutation testing."
    exit 1
fi 