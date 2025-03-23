#!/bin/bash

# Simple script to run mutation testing on basic functions

echo "Running tests to ensure they pass..."
python -m unittest test_basic_functions.py

if [ $? -eq 0 ]; then
    echo "Tests passed! Running mutation testing..."
    
    # Create a setup.cfg file for mutmut
    cat > setup.cfg << EOF
[mutmut]
paths_to_mutate=basic_functions.py
backup=False
runner=python -m unittest test_basic_functions.py
EOF
    
    echo "Created setup.cfg for mutmut"
    
    # Run mutation testing
    python -m mutmut run
    MUTMUT_STATUS=$?
    
    # Show results
    if [ $MUTMUT_STATUS -eq 0 ]; then
        echo "Mutation testing completed successfully!"
        
        # Show summary of results
        results=$(python -m mutmut results)
        echo -e "\nResults summary:"
        echo "$results"
        
        # Count survived mutations
        survived_count=$(echo "$results" | grep -c "survived")
        
        # Check if there are survived mutants
        if [ "$survived_count" -gt 0 ]; then
            echo -e "\nFound $survived_count survived mutations! This means your tests didn't catch these potential bugs."
            
            echo -e "\nShowing the first mutation as an example:"
            python -m mutmut show 1
            
            echo -e "\nTo fix these issues, improve your tests to catch more mutations."
            echo "Try adding more test cases, especially for edge cases and conditional logic."
        else
            echo -e "\nGreat job! All mutations were killed by your tests."
        fi
    else
        echo "Mutation testing failed with exit code: $MUTMUT_STATUS"
    fi
    
    # Clean up
    rm -f setup.cfg
    
    echo -e "\nMutation testing demo complete."
else
    echo "Tests failed. Please fix the tests before running mutation testing."
    exit 1
fi 