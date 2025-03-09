#!/bin/bash

# Script to install Git hooks

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the Git hooks directory
GIT_DIR="$(git rev-parse --git-dir)"
HOOKS_DIR="$GIT_DIR/hooks"

echo "Installing Git hooks from $SCRIPT_DIR to $HOOKS_DIR"

# Make the pre-push hook executable
chmod +x "$SCRIPT_DIR/pre-push"

# Create a symlink to the pre-push hook
ln -sf "$SCRIPT_DIR/pre-push" "$HOOKS_DIR/pre-push"

echo "Git hooks installed successfully!"
echo "The following hooks are now active:"
echo "- pre-push: Automatically bumps version when pushing to dev or prod branches" 