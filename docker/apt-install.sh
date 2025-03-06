#!/bin/bash
# apt-install.sh - Space-efficient apt-get install with retries

set -e

MAX_RETRIES=3
DELAY=5

# Create a clean function to aggressively free space
clean_apt_cache() {
    echo "Cleaning apt cache to free up space..."
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    rm -rf /var/cache/apt/archives/*.deb
    # Additional cleanup to ensure minimal space usage
    apt-get autoclean
    rm -rf /tmp/* /var/tmp/*
}

# Pre-clean to ensure we start with maximum available space
clean_apt_cache

# Update package lists with retry
echo "Updating apt package lists..."
for i in $(seq 1 $MAX_RETRIES); do
    if apt-get update -y; then
        break
    fi
    echo "apt-get update failed, retrying in $DELAY seconds... (Attempt $i/$MAX_RETRIES)"
    clean_apt_cache
    sleep $DELAY
    if [ $i -eq $MAX_RETRIES ]; then
        echo "Failed to update apt package lists after $MAX_RETRIES attempts."
        exit 1
    fi
done

# Check disk space before installation
echo "Checking available disk space..."
FREE_SPACE=$(df -k /var/cache/apt/archives/ | tail -1 | awk '{print $4}')
echo "Available space: ${FREE_SPACE}KB"

# Install packages in smaller batches to reduce peak space usage
echo "Installing packages with minimal space usage: $@"
for package in "$@"; do
    echo "Installing package: ${package}"
    for i in $(seq 1 $MAX_RETRIES); do
        if apt-get install -y --no-install-recommends ${package}; then
            # Clean up immediately after each package
            clean_apt_cache
            break
        fi
        echo "apt-get install failed for ${package}, retrying in $DELAY seconds... (Attempt $i/$MAX_RETRIES)"
        clean_apt_cache
        sleep $DELAY
        if [ $i -eq $MAX_RETRIES ]; then
            echo "Failed to install package ${package} after $MAX_RETRIES attempts."
            exit 1
        fi
    done
done

# Final cleanup
clean_apt_cache

echo "Package installation completed successfully."
