#!/bin/bash

# run_all_sync.sh - Script to run data synchronization commands
# Usage: ./run_all_sync.sh [--customers-only] [--products-only] [--debug]

# Set default values
DEBUG=0
CUSTOMERS_ONLY=0
PRODUCTS_ONLY=0
FORCE_UPDATE=0

# Process command line arguments
for arg in "$@"
do
    case $arg in
        --debug)
        DEBUG=1
        shift
        ;;
        --customers-only)
        CUSTOMERS_ONLY=1
        shift
        ;;
        --products-only)
        PRODUCTS_ONLY=1
        shift
        ;;
        --force-update)
        FORCE_UPDATE=1
        shift
        ;;
        *)
        # Unknown option
        shift
        ;;
    esac
done

# Set up debug flag
DEBUG_FLAG=""
if [ $DEBUG -eq 1 ]; then
    DEBUG_FLAG="--debug"
    echo "Debug mode enabled"
fi

# Set up force update flag
FORCE_FLAG=""
if [ $FORCE_UPDATE -eq 1 ]; then
    FORCE_FLAG="--force-update"
    echo "Force update enabled"
fi

# Function to run a sync command with proper output formatting
run_sync() {
    echo "========================================"
    echo "Running: $1"
    echo "========================================"
    eval "$1"
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Command failed with exit code $EXIT_CODE"
    fi
    echo ""
    return $EXIT_CODE
}

# Function to run customer sync with environment variables
run_customer_sync() {
    echo "========================================"
    echo "Running customers sync with fixed environment"
    echo "========================================"
    
    # Set environment variables required by the extractor
    export LEGACY_ERP_TABLE_NAME="Kunden"
    export LEGACY_ERP_ENVIRONMENT="live"
    
    # Run the command directly with the entity type flag
    run_sync "python manage.py run_sync --entity-type customer $DEBUG_FLAG $FORCE_FLAG"
    return $?
}

# Determine which sync processes to run
if [ $CUSTOMERS_ONLY -eq 1 ]; then
    echo "Running customers sync only"
    run_customer_sync
    exit $?
elif [ $PRODUCTS_ONLY -eq 1 ]; then
    echo "Running products sync only"
    run_sync "python manage.py sync_products $DEBUG_FLAG $FORCE_FLAG"
    exit $?
else
    echo "Running all sync processes"
    
    # Run customer sync first
    run_customer_sync
    CUSTOMER_EXIT=$?
    
    # Run product sync
    run_sync "python manage.py sync_products $DEBUG_FLAG $FORCE_FLAG"
    PRODUCT_EXIT=$?
    
    # Run inventory sync
    run_sync "python manage.py sync_inventory $DEBUG_FLAG $FORCE_FLAG"
    INVENTORY_EXIT=$?
    
    # Report overall status
    if [ $CUSTOMER_EXIT -ne 0 ] || [ $PRODUCT_EXIT -ne 0 ] || [ $INVENTORY_EXIT -ne 0 ]; then
        echo "One or more sync processes failed"
        exit 1
    else
        echo "All sync processes completed successfully"
        exit 0
    fi
fi 