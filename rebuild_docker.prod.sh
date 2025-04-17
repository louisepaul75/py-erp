#!/bin/bash

# Default values
RUN_TESTS=true
RUN_MONITORING=true
DEBUG_MODE=false
LOCAL_HTTPS_MODE=false
PROFILE_MEMORY=false
NO_CACHE_BUILD=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --no-tests) RUN_TESTS=false; shift ;;
        --no-monitoring) RUN_MONITORING=false; shift ;;
        --debug) DEBUG_MODE=true; shift ;;
        --local-https) LOCAL_HTTPS_MODE=true; shift ;;
        --profile-memory) PROFILE_MEMORY=true; shift ;;
        --no-cache-build) NO_CACHE_BUILD=true; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Ensure we're in the project root directory
cd "$(dirname "$0")"

# Announce test skipping early if flag is set
if [ "$RUN_TESTS" = false ]; then
    echo "Skipping tests as requested via --no-tests flag."
    echo ""
fi

# Define compose file paths
COMPOSE_FILE="docker/docker-compose.prod.yml"
MONITORING_COMPOSE_FILE="docker/docker-compose.monitoring.yml"

# Stop and remove existing containers managed by the main compose file
echo "Stopping and removing existing main docker-compose services..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans || true

# Stop and remove monitoring container if it exists
if [ -f "$MONITORING_COMPOSE_FILE" ]; then
    echo "Stopping and removing existing monitoring services..."
    docker-compose -f "$MONITORING_COMPOSE_FILE" down --remove-orphans || true
else
    echo "Monitoring compose file ($MONITORING_COMPOSE_FILE) not found, skipping monitoring stop."
fi

# Build Docker images defined in the main compose file
echo "Building Docker images defined in $COMPOSE_FILE..."
BUILD_ARGS=""
if [ "$NO_CACHE_BUILD" = true ]; then
    echo "Using --no-cache flag for build..."
    BUILD_ARGS="--no-cache"
fi
docker-compose -f "$COMPOSE_FILE" build $BUILD_ARGS
if [ $? -ne 0 ]; then
    echo "Error: Docker compose build failed."
    exit 1
fi

# Ensure the host directory for memory snapshots exists
mkdir -p ./memory_snapshots_output/memory_snapshots

# Choose environment file based on mode (used by compose implicitly if named .env or explicitly via --env-file in command)
ENV_FILE="config/env/.env.prod"
if [ "$DEBUG_MODE" = true ]; then
    ENV_FILE="config/env/.env.prod.local"
    echo "Using debug environment file: $ENV_FILE"
else
    echo "Using production environment file: $ENV_FILE"
fi

# Prepare compose command arguments for optional features
COMPOSE_UP_ARGS="-d"
if [ "$DEBUG_MODE" = true ]; then
    COMPOSE_UP_ARGS="$COMPOSE_UP_ARGS --env-file $ENV_FILE"
# else compose uses default .env or the env_file specified in compose file
fi

# Start main services
echo "Starting main docker-compose services from $COMPOSE_FILE..."
docker-compose -f "$COMPOSE_FILE" up $COMPOSE_UP_ARGS
if [ $? -ne 0 ]; then
    echo "Error: docker-compose up failed for $COMPOSE_FILE."
    exit 1
fi

# Set environment variables within the running container for optional features
if [ "$PROFILE_MEMORY" = true ]; then
    echo "Enabling memory profiling in pyerp container..."
    docker-compose -f "$COMPOSE_FILE" exec -T pyerp bash -c "export ENABLE_MEMORY_PROFILING=true"
fi
if [ "$LOCAL_HTTPS_MODE" = true ]; then
    echo "Enabling local HTTPS proxy in pyerp container..."
    docker-compose -f "$COMPOSE_FILE" exec -T pyerp bash -c "export USE_LOCAL_HTTPS_PROXY=true"
fi

