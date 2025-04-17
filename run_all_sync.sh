#!/bin/bash

# run_all_sync.sh - Script to run data synchronization commands
# Usage: ./run_all_sync.sh [--customers-only] [--products-only] [--employees-only] [--sales-only] [--images-only] [--bb-creditors-only] [--bb-receipts-inbound-only] [--bb-receipts-outbound-only] [--days N] [--debug] [--force-update] [--top N]

# Set default values
DEBUG=0
CUSTOMERS_ONLY=0
PRODUCTS_ONLY=0
EMPLOYEES_ONLY=0
SALES_ONLY=0
IMAGES_ONLY=0
BB_CREDITORS_ONLY=0
BB_RECEIPTS_INBOUND_ONLY=0
BB_RECEIPTS_OUTBOUND_ONLY=0
FORCE_UPDATE=0
TOP_VALUE=0
DAYS_VALUE=0
EXTRA_FLAGS=""

# Process command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --debug)
        DEBUG=1
        EXTRA_FLAGS+=" --debug"
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
        --employees-only)
        EMPLOYEES_ONLY=1
        shift
        ;;
        --sales-only)
        SALES_ONLY=1
        shift
        ;;
        --images-only)
        IMAGES_ONLY=1
        shift
        ;;
        --bb-creditors-only)
        BB_CREDITORS_ONLY=1
        shift
        ;;
        --bb-receipts-inbound-only)
        BB_RECEIPTS_INBOUND_ONLY=1
        shift
        ;;
        --bb-receipts-outbound-only)
        BB_RECEIPTS_OUTBOUND_ONLY=1
        shift
        ;;
        --force-update)
        FORCE_UPDATE=1
        EXTRA_FLAGS+=" --force-update"
        shift
        ;;
        --top=*)
        TOP_VALUE="${1#*=}"
        EXTRA_FLAGS+=" --top=${TOP_VALUE}"
        shift
        ;;
        --top)
        if [[ -n "$2" && "$2" != --* ]]; then
            TOP_VALUE="$2"
            EXTRA_FLAGS+=" --top=${TOP_VALUE}"
            shift 2
        else
            echo "Error: Argument for --top is missing" >&2
            exit 1
        fi
        ;;
        --days=*)
        DAYS_VALUE="${1#*=}"
        EXTRA_FLAGS+=" --days=${DAYS_VALUE}"
        shift
        ;;
        --days)
        if [[ -n "$2" && "$2" != --* ]]; then
            DAYS_VALUE="$2"
            EXTRA_FLAGS+=" --days=${DAYS_VALUE}"
            shift 2
        else
            echo "Error: Argument for --days is missing" >&2
            exit 1
        fi
        ;;
        *)
        echo "Unknown option: $1" >&2
        shift
        ;;
    esac
done

# Report settings based on flags collected
if [ $DEBUG -eq 1 ]; then
    echo "Debug mode enabled"
fi
if [ $FORCE_UPDATE -eq 1 ]; then
    echo "Force update enabled"
fi
if [ $TOP_VALUE -gt 0 ]; then
    echo "Top limit set to $TOP_VALUE"
fi
if [ $DAYS_VALUE -gt 0 ]; then
    echo "Days filter set to $DAYS_VALUE"
fi

# Function to run a sync command with proper output formatting
run_sync() {
    COMMAND=$1
    FLAGS=$2
    # Remove leading/trailing whitespace from FLAGS just in case
    FLAGS=$(echo "$FLAGS" | xargs)
    echo "========================================"
    printf "Running: %s %s\n" "$COMMAND" "$FLAGS"
    echo "========================================"
    eval "$COMMAND $FLAGS"
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
    
    export LEGACY_ERP_ENVIRONMENT="live"
    export LEGACY_ERP_TABLE_NAME="Kunden"
    
    run_sync "python manage.py run_sync --entity-type customer" "$EXTRA_FLAGS"
    return $?
}

# Function to run employee sync with environment variables
run_employee_sync() {
    echo "========================================"
    echo "Running employees sync with fixed environment"
    echo "========================================"
    
    export LEGACY_ERP_ENVIRONMENT="live"
    export LEGACY_ERP_TABLE_NAME="Personal"
    
    run_sync "python manage.py run_sync --entity-type employee" "$EXTRA_FLAGS"
    return $?
}

# Function to run sales record sync
run_sales_sync() {
    echo "========================================"
    echo "Running sales records sync"
    echo "========================================"
    run_sync "python manage.py sync_sales_records" "$EXTRA_FLAGS"
    return $?
}

