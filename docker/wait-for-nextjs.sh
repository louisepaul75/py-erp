#!/bin/bash
# wait-for-nextjs.sh

set -e

# Host and port for Next.js (must match Nginx proxy_pass and Next.js listen address)
host="127.0.0.1"
port="3000"
# Nginx command will be executed directly below

echo "Waiting for Next.js on $host:$port..."

# Add a small initial delay
sleep 2

# Loop until the server responds to a simple curl request
# Use --fail to exit with non-zero status on HTTP errors (4xx, 5xx)
# Use -s for silent mode, -o /dev/null to discard output
# Check the hardcoded host IP
while ! curl -fsSo /dev/null http://$host:$port; do
  echo "Next.js is unavailable (checking $host:$port) - sleeping"
  sleep 1
done

echo "Next.js is up - executing Nginx directly..."
# Execute nginx directly, passing arguments separately
exec /usr/sbin/nginx -g 'daemon off;'