echo -e "\nServices from $COMPOSE_FILE are running in the background. Use 'docker-compose -f $COMPOSE_FILE logs' to view logs."
echo -e "Zebra Day service (zebra-day) is expected to be running as part of the main services."

# --- Check Database Connection Source ---
echo -e "\n--- Verifying Database Connection Source in pyerp Logs ---"
echo "Waiting 15 seconds for application logs to populate..."
sleep 15

DB_SOURCE_CHECK_SUCCESS=false
DB_SOURCE_LOG_LINE=""
for i in $(seq 1 3); do 
    DB_SOURCE_LOG_LINE=$(docker-compose -f "$COMPOSE_FILE" logs pyerp 2>&1 | grep -E 'Database settings source:' | tail -n 1)
    if [[ -n "$DB_SOURCE_LOG_LINE" ]]; then
        if [[ "$DB_SOURCE_LOG_LINE" == *"1Password"* ]]; then
            echo "✅ Database successfully connected using 1Password credentials."
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            DB_SOURCE_CHECK_SUCCESS=true
            break
        elif [[ "$DB_SOURCE_LOG_LINE" == *"environment variables"* ]]; then
            echo "❌ ERROR: Database connected using environment variables, not 1Password!"
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            echo "   Stopping build process as 1Password connection failed."
            docker-compose -f "$COMPOSE_FILE" down # Stop services on failure
            exit 1 # Exit script with error
        else
            echo "❓ Unknown database connection source state on attempt $i."
            echo "   Log line found: '$DB_SOURCE_LOG_LINE'"
            # Keep DB_SOURCE_CHECK_SUCCESS as false
        fi
    else
        echo "⚠️ Database source log line not found yet (attempt $i). Waiting..."
        # Keep DB_SOURCE_CHECK_SUCCESS as false
    fi
    if [ "$DB_SOURCE_CHECK_SUCCESS" = false ]; then
        sleep 5
    fi
done

if [ "$DB_SOURCE_CHECK_SUCCESS" = false ]; then
    echo "❌ ERROR: Failed to verify database connection source after multiple attempts."
    echo "   Could not find the 'Database settings source:' log line or it indicated failure."
    echo "   Last checked line (if any): '$DB_SOURCE_LOG_LINE'"
    echo "   Stopping build process."
    docker-compose -f "$COMPOSE_FILE" down # Stop services on failure
    exit 1 # Exit script with error
fi
echo "--- Database Check Complete ---"

# Start the monitoring container unless skipped
if [ "$RUN_MONITORING" = true ]; then
    if [ -f "$MONITORING_COMPOSE_FILE" ]; then
        echo "Starting monitoring services from $MONITORING_COMPOSE_FILE..."
        docker-compose -f "$MONITORING_COMPOSE_FILE" up -d
        if [ $? -ne 0 ]; then
            echo "Error: docker-compose up failed for $MONITORING_COMPOSE_FILE."
            # Decide if this is critical enough to stop
        else 
            echo -e "\nMonitoring services started:"
            echo -e "- Elasticsearch: http://localhost:9200 (usually)"
            echo -e "- Kibana: http://localhost:5601 (usually)"
            echo -e "Check $MONITORING_COMPOSE_FILE for actual port mappings."
            echo -e "Monitoring container logs: docker-compose -f $MONITORING_COMPOSE_FILE logs"
            
            # Simplified wait/check for monitoring stack - adjust as needed
            echo "Waiting up to 60 seconds for Elasticsearch (monitoring) to become available..."
            for i in {1..12}; do
                # Adjust URL/port if monitoring compose maps differently
                if curl -s http://localhost:9200 > /dev/null; then 
                    echo "Monitoring Elasticsearch appears ready!"
                    break
                fi
                echo "Waiting... attempt $i of 12"
                sleep 5
                if [ $i -eq 12 ]; then
                    echo "Warning: Monitoring Elasticsearch did not respond in time. It might still be starting."
                fi
            done
        fi
    else
        echo "Warning: Monitoring compose file ($MONITORING_COMPOSE_FILE) not found. Cannot start monitoring services."
    fi
