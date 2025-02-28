#!/bin/bash

# Export the required environment variables
export DB_PASSWORD=admin123
export MYSQL_ROOT_PASSWORD=rootpassword

# Run the rebuild script with environment variables
sudo -E bash ./scripts/docker_rebuild_with_nginx.sh --branch=master
