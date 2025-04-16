#!/bin/bash

# Initialize variables for optional parameters
RUN_TESTS=""
USE_CACHE="yes"
START_MONITORING="no" # Default to not starting monitoring services

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tests)
            if [ -z "$2" ]; then
                echo "Error: --tests requires a parameter (e.g. ui)"
                exit 1
            fi
            RUN_TESTS="$2"
            shift 2
            ;;
        --no-cache)
            USE_CACHE="no"
            shift
            ;;
        --with-monitoring) # Flag to explicitly start monitoring services
            START_MONITORING="yes"
            shift
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--tests ui] [--no-cache] [--with-monitoring]"
            exit 1
            ;;
    esac
done

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Define compose file path
COMPOSE_FILE="docker/docker-compose.dev.yml"

# Stop and remove existing containers defined in the compose file
# This ensures a clean state, stopping all services including monitoring if it was running
echo "Stopping and removing existing docker-compose services..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true

# Rebuild Docker images defined in the compose file
if [ "$USE_CACHE" == "no" ]; then
    echo "Rebuilding Docker images (no cache)..."
    # We rebuild all services defined in the file, even if not starting monitoring now
    docker-compose -f "$COMPOSE_FILE" build --no-cache
else
    echo "Rebuilding Docker images (using cache)..."
    docker-compose -f "$COMPOSE_FILE" build
fi

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "Error: Docker compose build failed."
    exit 1
fi

# Create necessary host directories (compose volumes handle container dirs)
mkdir -p static media logs data

