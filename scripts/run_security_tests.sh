#!/bin/bash

# Run Bandit security checks
# Usage: ./scripts/run_security_tests.sh

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Directory for security reports
REPORT_DIR="security_reports"
mkdir -p $REPORT_DIR

# Timestamp for the report
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${YELLOW}Running Bandit security checks...${NC}"

# Run Bandit with HTML report
bandit -c pyproject.toml -r pyerp -f html -o "$REPORT_DIR/bandit_report_$TIMESTAMP.html"
BANDIT_EXIT=$?

# Also generate JSON report for CI/CD integration
bandit -c pyproject.toml -r pyerp -f json -o "$REPORT_DIR/bandit_report_$TIMESTAMP.json"

if [ $BANDIT_EXIT -eq 0 ]; then
    echo -e "${GREEN}No security issues found.${NC}"
elif [ $BANDIT_EXIT -eq 1 ]; then
    echo -e "${RED}Security issues found. Check the report at $REPORT_DIR/bandit_report_$TIMESTAMP.html${NC}"
else
    echo -e "${RED}An error occurred while running Bandit.${NC}"
    exit $BANDIT_EXIT
fi

echo -e "${GREEN}Security reports generated in $REPORT_DIR directory.${NC}"
echo -e "${YELLOW}HTML Report: $REPORT_DIR/bandit_report_$TIMESTAMP.html${NC}"
echo -e "${YELLOW}JSON Report: $REPORT_DIR/bandit_report_$TIMESTAMP.json${NC}"

# Make the report directory browsable by creating an index.html
cat > "$REPORT_DIR/index.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Security Reports</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>Security Reports</h1>
    <p>Latest report: <a href="bandit_report_$TIMESTAMP.html">Bandit Report $TIMESTAMP</a></p>
    <h2>All Reports</h2>
    <ul>
EOF

# Add links to all reports
for report in "$REPORT_DIR"/*.html; do
    if [ "$(basename "$report")" != "index.html" ]; then
        filename=$(basename "$report")
        report_date=$(echo "$filename" | sed -E 's/bandit_report_([0-9]{8}_[0-9]{6}).html/\1/')
        formatted_date=$(date -j -f "%Y%m%d_%H%M%S" "$report_date" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$report_date")
        echo "        <li><a href=\"$filename\">Bandit Report - $formatted_date</a></li>" >> "$REPORT_DIR/index.html"
    fi
done

cat >> "$REPORT_DIR/index.html" << EOF
    </ul>
</body>
</html>
EOF

echo -e "${GREEN}Security testing complete!${NC}" 