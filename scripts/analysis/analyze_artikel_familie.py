"""
Script to analyze the structure of the Artikel_Familie table from the legacy 4D system.
This script uses the WSZ_api getTable functionality to fetch data from Artikel_Familie
and analyze it to help with product categorization.
"""

import os
import sys
import json
from collections import Counter
from pprint import pprint

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    import pandas as pd
    # Import the necessary functions from WSZ_api
    from wsz_api.getTable import fetch_data_from_api
    from wsz_api.auth import get_session_cookie

    def analyze_artikel_familie():
        """
        Fetch data from the Artikel_Familie table and analyze its structure.
        """
        print("Fetching data from Artikel_Familie table...")
        try:
            # Fetch data from the 4D database
            df = fetch_data_from_api("Artikel_Familie")
            
            if df is None or len(df) == 0:
                print("No data returned from Artikel_Familie table")
                return None
            
            print(f"Retrieved {len(df)} records from Artikel_Familie table")
            
            # Print column names and data types
            print("\nColumn Information:")
            for col in df.columns:
                print(f"{col}: {df[col].dtype}")
            
            # Show a sample of records
            print("\nSample Records (first 5):")
            for i in range(min(5, len(df))):
                print(f"\nRecord {i+1}:")
                for col in df.columns:
                    print(f"  {col}: {df.iloc[i][col]}")
            
            # Analyze specific fields that might be useful for categorization
            if 'Name' in df.columns:
                print("\nCategory Names Analysis:")
                name_counter = Counter(df['Name'])
                print(f"Total unique category names: {len(name_counter)}")
                print("\nMost common category names:")
                for name, count in name_counter.most_common(10):
                    print(f"  {name}: {count} occurrences")
            
            # Check for hierarchical structure
            if 'ParentID' in df.columns or 'Parent_ID' in df.columns or 'Eltern_ID' in df.columns:
                parent_col = next((col for col in ['ParentID', 'Parent_ID', 'Eltern_ID'] if col in df.columns), None)
                if parent_col:
                    print(f"\nHierarchy Analysis using {parent_col}:")
                    parent_counts = Counter(df[parent_col].dropna())
                    print(f"Number of unique parent IDs: {len(parent_counts)}")
                    print(f"Number of root categories (no parent): {(df[parent_col].isna() | (df[parent_col] == 0)).sum()}")
                    max_depth = 1
                    # Add logic to calculate max depth of hierarchy if needed
                    print(f"Maximum hierarchy depth: {max_depth}+")
            
            # Return the DataFrame for further processing if needed
            return df
            
        except Exception as e:
            print(f"Error analyzing Artikel_Familie: {e}")
            import traceback
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        # Execute the analysis
        familie_data = analyze_artikel_familie()
        
        # Save to JSON if data was retrieved
        if familie_data is not None:
            try:
                # Convert to records format for easier JSON serialization
                records = familie_data.to_dict(orient='records')
                output_file = 'artikel_familie_analysis.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                print(f"\nSaved {len(records)} records to {output_file}")
            except Exception as e:
                print(f"Error saving data to JSON: {e}")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure the WSZ_api package is available at the specified path.") 