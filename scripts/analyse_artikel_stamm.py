"""
Script to analyze the structure of the Artikel_Stamm table from the legacy 4D system.
This script fetches data using the WSZ_API and prints out information about the
structure of the data to help design the appropriate Django model.
"""

import os
import sys
import traceback

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.development")
django.setup()

try:
    from pprint import pprint

    # Import the API client
    from pyerp.legacy_sync.api_client import api_client

    def analyze_artikel_stamm():
        """
        Fetch data from the Artikel_Stamm table and analyze its structure.
        """
        print("Fetching data from Artikel_Stamm table...")
        try:
            # Fetch a limited number of records to analyze the structure
            df = api_client.fetch_table(
                table_name="Artikel_Stamm",
                top=10,  # Limit to first 10 records for analysis
                new_data_only=False,  # Get all records regardless of modification date
            )

            # Basic information
            print(f"\n{'=' * 80}")
            print(f"Number of records fetched: {len(df)}")
            print(f"{'=' * 80}\n")

            # Column information
            print(f"\n{'=' * 80}")
            print("Column Names and Data Types:")
            print(f"{'=' * 80}")
            for col in df.columns:
                non_null_values = df[col].dropna()
                sample_value = (
                    non_null_values.iloc[0] if len(non_null_values) > 0 else None
                )
                print(f"- {col}")
                print(f"  Data Type: {df[col].dtype}")
                print(f"  Sample Value: {sample_value}")
                print(f"  Null Count: {df[col].isna().sum()} out of {len(df)}")
                print()

            # Print first record in detail
            if len(df) > 0:
                print(f"\n{'=' * 80}")
                print("Detailed First Record:")
                print(f"{'=' * 80}")
                first_record = df.iloc[0].to_dict()
                pprint(first_record)

            # Unique values analysis for categorical fields
            print(f"\n{'=' * 80}")
            print("Unique Values for Selected Fields:")
            print(f"{'=' * 80}")
            categorical_fields = [
                col
                for col in df.columns
                if df[col].dtype == "object" and df[col].nunique() < 10
            ]
            for field in categorical_fields:
                print(f"Field: {field}")
                unique_values = df[field].unique()
                print(f"Unique Values ({len(unique_values)}):")
                pprint(unique_values[:10])  # Show only first 10 unique values
                print()

            # Save to CSV for further analysis
            output_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "artikel_stamm_sample.csv",
            )
            df.to_csv(output_path, index=False)
            print(f"\nSample data saved to {output_path}")

            return df
        except Exception as e:
            print(f"Error fetching data: {e}")
            print("\nDetailed traceback:")
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        df = analyze_artikel_stamm()
except Exception as e:
    print(f"Error in script: {e}")
    print("\nDetailed traceback:")
    traceback.print_exc()
