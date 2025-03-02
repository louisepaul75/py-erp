"""
Script to list all available tables in the legacy 4D database.
This will help us identify the correct table name for product families/categories.
"""

import os
import sys
import traceback

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Try to import modules from WSZ_api
    from wsz_api.getTable import fetch_data_from_api
    from wsz_api.auth import get_session_cookie
    
    def list_all_tables():
        """
        List all available tables in the 4D database.
        Returns a list of table names or None if an error occurs.
        """
        print("Using alternative approach - checking common table names...")
        # Try common table names pattern
        possible_tables = [
            "Art_Familie", "Artikel_Familie", "Familie", 
            "ArtikelFamilie", "ArtFamilie", "ArtikelKategorien",
            "Kategorie", "Kategorien", "Warengruppe", "Warengruppen",
            "Produktgruppe", "Produktgruppen", "Produktkategorie", "Produktkategorien"
        ]
        
        found_tables = []
        for table in possible_tables:
            try:
                print(f"Checking if {table} exists...")
                df = fetch_data_from_api(table)
                if df is not None and len(df) > 0:
                    print(f"✓ Table {table} exists with data ({len(df)} rows)")
                    found_tables.append(table)
                else:
                    print(f"✗ Table {table} returned no data")
            except Exception as e:
                print(f"✗ Table {table} check failed: {str(e).split('\n')[0]}")
        
        # Also try to get a sample from Artikel_Variante to see table references
        try:
            print("\nChecking Artikel_Variante for category/family references...")
            av_df = fetch_data_from_api("Artikel_Variante")
            if av_df is not None and len(av_df) > 0:
                print(f"Found {len(av_df)} rows in Artikel_Variante")
                # Print column names that might be related to categories
                category_cols = [col for col in av_df.columns if 
                                any(keyword in col.lower() for keyword in 
                                    ['kategorie', 'familie', 'group', 'warengruppe', 'category'])]
                
                if category_cols:
                    print("Potential category/family related columns in Artikel_Variante:")
                    for col in category_cols:
                        val = av_df[col].iloc[0]
                        print(f"  - {col}: {val if val is not None else 'NULL'}")
                        
                # Look at the first few rows to understand structure
                print("\nSample of first 3 rows from Artikel_Variante:")
                sample_size = min(3, len(av_df))
                for i in range(sample_size):
                    print(f"\nRow {i+1}:")
                    for col in av_df.columns:
                        val = av_df[col].iloc[i]
                        if val is not None and str(val).strip():  # Only print non-empty values
                            print(f"  {col}: {val}")
        except Exception as e:
            print(f"Error checking Artikel_Variante: {str(e)}")
            traceback.print_exc()
        
        return found_tables

    if __name__ == "__main__":
        # List all tables
        tables = list_all_tables()
        
        if tables and len(tables) > 0:
            print(f"\nFound {len(tables)} tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            
            # If we found tables, try to fetch and display sample data from each
            for table in tables:
                try:
                    print(f"\n--- Sample data from {table} ---")
                    data = fetch_data_from_api(table)
                    if data is not None and len(data) > 0:
                        print(f"Total rows: {len(data)}")
                        print("Column names:", list(data.columns))
                        
                        # Print sample rows
                        sample_size = min(3, len(data))
                        for i in range(sample_size):
                            print(f"\nRow {i+1}:")
                            for col in data.columns:
                                val = data[col].iloc[i]
                                if val is not None and str(val).strip():  # Only print non-empty values
                                    print(f"  {col}: {val}")
                except Exception as e:
                    print(f"Error fetching sample data from {table}: {e}")
        else:
            print("\nNo tables found or error occurred.")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure the WSZ_api package is available at the specified path.") 