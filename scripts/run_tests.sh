#!/bin/bash
set -e

# Create coverage directory
mkdir -p coverage

# Check if tests directory exists in current location
if [ -d "tests" ]; then
  cd tests
  echo "Running tests from tests directory: $(pwd)"
else
  echo "Tests directory not found in current location: $(pwd)"
  # If we're not already in the project root, try to find it
  if [ ! -f "manage.py" ]; then
    # Try to move up one directory if we're in a subdirectory
    cd ..
    if [ -d "tests" ]; then
      cd tests
      echo "Found tests directory after moving up: $(pwd)"
    else
      echo "ERROR: Could not locate tests directory"
      exit 1
    fi
  else
    echo "ERROR: In project root but tests directory not found"
    exit 1
  fi
fi

# Which test group to run - default to all if not specified
TEST_GROUP=${1:-all}

if [ "$TEST_GROUP" = "all" ]; then
  # Run all tests
  python -m pytest \
    --cov=../pyerp \
    --cov-report=xml:../coverage/all-coverage.xml \
    --junitxml=../coverage/all-junit.xml \
    -o junit_family=legacy
else
  # Run specific test group
  python -m pytest ${TEST_GROUP}/ \
    --cov=../pyerp \
    --cov-report=xml:../coverage/${TEST_GROUP}-coverage.xml \
    --junitxml=../coverage/${TEST_GROUP}-junit.xml \
    -o junit_family=legacy
fi 