"""Management command to sample data from the Art_Kalkulation table for analysis."""  # noqa: E501
import json
import os  # noqa: F401
import sys
import pandas as pd  # noqa: F401
from pprint import pprint  # noqa: F401
from django.core.management.base import BaseCommand
from django.conf import settings  # noqa: F401

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

# Import the necessary functions from WSZ_api
from wsz_api.getTable import fetch_data_from_api


class Command(BaseCommand):
    help = 'Fetch sample data from Art_Kalkulation table for analysis'  # noqa: F841

    def add_arguments(self, parser):

        parser.add_argument('--limit', type=int, default=10, help='Number of records to fetch')  # noqa: E501
        parser.add_argument('--output', type=str, help='Output file path (defaults to console output)')  # noqa: E501
        parser.add_argument('--fields', action='store_true', help='Show only field names and types')  # noqa: E501
        parser.add_argument('--debug', action='store_true', help='Show debug information')  # noqa: E501
  # noqa: E501, F841

    def handle(self, *args, **options):
        """Handle command execution."""
        limit = options['limit']
        output_file = options['output']
        fields_only = options['fields']
        debug = options['debug']

        self.stdout.write(f"Fetching {limit} sample records from Art_Kalkulation table...")  # noqa: E501

        try:
            # Use the fetch_data_from_api function to get data
            df = fetch_data_from_api(
                table_name="Art_Kalkulation",  # noqa: F841
  # noqa: F841
                top=limit,  # noqa: F841
  # noqa: F841
                new_data_only=False  # noqa: F841
  # noqa: E501, F841
            )

            if df is None or len(df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from the API"))  # noqa: E501
                return

            self.stdout.write(self.style.SUCCESS(f"Retrieved {len(df)} records"))  # noqa: E501

            # If debug is enabled, show basic dataframe info
            if debug:
                self.stdout.write("\nDataFrame Info:")
                buffer = []
                df.info(buf=buffer)
                self.stdout.write("\n".join(buffer))

                self.stdout.write("\nFirst few rows:")
                self.stdout.write(df.head().to_string())

            # Process the data
            if fields_only:
                # Print column information
                self.stdout.write(self.style.SUCCESS("\nFields in Art_Kalkulation table:"))  # noqa: E501
                for col in df.columns:
                    non_null_values = df[col].dropna()
                    data_type = df[col].dtype
                    sample_value = non_null_values.iloc[0] if len(non_null_values) > 0 else None  # noqa: E501

                    self.stdout.write(f"- {col}")
                    self.stdout.write(f"  Data Type: {data_type}")
                    self.stdout.write(f"  Sample Value: {sample_value}")
                    self.stdout.write(f"  Null Count: {df[col].isna().sum()} out of {len(df)}")  # noqa: E501
                    self.stdout.write("")

                # Write to file if requested
                if output_file:
                    field_info = {}
                    for col in df.columns:
                        non_null_values = df[col].dropna()
                        sample_value = non_null_values.iloc[0] if len(non_null_values) > 0 else None  # noqa: E501
                        field_info[col] = {
                            "data_type": str(df[col].dtype),  # noqa: E128
                            "sample_value": str(sample_value),
                            "null_count": int(df[col].isna().sum()),
                            "total_records": len(df)
                        }

                    with open(output_file, 'w') as f:
                        json.dump(field_info, f, indent=2)
  # noqa: F841
                        self.stdout.write(self.style.SUCCESS(f"Field information written to {output_file}"))  # noqa: E501
            else:
                # Export full data sample
                if output_file:
                    # Save as JSON
                    if output_file.endswith('.json'):
                        result = df.to_json(orient='records', lines=False, date_format='iso')  # noqa: E501
                        with open(output_file, 'w') as f:
                            f.write(result)
                    # Save as CSV
                    elif output_file.endswith('.csv'):
                        df.to_csv(output_file, index=False)
                    # Default to Excel
                    else:
                        df.to_excel(output_file, index=False)
  # noqa: F841

                    self.stdout.write(self.style.SUCCESS(f"Sample data written to {output_file}"))  # noqa: E501
                else:
                    # Print first few records to console in a readable format
                    self.stdout.write("\nSample Records:")
                    for idx, row in df.head(min(limit, len(df))).iterrows():
                        self.stdout.write(f"\nRecord {idx}:")
                        for col, value in row.items():
                            self.stdout.write(f"  {col}: {value}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
