#!/usr/bin/env python
import sys
import os
import argparse
import pandas as pd
import json
import traceback

# Add the WSZ_api package to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
    from wsz_api.auth import get_session_cookie
    print("Successfully imported WSZ_api modules")
except ImportError as e:
    print(f"Error importing WSZ_api modules: {e}")
    sys.exit(1)

def main() -> None:
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description='Query the legacy API')
        parser.add_argument('--table', type=str, required=True, help='Table name to query')
        parser.add_argument('--limit', type=int, default=3, help='Max number of records to return')
        parser.add_argument('--skip', type=int, default=0, help='Number of records to skip')
        parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
        parser.add_argument('--output', type=str, help='Output file path (optional)')
        args = parser.parse_args()

        # Get a session cookie
        print("Getting session cookie...")
        try:
            cookie = get_session_cookie(mode='live')
            print("Successfully got session cookie")
        except Exception as e:
            print(f"Error getting session cookie: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        print(f"Fetching data from {args.table} table (limit: {args.limit}, skip: {args.skip})...")
        
        # Fetch data from the API
        try:
            df = fetch_data_from_api(
                table_name=args.table,
                top=args.limit,
                skip=args.skip,
                new_data_only=False  # We want all data, not just new data
            )
            print(f"Successfully fetched {len(df)} records.")
        except Exception as e:
            print(f"Error fetching data: {e}")
            traceback.print_exc()
            sys.exit(1)
        
        # Check if we got any data
        if df.empty:
            print("No data returned from API")
            sys.exit(0)
        
        # Output data
        if args.output:
            if args.format == 'json':
                with open(args.output, 'w') as f:
                    f.write(df.to_json(orient='records', indent=2))
            else:
                df.to_csv(args.output, index=False)
            print(f"Data saved to {args.output}")
        else:
            # Output to console
            if args.format == 'json':
                # Convert to JSON and pretty-print
                json_data = json.loads(df.to_json(orient='records'))
                print(json.dumps(json_data, indent=2))
            else:
                # Output as CSV
                print(df.to_csv(index=False))
        
        # Print column information
        print("\nColumn Information:")
        for column in df.columns:
            print(f"- {column} (dtype: {df[column].dtype})")
            # Print sample values (non-null)
            non_null_values = df[column].dropna()
            if not non_null_values.empty:
                sample_value = non_null_values.iloc[0]
                print(f"  Sample value: {sample_value}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 