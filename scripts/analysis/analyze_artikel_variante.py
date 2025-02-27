"""
Script to analyze the structure of the Artikel_Variante table from the legacy 4D system.
This script uses the WSZ_api getTable functionality to fetch and analyze product variants.
"""

import os
import sys
import traceback
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

    def analyze_artikel_variante(sample_size=10):
        """
        Fetch data from the Artikel_Variante table and analyze its structure.
        
        Args:
            sample_size: Number of records to fetch for analysis
        
        Returns:
            DataFrame containing the fetched records
        """
        print("Fetching data from Artikel_Variante table...")
        try:
            # Fetch a limited number of records to analyze the structure
            df = fetch_data_from_api(
                table_name="Artikel_Variante",
                top=sample_size,  # Limit to specified number of records for analysis
                new_data_only=False  # Get all records regardless of modification date
            )
            
            # Basic information
            print(f"\n{'='*80}")
            print(f"Number of records fetched: {len(df)}")
            print(f"{'='*80}\n")
            
            # Column information
            print(f"\n{'='*80}")
            print("Column Names and Data Types:")
            print(f"{'='*80}")
            for col in df.columns:
                non_null_values = df[col].dropna()
                sample_value = non_null_values.iloc[0] if len(non_null_values) > 0 else None
                print(f"- {col}")
                print(f"  Data Type: {df[col].dtype}")
                print(f"  Sample Value: {sample_value}")
                print(f"  Null Count: {df[col].isna().sum()} out of {len(df)}")
                print()
            
            # Print first record in detail
            if len(df) > 0:
                print(f"\n{'='*80}")
                print("Detailed First Record:")
                print(f"{'='*80}")
                first_record = df.iloc[0].to_dict()
                pprint(first_record)
                
            # Analyze relationships with Artikel_Stamm (if any)
            print(f"\n{'='*80}")
            print("Relationship Analysis:")
            print(f"{'='*80}")
            
            # Look for potential foreign key fields (common patterns include fk_*, *_id, etc.)
            potential_fk_fields = [col for col in df.columns if 
                                  col.startswith('fk_') or 
                                  col.endswith('_id') or 
                                  col.endswith('ID') or
                                  'artnr' in col.lower() or
                                  col == 'refOld']  # Added refOld as it seems to reference Artikel_Stamm
            
            if potential_fk_fields:
                print("Potential foreign key fields to Artikel_Stamm:")
                for field in potential_fk_fields:
                    unique_count = df[field].nunique()
                    print(f"- {field}: {unique_count} unique values")
            else:
                print("No obvious foreign key fields detected")
            
            # Analyze the alteNummer field which appears to be the SKU
            print(f"\n{'='*80}")
            print("SKU Analysis (alteNummer field):")
            print(f"{'='*80}")
            if 'alteNummer' in df.columns:
                # Check if SKUs follow a pattern (e.g., base-variant)
                sample_skus = df['alteNummer'].dropna().head(10).tolist()
                print(f"Sample SKUs: {sample_skus}")
                
                # Check for pattern with base SKU and variant code
                has_dash = df['alteNummer'].str.contains('-').sum()
                print(f"SKUs with dash separator: {has_dash} out of {len(df)}")
                
                if has_dash > 0:
                    # Extract base SKU and variant code
                    df['base_sku'] = df['alteNummer'].str.split('-').str[0]
                    df['variant_code'] = df['alteNummer'].str.split('-').str[1]
                    
                    # Count unique base SKUs and variant codes
                    unique_base_skus = df['base_sku'].nunique()
                    unique_variant_codes = df['variant_code'].nunique()
                    print(f"Unique base SKUs: {unique_base_skus}")
                    print(f"Unique variant codes: {unique_variant_codes}")
                    
                    # Show sample of variant codes
                    variant_samples = df['variant_code'].dropna().unique()[:10]
                    print(f"Sample variant codes: {variant_samples}")
            
            # Analyze the relationship between Artikel_Variante and Artikel_Familie
            print(f"\n{'='*80}")
            print("Artikel_Familie Relationship Analysis:")
            print(f"{'='*80}")
            if 'Familie_' in df.columns:
                unique_families = df['Familie_'].nunique()
                print(f"Number of unique Familie_ values: {unique_families}")
                print(f"This suggests that variants are grouped into {unique_families} product families")
            
            # Analyze the Preise field which contains pricing information
            print(f"\n{'='*80}")
            print("Price Analysis:")
            print(f"{'='*80}")
            if 'Preise' in df.columns and df['Preise'].iloc[0] is not None:
                # Extract the first non-null Preise value to analyze its structure
                sample_price = None
                for price in df['Preise']:
                    if price is not None:
                        sample_price = price
                        break
                
                if sample_price:
                    print("Price structure:")
                    pprint(sample_price)
                    
                    # Check for different price types
                    if isinstance(sample_price, dict) and 'Coll' in sample_price:
                        price_types = set()
                        for item in sample_price['Coll']:
                            if isinstance(item, dict) and 'Art' in item:
                                price_types.add(item['Art'])
                        
                        print(f"Price types found: {price_types}")
            
            # Save to CSV for further analysis
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artikel_variante_sample.csv')
            
            # Convert complex objects to strings to avoid CSV export issues
            df_export = df.copy()
            for col in df_export.columns:
                if df_export[col].dtype == 'object':
                    df_export[col] = df_export[col].apply(lambda x: str(x) if x is not None else None)
            
            df_export.to_csv(output_path, index=False)
            print(f"\nSample data saved to {output_path}")
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            print("\nDetailed traceback:")
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        # Get the sample size from command-line arguments if provided
        sample_size = 10
        if len(sys.argv) > 1:
            try:
                sample_size = int(sys.argv[1])
            except ValueError:
                print(f"Invalid sample size: {sys.argv[1]}. Using default: 10")
        
        print(f"Analyzing Artikel_Variante table with sample size: {sample_size}")
        df = analyze_artikel_variante(sample_size)
        
        # Print summary statistics
        if df is not None and not df.empty:
            print(f"\n{'='*80}")
            print("Summary Statistics:")
            print(f"{'='*80}")
            print(f"Total records analyzed: {len(df)}")
            print("\nNext steps:")
            print("1. Review the CSV output for detailed data analysis")
            print("2. Use insights to plan integration with pyERP product model")
            print("3. Consider mapping Artikel_Variante to product variants in the new system")
        
except Exception as e:
    print(f"Error in script: {e}")
    print("\nDetailed traceback:")
    traceback.print_exc() 