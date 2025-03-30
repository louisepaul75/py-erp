#!/bin/bash
set -e

# Create coverage directory
mkdir -p coverage

# Function to verify we're in the right location
verify_project_root() {
  if [ -f "manage.py" ] && [ -f "setup.py" ]; then
    return 0  # We're in the project root
  else
    return 1  # Not in the project root
  fi
}

# Check current location
if verify_project_root; then
  echo "Currently in project root: $(pwd)"
else
  # Try to find the project root
  echo "Not in project root, attempting to locate it..."
  
  # Try going up one directory
  cd ..
  if verify_project_root; then
    echo "Found project root after moving up: $(pwd)"
  else
    echo "ERROR: Could not locate project root"
    echo "Current location: $(pwd)"
    exit 1
  fi
fi

# Default options
COVERAGE=true
MUTATION=false
FUZZ=false
VERBOSITY=1

# Parse command line options
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-coverage)
      COVERAGE=false
      shift
      ;;
    --mutation)
      MUTATION=true
      shift
      ;;
    --fuzz)
      FUZZ=true
      shift
      ;;
    -v|--verbose)
      VERBOSITY=2
      shift
      ;;
    -q|--quiet)
      VERBOSITY=0
      shift
      ;;
    *)
      TEST_GROUP=$1
      shift
      ;;
  esac
done

# Set default test group to 'all' if not specified
TEST_GROUP=${TEST_GROUP:-all}

echo "Running tests with options:"
echo "  Test group: $TEST_GROUP"
echo "  Coverage: $COVERAGE"
echo "  Mutation testing: $MUTATION"
echo "  Fuzz testing: $FUZZ"
echo "  Verbosity: $VERBOSITY"

# Prepare base pytest options
PYTEST_OPTS=""

# Add coverage options if enabled
if [ "$COVERAGE" = true ]; then
  PYTEST_OPTS="$PYTEST_OPTS --cov=pyerp"
  PYTEST_OPTS="$PYTEST_OPTS --cov-report=xml:coverage/${TEST_GROUP}-coverage.xml"
  PYTEST_OPTS="$PYTEST_OPTS --junitxml=coverage/${TEST_GROUP}-junit.xml"
  PYTEST_OPTS="$PYTEST_OPTS -o junit_family=legacy"
fi

# Add verbosity options
if [ "$VERBOSITY" -eq 0 ]; then
  PYTEST_OPTS="$PYTEST_OPTS -q"
elif [ "$VERBOSITY" -eq 2 ]; then
  PYTEST_OPTS="$PYTEST_OPTS -v"
fi

# Special handling for UI tests which use Jest
if [ "$TEST_GROUP" = "ui" ]; then
  echo "Running UI tests with Jest"
  
  # Check if frontend-react directory exists
  if [ ! -d "frontend-react" ]; then
    echo "ERROR: frontend-react directory not found"
    echo "Current location: $(pwd)"
    echo "Contents:"
    ls -la
    exit 1
  fi
  
  # Check if Node.js is installed
  if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    exit 1
  fi
  
  # Go to frontend directory and run tests
  cd frontend-react
  
  # Install dependencies if node_modules doesn't exist or is empty
  if [ ! -d "node_modules" ] || [ -z "$(ls -A node_modules)" ]; then
    echo "Installing frontend dependencies..."
    npm ci
  fi
  
  # Prepare Jest options
  JEST_OPTS=""
  
  # Add coverage options for Jest
  if [ "$COVERAGE" = true ]; then
    JEST_OPTS="$JEST_OPTS --coverage"
  fi
  
  # Add fuzz testing options for Jest
  if [ "$FUZZ" = true ]; then
    JEST_OPTS="$JEST_OPTS --testMatch='**/?(*.)+(fuzz).test.[jt]s?(x)'"
  fi
  
  # Run tests with prepared options
  echo "Running Jest tests with options: $JEST_OPTS"
  npm test -- $JEST_OPTS
  
  # Copy test results to the expected location for the CI pipeline
  if [ "$COVERAGE" = true ]; then
    mkdir -p ../coverage
    cp jest-junit.xml ../coverage/ui-junit.xml
    cp -r coverage/coverage-final.json ../coverage/ui-coverage.xml
  fi
  
  # Return to project root
  cd ..
  
  echo "UI tests completed"
