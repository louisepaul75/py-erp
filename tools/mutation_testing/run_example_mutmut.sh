#!/bin/bash

# A very simple script to demonstrate mutation testing

echo "Running the tests to make sure they pass..."
python -m unittest mutmut_example.py

if [ $? -eq 0 ]; then
    echo "Tests are passing. Now running mutation testing..."
    
    # Create a temporary directory for mutmut
    TEMP_DIR="$(mktemp -d)"
    echo "Created temporary directory: $TEMP_DIR"
    
    # Copy our example file
    cp mutmut_example.py "$TEMP_DIR/"
    cd "$TEMP_DIR"
    
    # Create setup.cfg for mutmut
    cat > setup.cfg << EOF
[mutmut]
paths_to_mutate=mutmut_example.py
backup=False
runner=python -m unittest mutmut_example.py
EOF
    
    echo "Created setup.cfg configuration"
    
    # Run mutmut
    echo "Running mutmut on mutmut_example.py..."
    python -m mutmut run
    MUTMUT_STATUS=$?
    
    # Show results
    if [ $MUTMUT_STATUS -eq 0 ]; then
        echo -e "\nResults summary:"
        python -m mutmut results
        
        echo -e "\nHere's an example of a mutation (if any were generated):"
        python -m mutmut show 1
    else
        echo -e "\nMutmut failed with status code: $MUTMUT_STATUS"
    fi
    
    # Return to original directory
    cd - > /dev/null
    
    # Clean up
    rm -rf "$TEMP_DIR"
    
    echo -e "\nMutation testing demonstration complete."
else
    echo "Tests failed. Please fix the tests before running mutation testing."
    exit 1
fi 