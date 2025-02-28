# pyERP Direct API Scripts

This directory contains utility scripts for interacting with the legacy ERP system using the Direct API module.

## Available Scripts

### getTable.py

A generic script to fetch data from any table in the legacy ERP system.

#### Prerequisites

- Python 3.6+
- Django environment configured
- Access to the legacy ERP system

#### Usage

```bash
# Activate your virtual environment first
cd /path/to/pyERP
.\venv\Scripts\activate

# Basic usage - fetch 100 records from a table
python pyerp/direct_api/scripts/getTable.py table_name

# Fetch all records from a table
python pyerp/direct_api/scripts/getTable.py table_name --all

# Fetch records with filtering
python pyerp/direct_api/scripts/getTable.py table_name --filter "field eq 'value'"

# Save output to a file
python pyerp/direct_api/scripts/getTable.py table_name --output data/output.csv

# Change output format
python pyerp/direct_api/scripts/getTable.py table_name --format json --output data/output.json
python pyerp/direct_api/scripts/getTable.py table_name --format excel --output data/output.xlsx

# Use a different environment
python pyerp/direct_api/scripts/getTable.py table_name --env test

# Fetch records created after a specific date
python pyerp/direct_api/scripts/getTable.py table_name --date-created-start 2023-01-01

# Fetch all data (not just new data)
python pyerp/direct_api/scripts/getTable.py table_name --no-new-data-only

# Enable verbose logging
python pyerp/direct_api/scripts/getTable.py table_name --verbose

# Clear existing session before fetching data
python pyerp/direct_api/scripts/getTable.py table_name --clear-session

# Debug session issues
python pyerp/direct_api/scripts/getTable.py table_name --debug-session
```

#### Options

- `table_name`: Name of the table to fetch data from (required)
- `--env ENV`: Environment to use (default: live)
- `--top N`: Number of records to fetch (default: 100)
- `--skip N`: Number of records to skip (default: 0)
- `--all`: Fetch all records (overrides --top and --skip)
- `--filter FILTER`: Filter query string
- `--output FILE`: Output file (default: stdout)
- `--no-new-data-only`: Fetch all data, not just new data
- `--date-created-start DATE`: Start date for filtering by creation date (YYYY-MM-DD)
- `--format FORMAT`: Output format (csv, json, excel, default: csv)
- `--verbose`: Enable verbose output
- `--clear-session`: Clear existing session before fetching data
- `--debug-session`: Enable detailed session debugging

#### Examples

1. Fetch customers created after January 1, 2023:
```bash
python pyerp/direct_api/scripts/getTable.py Customers --date-created-start 2023-01-01
```

2. Fetch all active products and save as JSON:
```bash
python pyerp/direct_api/scripts/getTable.py Products --filter "active eq true" --format json --output data/active_products.json
```

3. Fetch the first 500 orders:
```bash
python pyerp/direct_api/scripts/getTable.py Orders --top 500
```

4. Fetch all orders from the test environment:
```bash
python pyerp/direct_api/scripts/getTable.py Orders --all --env test
```

#### Customizing the Script

You can also customize the script by modifying the `if __name__ == '__main__':` section to hardcode specific table names or parameters:

1. Open the `getTable.py` file in your editor
2. Locate the `if __name__ == '__main__':` section at the bottom of the file
3. Uncomment and modify the example code to specify your table name and parameters:

```python
if __name__ == '__main__':
    # Example 1: Use command line arguments
    # main()
    
    # Example 2: Hardcode the table name and other parameters
    fetch_table(
        table_name="Customers",
        env="live",
        all_records=True,
        output_format="json"
    )
```

This allows you to create specialized versions of the script for specific tables without having to pass command-line arguments each time.

#### Session Management

The script is designed to efficiently manage API sessions to minimize the number of sessions created on the legacy ERP server:

1. **Single Global Session**: The script now uses a single global client and session cookie for all requests, ensuring that only one session is created regardless of how many tables you fetch.

2. **Session Forcing**: The `--clear-session` flag invalidates the current session and creates a new one, useful if you encounter authentication issues.

3. **Session Debugging**: The `--debug-session` flag provides detailed information about the session, including:
   - Session cookie file location and content
   - Session object details
   - Session validity
   - Test connection to verify the session works

4. **Monkey Patching**: The script now monkey patches the client's request method to ensure it always uses the same session cookie, preventing the creation of multiple sessions.

If you're experiencing issues with multiple sessions being created, try these steps:

1. Run the script with the `--debug-session` flag to get detailed information about the session:
   ```bash
   python pyerp/direct_api/scripts/getTable.py table_name --debug-session
   ```

2. Clear any existing sessions and start fresh:
   ```bash
   python pyerp/direct_api/scripts/getTable.py table_name --clear-session --debug-session
   ```

3. Check the legacy ERP server logs to see if multiple sessions are still being created

4. Ensure you're not running multiple instances of the script simultaneously 