elif [ "$TEST_GROUP" = "all" ]; then
  echo "Running all tests"
  
  # First run UI tests
  $0 ui
  
  # Then run backend tests
  
  # Add fuzz test markers if enabled
  if [ "$FUZZ" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -m 'fuzzing or property'"
  fi
  
  # Run backend tests with automatic discovery
  python -m pytest $PYTEST_OPTS --nomigrations
  
  # Run mutation tests if enabled
  if [ "$MUTATION" = true ]; then
    echo "Running mutation tests with mutmut"
    if [ -f "tools/mutation_testing/run_mutmut.sh" ]; then
      ./tools/mutation_testing/run_mutmut.sh
    else
      echo "WARNING: Mutation testing script not found at tools/mutation_testing/run_mutmut.sh"
      echo "Attempting to run mutmut directly"
      python -m mutmut run
    fi
  fi
elif [ "$TEST_GROUP" = "sync" ]; then
  echo "Running sync tests"
  
  # Set up environment for sync tests
  export DJANGO_SETTINGS_MODULE=pyerp.config.settings.test
  
  # Run the sync tests with the appropriate options
  echo "Running sync tests with pytest..."
  python -m pytest tests/backend/sync/ $PYTEST_OPTS
  
  echo "Sync tests completed"
else
  echo "Running $TEST_GROUP tests"
  
  # Use pytest markers for standard categories (backend, core, unit, etc.)
  # These markers are defined in pytest.ini
  if [[ "$TEST_GROUP" =~ ^(backend|core|unit|api|database)$ ]]; then
    echo "Using marker: -m $TEST_GROUP"
    
    # Add fuzz test markers if enabled
    if [ "$FUZZ" = true ]; then
      PYTEST_OPTS="$PYTEST_OPTS -m '$TEST_GROUP or fuzzing or property'"
    else
      PYTEST_OPTS="$PYTEST_OPTS -m $TEST_GROUP"
    fi
    
    # Run tests matching the marker
    python -m pytest $PYTEST_OPTS --nomigrations
  else
    # For other test groups, try to find a matching directory
    echo "Looking for test directory for group: $TEST_GROUP"
    
    # Try different possible locations for tests
    # Add or modify these paths according to your actual project structure
    POSSIBLE_PATHS=(
      "pyerp/$TEST_GROUP/tests"  # Module-specific tests
      "pyerp/tests/$TEST_GROUP"  # Tests grouped by category in central location
      "$TEST_GROUP"              # Top-level directory
    )
    
    TEST_PATH=""
    for path in "${POSSIBLE_PATHS[@]}"; do
      if [ -d "$path" ]; then
        TEST_PATH="$path"
        echo "Found test directory: $TEST_PATH"
        break
      fi
    done
    
    if [ -z "$TEST_PATH" ]; then
      echo "WARNING: Could not find test directory for group $TEST_GROUP"
      echo "Available directories in pyerp:"
      ls -la pyerp/
      echo "Attempting to run tests using the group name as a directory pattern"
      
      # Fall back to running tests using a pattern
      python -m pytest -k "$TEST_GROUP" $PYTEST_OPTS --nomigrations
    else
      # Run tests from the found directory
      python -m pytest "$TEST_PATH" $PYTEST_OPTS --nomigrations
    fi
  fi
  
  # Run mutation tests if enabled and we have a specific module to test
  if [ "$MUTATION" = true ]; then
    echo "Running mutation tests for $TEST_GROUP"
    if [ -f "tools/mutation_testing/run_mutmut.sh" ]; then
      if [ -n "$TEST_PATH" ]; then
        ./tools/mutation_testing/run_mutmut.sh "pyerp/$TEST_GROUP" "$TEST_PATH"
      else
        ./tools/mutation_testing/run_mutmut.sh "pyerp/$TEST_GROUP"
      fi
    else
      echo "WARNING: Mutation testing script not found at tools/mutation_testing/run_mutmut.sh"
      echo "Attempting to run mutmut directly"
      python -m mutmut run --paths-to-mutate "pyerp/$TEST_GROUP"
    fi
  fi
fi 