#!/bin/bash

# A simplified script to demonstrate mutation testing on a small test file

echo "Running the tests to make sure they pass..."
python -m unittest test_mutmut_demo.py

if [ $? -eq 0 ]; then
    echo "Tests are passing. Now running mutation testing..."
    
    # Create a simple setup.cfg for mutmut
    cat > setup.cfg << EOF
[mutmut]
paths_to_mutate=test_mutmut_demo.py
backup=False
runner=python -m unittest test_mutmut_demo.py
tests_dir=.
EOF
    
    echo "Created setup.cfg for mutmut"
    
    # Create a clean mutants directory
    echo "Setting up clean mutants directory..."
    rm -rf mutants
    mkdir -p mutants
    
    # Run mutmut with explicit output directory
    echo "Running mutmut with the setup.cfg configuration..."
    PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 mutmut run
    MUTMUT_RESULT=$?
    
    if [ $MUTMUT_RESULT -eq 0 ]; then
        echo -e "\nResults summary:"
        mutmut results
        
        echo -e "\nTo show a specific mutation:"
        echo "mutmut show <id>"
        
        echo -e "\nTo apply a mutation:"
        echo "mutmut apply <id>"
    else
        echo -e "\nMutmut failed with exit code: $MUTMUT_RESULT"
        echo "Check the error messages above for details."
    fi
    
    # Clean up
    rm -f setup.cfg
else
    echo "Tests failed. Please fix the tests before running mutation testing."
    exit 1
fi 