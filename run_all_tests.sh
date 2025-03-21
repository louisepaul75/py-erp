#!/bin/bash

# Display help message
show_help() {
    echo "PyERP Testing Suite"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -t, --type TYPE    Type of tests to run (all, unit, backend, ui, etc.)"
    echo "  -c, --coverage     Generate coverage report"
    echo "  -n, --no-coverage  Disable coverage reporting"
    echo "  -m, --mutation     Run mutation tests"
    echo "  -f, --fuzz         Run fuzz tests"
    echo "  -v, --verbose      Verbose output"
    echo "  -q, --quiet        Quiet output"
    echo ""
    echo "Examples:"
    echo "  $0 -t unit -m      Run unit tests with mutation testing"
    echo "  $0 -t all -f -n    Run all tests with fuzzing and no coverage"
    echo "  $0 -t backend -v   Run backend tests with high verbosity"
}

# Default values
TEST_TYPE="all"
COVERAGE_OPT=""
MUTATION_OPT=""
FUZZ_OPT=""
VERBOSITY_OPT=""

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--type)
            TEST_TYPE="$2"
            shift
            shift
            ;;
        -c|--coverage)
            COVERAGE_OPT=""  # Default is coverage enabled
            shift
            ;;
        -n|--no-coverage)
            COVERAGE_OPT="--no-coverage"
            shift
            ;;
        -m|--mutation)
            MUTATION_OPT="--mutation"
            shift
            ;;
        -f|--fuzz)
            FUZZ_OPT="--fuzz"
            shift
            ;;
        -v|--verbose)
            VERBOSITY_OPT="-v"
            shift
            ;;
        -q|--quiet)
            VERBOSITY_OPT="-q"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Build command
CMD="./scripts/run_tests.sh $TEST_TYPE $COVERAGE_OPT $MUTATION_OPT $FUZZ_OPT $VERBOSITY_OPT"

# Echo command before running
echo "Running: $CMD"
echo "-------------------------------------"

# Execute the command
eval $CMD 