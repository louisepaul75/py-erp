#!/bin/bash

# Script to ensure all necessary frontend dependencies are installed
# This runs every time the container starts

cd /app/frontend-react

echo "Ensuring frontend dependencies are installed..."
npm install

echo "Checking for missing frontend dependencies..."

# Install @testing-library/dom if not already installed
if ! npm list @testing-library/dom --depth=0 --silent > /dev/null 2>&1; then
  echo "Installing @testing-library/dom..."
  npm install @testing-library/dom --save-dev
else
  echo "@testing-library/dom is already installed."
fi

# Install Stryker dependencies if not already installed
if ! npm list @stryker-mutator/core --depth=0 --silent > /dev/null 2>&1; then
  echo "Installing Stryker packages for mutation testing..."
  npm install @stryker-mutator/core@8.7.1 @stryker-mutator/jest-runner@8.7.1 --save-dev
else
  echo "Stryker packages are already installed."
fi

# Install serve for viewing Stryker reports if not already installed
if ! npm list serve --depth=0 --silent > /dev/null 2>&1; then
  echo "Installing serve package for viewing mutation test reports..."
  npm install serve --save-dev
else
  echo "Serve package is already installed."
fi

# Add any other missing dependencies here
# For example:
# if ! npm list some-package --depth=0 --silent > /dev/null 2>&1; then
#   echo "Installing some-package..."
#   npm install some-package --save-dev
# fi

echo "Frontend dependencies check completed."

# Return to app directory
cd /app 
