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

# Which test group to run - default to all if not specified
TEST_GROUP=${1:-all}

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
  
  # Run tests with coverage and CI mode
  echo "Running Jest tests..."
  npm run test:ci
  
  # Copy test results to the expected location for the CI pipeline
  mkdir -p ../coverage
  cp jest-junit.xml ../coverage/ui-junit.xml
  cp -r coverage/coverage-final.json ../coverage/ui-coverage.xml
  
  # Return to project root
  cd ..
  
  echo "UI tests completed"
elif [ "$TEST_GROUP" = "all" ]; then
  echo "Running all tests"
  
  # First run UI tests
  $0 ui
  
  # Then run all backend tests using pytest's automatic discovery
  python -m pytest \
    --cov=pyerp \
    --cov-report=xml:coverage/all-coverage.xml \
    --junitxml=coverage/all-junit.xml \
    -o junit_family=legacy
else
  echo "Running $TEST_GROUP tests"
  
  # Use pytest markers for standard categories (backend, core, unit, etc.)
  # These markers are defined in pytest.ini
  if [[ "$TEST_GROUP" =~ ^(backend|core|unit|api|database)$ ]]; then
    echo "Using marker: -m $TEST_GROUP"
    
    # Run tests matching the marker
    python -m pytest \
      -m $TEST_GROUP \
      --cov=pyerp \
      --cov-report=xml:coverage/${TEST_GROUP}-coverage.xml \
      --junitxml=coverage/${TEST_GROUP}-junit.xml \
      -o junit_family=legacy
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
      python -m pytest \
        -k "$TEST_GROUP" \
        --cov=pyerp \
        --cov-report=xml:coverage/${TEST_GROUP}-coverage.xml \
        --junitxml=coverage/${TEST_GROUP}-junit.xml \
        -o junit_family=legacy
    else
      # Run tests from the found directory
      python -m pytest \
        "$TEST_PATH" \
        --cov=pyerp \
        --cov-report=xml:coverage/${TEST_GROUP}-coverage.xml \
        --junitxml=coverage/${TEST_GROUP}-junit.xml \
        -o junit_family=legacy
    fi
  fi
fi 