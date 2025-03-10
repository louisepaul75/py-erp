#!/usr/bin/env python
"""
Script to fetch a sample of Artikel_Variante records from the legacy ERP
and examine the structure of the Preise column.
"""

import os
import sys
import json
import django
import pandas as pd
from pprint import pprint
from pyerp.external_api.legacy_erp.client import SimpleAPIClient

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()


def fetch_artikel_variante_preise(limit=5):
    """
    Fetch a sample of Artikel_Variante records and examine the Preise column.
    
    Args:
        limit (int): Number of records to fetch
    """
    print(f"Fetching {limit} records from Artikel_Variante table...")
    
    try:
        # Create an instance of the SimpleAPIClient
        client = SimpleAPIClient(environment="live")
        
        # Fetch data using the client
        response = client.session.get(
            f"{client.base_url}/rest/Artikel_Variante?$top={limit}"
        )
        
        # Convert response to DataFrame
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
            
        data = response.json()
        if "__ENTITIES" not in data:
            print("No __ENTITIES found in response")
            print("Response:", data)
            return
            
        df = pd.DataFrame(data["__ENTITIES"])
        
        if df.empty:
            print("No data returned from Artikel_Variante table")
            return
        
        print(f"Successfully fetched {len(df)} records")
        
        # Check if Preise column exists
        if "Preise" not in df.columns:
            print("Preise column not found in Artikel_Variante table")
            print("Available columns:", df.columns.tolist())
            return
        
        # Examine the structure of the Preise column
        print("\n=== Structure of Preise column ===\n")
        
        for index, row in df.iterrows():
            print(f"\nRecord {index + 1}:")
            print(f"UID: {row.get('UID', 'N/A')}")
            print(f"Nummer: {row.get('Nummer', 'N/A')}")
            print(f"alteNummer: {row.get('alteNummer', 'N/A')}")
            print(f"Bezeichnung: {row.get('Bezeichnung', 'N/A')}")
            
            preise = row.get("Preise")
            if preise is None:
                print("Preise: None")
                continue
                
            print("Preise structure:")
            pprint(preise)
            
            # If Preise is a dictionary with a Coll key, examine each 
            # price entry
            if isinstance(preise, dict) and "Coll" in preise:
                print("\nDetailed price entries:")
                for i, price in enumerate(preise["Coll"]):
                    print(f"  Price entry {i + 1}:")
                    pprint(f"    {price}")
            
            print("-" * 50)
        
        # Save a sample to a JSON file for further examination
        sample_file = "artikel_variante_preise_sample.json"
        sample_data = df.head(limit).to_dict(orient="records")
        
        with open(sample_file, "w") as f:
            json.dump(sample_data, f, indent=2, default=str)
        
        print(f"\nSaved sample data to {sample_file}")
        
    except Exception as e:
        print(f"Error fetching data: {e}")


if __name__ == "__main__":
    # Get limit from command line argument if provided
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    fetch_artikel_variante_preise(limit) 