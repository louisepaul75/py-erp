#!/bin/bash

# Script to run Jest tests with coverage and enforce minimum thresholds

# Define colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running Jest tests with coverage report...${NC}"

# Change to the frontend-react directory if running from project root
if [ -d "frontend-react" ]; then
  cd frontend-react
fi

# Ensure node_modules exists
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Installing dependencies...${NC}"
  npm install
fi

# Run Jest with coverage
npx jest --coverage --ci --reporters=default --reporters=jest-junit

# Get the exit code of Jest
TEST_RESULT=$?

# Check if tests passed
if [ $TEST_RESULT -ne 0 ]; then
  echo -e "${RED}Tests failed with exit code $TEST_RESULT${NC}"
  exit $TEST_RESULT
fi

# Path to the coverage summary
COVERAGE_SUMMARY="coverage/coverage-summary.json"

# Extract coverage data if the file exists
if [ -f "$COVERAGE_SUMMARY" ]; then
  # Extract values using jq if available, otherwise use grep and cut
  if command -v jq &> /dev/null; then
    TOTAL_STATEMENTS=$(jq -r '.total.statements.pct' "$COVERAGE_SUMMARY")
    TOTAL_BRANCHES=$(jq -r '.total.branches.pct' "$COVERAGE_SUMMARY")
    TOTAL_FUNCTIONS=$(jq -r '.total.functions.pct' "$COVERAGE_SUMMARY")
    TOTAL_LINES=$(jq -r '.total.lines.pct' "$COVERAGE_SUMMARY")
  else
    echo -e "${YELLOW}jq not found, using fallback method to extract coverage data${NC}"
    TOTAL_STATEMENTS=$(grep -A3 "\"total\":" "$COVERAGE_SUMMARY" | grep "\"pct\":" | head -1 | cut -d':' -f2 | cut -d',' -f1 | tr -d ' ')
    TOTAL_BRANCHES=$(grep -A3 "\"total\":" "$COVERAGE_SUMMARY" | grep "\"pct\":" | head -2 | tail -1 | cut -d':' -f2 | cut -d',' -f1 | tr -d ' ')
    TOTAL_FUNCTIONS=$(grep -A3 "\"total\":" "$COVERAGE_SUMMARY" | grep "\"pct\":" | head -3 | tail -1 | cut -d':' -f2 | cut -d',' -f1 | tr -d ' ')
    TOTAL_LINES=$(grep -A3 "\"total\":" "$COVERAGE_SUMMARY" | grep "\"pct\":" | head -4 | tail -1 | cut -d':' -f2 | cut -d',' -f1 | tr -d ' ')
  fi
  
  # Define minimum thresholds
  MIN_STATEMENTS=80
  MIN_BRANCHES=70
  MIN_FUNCTIONS=80
  MIN_LINES=80
  
  echo -e "\n${GREEN}Coverage Summary:${NC}"
  echo -e "  Statements: ${TOTAL_STATEMENTS}% (minimum: ${MIN_STATEMENTS}%)"
  echo -e "  Branches:   ${TOTAL_BRANCHES}% (minimum: ${MIN_BRANCHES}%)"
  echo -e "  Functions:  ${TOTAL_FUNCTIONS}% (minimum: ${MIN_FUNCTIONS}%)"
  echo -e "  Lines:      ${TOTAL_LINES}% (minimum: ${MIN_LINES}%)"
  
  # Check if coverage meets thresholds
  FAILED=0
  
  if (( $(echo "$TOTAL_STATEMENTS < $MIN_STATEMENTS" | bc -l) )); then
    echo -e "${RED}Statement coverage below threshold!${NC}"
    FAILED=1
  fi
  
  if (( $(echo "$TOTAL_BRANCHES < $MIN_BRANCHES" | bc -l) )); then
    echo -e "${RED}Branch coverage below threshold!${NC}"
    FAILED=1
  fi
  
  if (( $(echo "$TOTAL_FUNCTIONS < $MIN_FUNCTIONS" | bc -l) )); then
    echo -e "${RED}Function coverage below threshold!${NC}"
    FAILED=1
  fi
  
  if (( $(echo "$TOTAL_LINES < $MIN_LINES" | bc -l) )); then
    echo -e "${RED}Line coverage below threshold!${NC}"
    FAILED=1
  fi
  
  if [ $FAILED -eq 1 ]; then
    echo -e "\n${RED}Coverage does not meet minimum thresholds.${NC}"
    echo -e "${YELLOW}See detailed report at: ${PWD}/coverage/lcov-report/index.html${NC}"
    exit 1
  else
    echo -e "\n${GREEN}All coverage thresholds met!${NC}"
    echo -e "${YELLOW}See detailed report at: ${PWD}/coverage/lcov-report/index.html${NC}"
  fi
else
  echo -e "${RED}Coverage summary file not found: $COVERAGE_SUMMARY${NC}"
  exit 1
fi

exit 0 