else
    echo "Skipping monitoring setup as requested."
fi

echo "Waiting 10 seconds before starting health checks..."
sleep 10

# --- Health Checks ---
echo -e "\n--- Running Health Checks ---"
MAX_RETRIES=12
RETRY_DELAY=5
APP_URL="http://localhost:80" # Nginx/proxy likely serves on 80
ZEBRA_HOST="zebra-day" # Internal service name
ZEBRA_PORT=8118 # Internal service port

# Function to check if a compose service is running
check_compose_service_running() {
    local compose_file=$1
    local service_name=$2
    docker-compose -f "$compose_file" ps -q "$service_name" | grep -q . 
}

# Check Main Application Endpoint (pyerp service)
echo "Checking main application endpoint ($APP_URL)..."
APP_SUCCESS=false
for i in $(seq 1 $MAX_RETRIES); do
    if curl -fsSL --head $APP_URL > /dev/null; then
        echo "✅ Main application endpoint is responsive."
        APP_SUCCESS=true
        break
    fi
    if ! check_compose_service_running "$COMPOSE_FILE" pyerp; then
        echo "❌ Error: Service pyerp seems to have stopped."
        break
    fi
    echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
    sleep $RETRY_DELAY
done
if [ "$APP_SUCCESS" = false ] && check_compose_service_running "$COMPOSE_FILE" pyerp; then
    echo "❌ Error: Main application endpoint failed to respond after $MAX_RETRIES attempts."
    echo "Please check logs: docker-compose -f $COMPOSE_FILE logs pyerp"
fi

# Check Zebra Day Service (zebra-day service, internally)
# We check this by exec'ing into pyerp and curling the internal service name
echo "Checking Zebra Day service (internally from pyerp)..."
ZEBRA_SUCCESS=false
if check_compose_service_running "$COMPOSE_FILE" pyerp && check_compose_service_running "$COMPOSE_FILE" zebra-day; then
    for i in $(seq 1 $MAX_RETRIES); do
        # Curl from pyerp to zebra-day using internal service name and port
        if docker-compose -f "$COMPOSE_FILE" exec -T pyerp curl -fsS http://$ZEBRA_HOST:$ZEBRA_PORT > /dev/null; then 
            echo "✅ Zebra Day service is responsive internally."
            ZEBRA_SUCCESS=true
            break
        fi
        echo "Attempt $i/$MAX_RETRIES failed. Retrying in $RETRY_DELAY seconds..."
        sleep $RETRY_DELAY
    done
    if [ "$ZEBRA_SUCCESS" = false ]; then
        echo "❌ Error: Zebra Day service failed to respond internally after $MAX_RETRIES attempts."
        echo "Please check logs: docker-compose -f $COMPOSE_FILE logs zebra-day"
    fi
else
    echo "Skipping Zebra Day health check because pyerp or zebra-day service is not running."
fi

echo "--- Health Checks Complete ---"

# Run tests inside the container if requested and main app is healthy
if [ "$RUN_TESTS" = true ]; then
  if [ "$APP_SUCCESS" = true ]; then
      echo -e "\n--- Running Tests Inside Container ---"
      echo "Executing tests within the pyerp container..."
      # Assuming ./run_all_tests.sh is executable and in the default working dir of the pyerp container
      docker-compose -f "$COMPOSE_FILE" exec pyerp ./run_all_tests.sh
      if [ $? -ne 0 ]; then
          echo "❌ Tests failed inside the container. Check container logs or run manually:"
          echo "   docker-compose -f $COMPOSE_FILE exec pyerp /bin/bash"
          echo "   (cd to appropriate directory if needed)"
          echo "   ./run_all_tests.sh"
          # Consider adding 'exit 1' here if test failure should stop the script
      else
          echo "✅ Tests passed inside the container."
      fi
      echo "--- Test Execution Complete ---"
  else
      echo -e "\nSkipping tests because the main application health check failed."
  fi
fi
