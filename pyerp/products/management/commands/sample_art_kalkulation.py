"""Management command to sample data from the Art_Kalkulation table for analysis."""
import json
import os
import sys
import pandas as pd
from pprint import pprint
from django.core.management.base import BaseCommand
from django.conf import settings

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

# Import the necessary functions from WSZ_api
from wsz_api.getTable import fetch_data_from_api


class Command(BaseCommand):
    help = 'Fetch sample data from Art_Kalkulation table for analysis'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Number of records to fetch')
        parser.add_argument('--output', type=str, help='Output file path (defaults to console output)')
        parser.add_argument('--fields', action='store_true', help='Show only field names and types')
        parser.add_argument('--debug', action='store_true', help='Show debug information')

    def handle(self, *args, **options):
        """Handle command execution."""
        limit = options['limit']
        output_file = options['output']
        fields_only = options['fields']
        debug = options['debug']
        
        self.stdout.write(f"Fetching {limit} sample records from Art_Kalkulation table...")
        
        try:
            # Use the fetch_data_from_api function to get data
            df = fetch_data_from_api(
                table_name="Art_Kalkulation",
                top=limit,
                new_data_only=False  # Get all records regardless of modification date
            )
            
            if df is None or len(df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from the API"))
                return
                
            self.stdout.write(self.style.SUCCESS(f"Retrieved {len(df)} records"))
            
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
                self.stdout.write(self.style.SUCCESS(f"\nFields in Art_Kalkulation table:"))
                for col in df.columns:
                    non_null_values = df[col].dropna()
                    data_type = df[col].dtype
                    sample_value = non_null_values.iloc[0] if len(non_null_values) > 0 else None
                    
                    self.stdout.write(f"- {col}")
                    self.stdout.write(f"  Data Type: {data_type}")
                    self.stdout.write(f"  Sample Value: {sample_value}")
                    self.stdout.write(f"  Null Count: {df[col].isna().sum()} out of {len(df)}")
                    self.stdout.write("")
                
                # Write to file if requested
                if output_file:
                    field_info = {}
                    for col in df.columns:
                        non_null_values = df[col].dropna()
                        sample_value = non_null_values.iloc[0] if len(non_null_values) > 0 else None
                        field_info[col] = {
                            "data_type": str(df[col].dtype),
                            "sample_value": str(sample_value),
                            "null_count": int(df[col].isna().sum()),
                            "total_records": len(df)
                        }
                    
                    with open(output_file, 'w') as f:
                        json.dump(field_info, f, indent=2)
                        self.stdout.write(self.style.SUCCESS(f"Field information written to {output_file}"))
            else:
                # Export full data sample
                if output_file:
                    # Save as JSON
                    if output_file.endswith('.json'):
                        result = df.to_json(orient='records', lines=False, date_format='iso')
                        with open(output_file, 'w') as f:
                            f.write(result)
                    # Save as CSV
                    elif output_file.endswith('.csv'):
                        df.to_csv(output_file, index=False)
                    # Default to Excel
                    else:
                        df.to_excel(output_file, index=False)
                        
                    self.stdout.write(self.style.SUCCESS(f"Sample data written to {output_file}"))
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