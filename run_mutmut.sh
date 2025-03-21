#!/bin/bash

# This script runs mutation testing using mutmut on a specific module

# Check if a module path is provided
if [ "$#" -eq 0 ]; then
    echo "Usage: $0 <module_path> [test_path]"
    echo "Example: $0 pyerp/users/models.py tests/unit/users"
    exit 1
fi

MODULE_PATH=$1
TEST_PATH=${2:-"tests"}

echo "Running mutation testing for $MODULE_PATH with tests in $TEST_PATH"

# Run mutmut on the specified module
mutmut run --paths-to-mutate "$MODULE_PATH" --tests-dir "$TEST_PATH"

# Show the results
echo -e "\nResults summary:"
mutmut results

# Optionally, you can add flags to show specific mutations
echo -e "\nTo show a specific mutation:"
echo "mutmut show <id>"

# Optionally, generate HTML report
echo -e "\nGenerating HTML report..."
mutmut html

echo -e "\nMutation testing complete. HTML report available at html/index.html" 