# Function to run image sync
run_images_sync() {
    echo "========================================"
    echo "Running product images sync"
    echo "========================================"
    run_sync "python manage.py sync_product_images" "$EXTRA_FLAGS"
    return $?
}

# Function to run Buchhaltungsbutler Creditor sync
run_bb_creditors_sync() {
    echo "========================================"
    echo "Running Buchhaltungsbutler Creditors sync"
    echo "========================================"
    # Assuming 'bb_creditors' is the configuration name in settings/DB
    run_sync "python manage.py run_sync --config-name bb_creditors" "$EXTRA_FLAGS"
    return $?
}

# Function to run Buchhaltungsbutler Inbound Receipts sync
run_bb_receipts_inbound_sync() {
    echo "========================================"
    echo "Running Buchhaltungsbutler Inbound Receipts sync"
    echo "========================================"
    # Assuming 'bb_receipts_inbound' is the configuration name
    run_sync "python manage.py run_sync --config-name bb_receipts_inbound" "$EXTRA_FLAGS"
    return $?
}

# Function to run Buchhaltungsbutler Outbound Receipts sync
run_bb_receipts_outbound_sync() {
    echo "========================================"
    echo "Running Buchhaltungsbutler Outbound Receipts sync"
    echo "========================================"
    # Assuming 'bb_receipts_outbound' is the configuration name
    run_sync "python manage.py run_sync --config-name bb_receipts_outbound" "$EXTRA_FLAGS"
    return $?
}

# Determine which sync processes to run
if [ $CUSTOMERS_ONLY -eq 1 ]; then
    echo "Running customers sync only"
    run_customer_sync
    exit $?
elif [ $PRODUCTS_ONLY -eq 1 ]; then
    echo "Running products sync only"
    run_sync "python manage.py sync_products" "$EXTRA_FLAGS"
    exit $?
elif [ $EMPLOYEES_ONLY -eq 1 ]; then
    echo "Running employees sync only"
    run_employee_sync
    exit $?
elif [ $SALES_ONLY -eq 1 ]; then
    echo "Running sales records sync only"
    run_sales_sync
    exit $?
elif [ $IMAGES_ONLY -eq 1 ]; then
    echo "Running product images sync only"
    run_images_sync
    exit $?
elif [ $BB_CREDITORS_ONLY -eq 1 ]; then
    echo "Running Buchhaltungsbutler Creditors sync only"
    run_bb_creditors_sync
    exit $?
elif [ $BB_RECEIPTS_INBOUND_ONLY -eq 1 ]; then
    echo "Running Buchhaltungsbutler Inbound Receipts sync only"
    run_bb_receipts_inbound_sync
    exit $?
elif [ $BB_RECEIPTS_OUTBOUND_ONLY -eq 1 ]; then
    echo "Running Buchhaltungsbutler Outbound Receipts sync only"
    run_bb_receipts_outbound_sync
    exit $?
else
    echo "Running all sync processes"
    
    run_customer_sync
    CUSTOMER_EXIT=$?
    
    run_sync "python manage.py sync_products" "$EXTRA_FLAGS"
    PRODUCT_EXIT=$?
    
    run_sync "python manage.py sync_inventory" "$EXTRA_FLAGS"
    INVENTORY_EXIT=$?
    
    run_employee_sync
    EMPLOYEE_EXIT=$?
    
    run_sales_sync
    SALES_EXIT=$?

    run_images_sync
    IMAGES_EXIT=$?

    run_bb_creditors_sync
    BB_CREDITORS_EXIT=$?

    run_bb_receipts_inbound_sync
    BB_RECEIPTS_INBOUND_EXIT=$?

    run_bb_receipts_outbound_sync
    BB_RECEIPTS_OUTBOUND_EXIT=$?
    
    if [ $CUSTOMER_EXIT -ne 0 ] || \
       [ $PRODUCT_EXIT -ne 0 ] || \
       [ $INVENTORY_EXIT -ne 0 ] || \
       [ $EMPLOYEE_EXIT -ne 0 ] || \
       [ $SALES_EXIT -ne 0 ] || \
       [ $IMAGES_EXIT -ne 0 ] || \
       [ $BB_CREDITORS_EXIT -ne 0 ] || \
       [ $BB_RECEIPTS_INBOUND_EXIT -ne 0 ] || \
       [ $BB_RECEIPTS_OUTBOUND_EXIT -ne 0 ]; then
        echo "One or more sync processes failed"
        exit 1
    else
        echo "All sync processes completed successfully"
        exit 0
    fi
fi 