# Clean the host logs directory before mounting it
echo "Cleaning host logs directory..."
rm -rf ./logs/*

# Determine which services to start
SERVICES_TO_START="pyerp-app zebra-day"
if [ "$START_MONITORING" == "yes" ]; then
    echo "Monitoring services will be started (--with-monitoring flag detected)."
    SERVICES_TO_START="$SERVICES_TO_START pyerp-elastic-kibana"
else
    echo "Monitoring services will NOT be started (use --with-monitoring to include them)."
fi

# Start the selected services defined in the compose file in detached mode
echo "Starting docker-compose services: $SERVICES_TO_START..."
docker-compose -f "$COMPOSE_FILE" up -d $SERVICES_TO_START

# Check if compose up was successful
if [ $? -ne 0 ]; then
    echo "Error: docker-compose up failed."
    exit 1
fi

# Show the last 50 lines of container logs for the main app
echo "Showing last 50 lines of pyerp-app logs..."
docker-compose -f "$COMPOSE_FILE" logs --tail 50 pyerp-app || true

# Run tests only if the --tests parameter was provided
if [ -n "$RUN_TESTS" ]; then
    echo "Waiting a few seconds for services to stabilize before running tests..."
    sleep 5 # Give services a moment to start
    case "$RUN_TESTS" in
        "ui")
            echo "Running frontend tests in pyerp-app container..."
            docker-compose -f "$COMPOSE_FILE" exec pyerp-app bash -c "cd /app/frontend-react && npm test -- --silent || echo 'Tests may fail initially, but the setup is complete.'"
            ;;
        *)
            echo "Unknown test type: $RUN_TESTS"
            echo "Supported test types: ui"
            ;;
    esac
fi

echo -e "\nServices are running in the background. Use 'docker-compose -f $COMPOSE_FILE logs [SERVICE_NAME]' to view logs."

# Display monitoring information based on whether it was started
if [ "$START_MONITORING" == "yes" ]; then
    echo -e "\nMonitoring services (internal ELK stack) were started:"
    echo -e "- Elasticsearch: http://localhost:9200 (exposed via pyerp-elastic-kibana service)"
    echo -e "- Kibana: http://localhost:5602 (exposed via pyerp-elastic-kibana service port mapping 5602:5601)"
else
    echo -e "\nMonitoring services were NOT started. Use the --with-monitoring flag to include them."
fi

echo -e "To run frontend tests manually, use: docker-compose -f $COMPOSE_FILE exec pyerp-app bash -c 'cd /app/frontend-react && npm test'"

echo "Waiting 10 seconds before starting health checks..."
sleep 10

# --- Health Checks ---
echo -e "\n--- Running Health Checks ---"
MAX_RETRIES=24
RETRY_DELAY=5
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
ZEBRA_URL="http://localhost:8118" # Health check for zebra_day

# Function to check if a compose service is running
check_service_running() {
    local service_name=$1
    docker-compose -f "$COMPOSE_FILE" ps -q "$service_name" 2>/dev/null | grep -q . 
}

# Check Next.js Frontend (pyerp-app)
if check_service_running pyerp-app; then
    echo "Checking Next.js frontend ($FRONTEND_URL)..."
    FRONTEND_SUCCESS=false
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -fsS $FRONTEND_URL > /dev/null; then
            echo "✅ Next.js frontend is responsive."
            FRONTEND_SUCCESS=true
            break
        fi
        if ! check_service_running pyerp-app; then
            echo "❌ Error: Service pyerp-app seems to have stopped during check."
            break
        fi
        echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    done
    if [ "$FRONTEND_SUCCESS" = false ] && check_service_running pyerp-app; then
        echo "❌ Error: Next.js frontend failed to respond after $MAX_RETRIES attempts."
    fi
else
     echo "Skipping Next.js health check because pyerp-app service is not running."
fi

# Check Django Backend (pyerp-app)
if check_service_running pyerp-app; then
    echo "Checking Django backend ($BACKEND_URL)..."
    BACKEND_SUCCESS=false
    for i in $(seq 1 $MAX_RETRIES); do
        if curl -fsS --head $BACKEND_URL/api/health/ > /dev/null; then # Check health endpoint
            echo "✅ Django backend is responsive."
            BACKEND_SUCCESS=true
            break
        fi
        if ! check_service_running pyerp-app; then
            echo "❌ Error: Service pyerp-app seems to have stopped during check."
            break
        fi
        echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    done
    if [ "$BACKEND_SUCCESS" = false ] && check_service_running pyerp-app; then
        echo "❌ Error: Django backend failed to respond after $MAX_RETRIES attempts."
    fi
else
     echo "Skipping Django health check because pyerp-app service is not running."
fi

# Check Zebra Day Service (zebra-day)
if check_service_running zebra-day; then
    echo "Checking Zebra Day service ($ZEBRA_URL)..."
    ZEBRA_SUCCESS=false
    for i in $(seq 1 $MAX_RETRIES); do
        # Zebra day base URL might just return the UI html
        if curl -fsS $ZEBRA_URL > /dev/null; then 
            echo "✅ Zebra Day service is responsive."
            ZEBRA_SUCCESS=true
            break
        fi
        if ! check_service_running zebra-day; then
            echo "❌ Error: Service zebra-day seems to have stopped during check."
            break
        fi
        echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    done
    if [ "$ZEBRA_SUCCESS" = false ] && check_service_running zebra-day; then
        echo "❌ Error: Zebra Day service failed to respond after $MAX_RETRIES attempts."
    fi
else
    echo "Skipping Zebra Day health check because zebra-day service is not running."
fi

echo "--- Health Checks Complete ---"

# --- Check Database Connection Source --- (Only if pyerp-app is running)
if check_service_running pyerp-app; then
    echo -e "\n--- Checking Database Connection Source in pyerp-app Logs ---"
    db_source_check_log=$(docker-compose -f "$COMPOSE_FILE" logs pyerp-app 2>&1 | grep -E 'Database settings source:' | tail -n 1)

    if [[ -z "$db_source_check_log" ]]; then
        echo "❌ Database source log line not found."
        echo "   Attempting to retrieve full logs for inspection..."
        docker-compose -f "$COMPOSE_FILE" logs pyerp-app || true
    elif [[ "$db_source_check_log" == *"1Password"* ]]; then
        echo "✅ Database connected using 1Password credentials."
        echo "   Log line found: '$db_source_check_log'"
    elif [[ "$db_source_check_log" == *"environment variables"* ]]; then
        echo "⚠️ Database connected using environment variables (not 1Password)."
        echo "   Log line found: '$db_source_check_log'"
    else
        echo "❓ Unknown database connection source state."
        echo "   Log line found: '$db_source_check_log'"
    fi
    echo "--- Database Check Complete ---"
else
    echo -e "\nSkipping Database Connection Source check because pyerp-app service is not running."
fi
