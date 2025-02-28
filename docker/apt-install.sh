#!/bin/bash
# apt-install.sh - Resilient apt-get install with retries

set -e

MAX_RETRIES=3
DELAY=5

# Update package lists with retry
echo "Updating apt package lists..."
for i in $(seq 1 $MAX_RETRIES); do
    if apt-get update -y; then
        break
    fi
    echo "apt-get update failed, retrying in $DELAY seconds... (Attempt $i/$MAX_RETRIES)"
    sleep $DELAY
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Failed to update apt package lists after $MAX_RETRIES attempts."
        exit 1
    fi
done

# Install packages with retry
echo "Installing packages: $@"
for i in $(seq 1 $MAX_RETRIES); do
    if apt-get install -y --no-install-recommends "$@"; then
        break
    fi
    echo "apt-get install failed, retrying in $DELAY seconds... (Attempt $i/$MAX_RETRIES)"
    sleep $DELAY
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Failed to install packages after $MAX_RETRIES attempts."
        exit 1
    fi
done

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "Package installation completed successfully." 