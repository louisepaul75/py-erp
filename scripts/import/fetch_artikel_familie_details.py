"""
Script to fetch Artikel_Familie details from the legacy 4D system.
This script uses the WSZ_api to fetch Artikel_Variante data and attempts to follow the
ArtikelFamilie references to get the family/category data.
"""

import json
import sys
import traceback
from collections import Counter, defaultdict

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r"C:\Users\Joan-Admin\PycharmProjects\WSZ_api"
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    import pandas as pd

    from wsz_api.api import WSZ_API  # Try to import directly from wsz_api.api
    from wsz_api.auth import get_session_cookie

    # Import the necessary functions from WSZ_api
    from wsz_api.getTable import fetch_data_from_api

    def fetch_artikel_familie_details():
        """
        Fetch details about the Artikel_Familie table by analyzing Artikel_Variante
        and attempting to fetch family data from deferred references.
        """
        print("Fetching Artikel_Variante data to analyze family references...")
        try:
            # First fetch Artikel_Variante data to get family references
            av_df = fetch_data_from_api("Artikel_Variante")
            if av_df is None or len(av_df) == 0:
                print("No data returned from Artikel_Variante")
                return None

            print(f"Retrieved {len(av_df)} records from Artikel_Variante")

            # Analyze Familie_ column
            if "Familie_" in av_df.columns:
                familie_ids = av_df["Familie_"].dropna().unique()
                print(f"Found {len(familie_ids)} unique Familie_ values")

                # Count occurrences of each Familie_ value
                familie_counts = Counter(av_df["Familie_"].dropna())
                print("Top 10 most common Familie_ values:")
                for familie_id, count in familie_counts.most_common(10):
                    print(f"  - {familie_id}: {count} products")

                # Try to fetch details for each Familie_ ID using WSZ_API
                try:
                    print(
                        "\nAttempting to fetch Artikel_Familie details using WSZ_API...",
                    )
                    api = WSZ_API()

                    # Collect details for each family
                    familie_details = {}
                    sample_ids = list(familie_ids)[:5]  # Try with first 5 IDs

                    for i, familie_id in enumerate(sample_ids):
                        print(
                            f"Fetching details for Familie ID {i + 1}/{len(sample_ids)}: {familie_id}",
                        )
                        try:
                            # Try to fetch single record using the ID
                            data = api.get_record("Artikel_Familie", familie_id)
                            if data:
                                familie_details[familie_id] = data
                                print("  ✓ Successfully fetched details")
                            else:
                                print("  ✗ No data returned")
                        except Exception as e:
                            print(f"  ✗ Error fetching details: {e!s}")

                    # Check if we got any details
                    if familie_details:
                        print(
                            f"\nSuccessfully fetched details for {len(familie_details)} familie IDs",
                        )

                        # Analyze the structure of familie details
                        print("\nAnalyzing Familie structure:")
                        all_keys = set()
                        for details in familie_details.values():
                            all_keys.update(details.keys())

                        print(
                            f"Fields in Artikel_Familie: {', '.join(sorted(all_keys))}",
                        )

                        # Print sample of family details
                        print("\nSample of Familie details:")
                        for i, (id, details) in enumerate(
                            list(familie_details.items())[:3],
                        ):
                            print(f"\nFamilie {i + 1}:")
                            for key, value in details.items():
                                print(f"  {key}: {value}")

                        # Try to find hierarchical structure
                        if any("Parent" in key for key in all_keys) or any(
                            "parent" in key.lower() for key in all_keys
                        ):
                            print("\nHierarchical structure detected!")
                            parent_key = next(
                                (k for k in all_keys if "parent" in k.lower()),
                                None,
                            )
                            if parent_key:
                                print(f"Parent reference field: {parent_key}")

                                # Build hierarchy
                                hierarchy = defaultdict(list)
                                for id, details in familie_details.items():
                                    parent_id = details.get(parent_key)
                                    hierarchy[parent_id].append(id)

                                print("\nFamily hierarchy (partial):")
                                for parent_id, children in hierarchy.items():
                                    print(
                                        f"Parent {parent_id}: {len(children)} children",
                                    )

                        # Return the collected details
                        return familie_details
                    print("Could not fetch any Familie details")

                except ImportError:
                    print("WSZ_API class not available. Using alternative approach.")
                    # Here you could implement an alternative approach using REST calls directly

            return None

        except Exception as e:
            print(f"Error analyzing Artikel_Familie: {e}")
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        # Execute the analysis
        familie_details = fetch_artikel_familie_details()

        # Save to JSON if data was retrieved
        if familie_details:
            try:
                output_file = "artikel_familie_details.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(familie_details, f, ensure_ascii=False, indent=2)
                print(
                    f"\nSaved details for {len(familie_details)} familie records to {output_file}",
                )
            except Exception as e:
                print(f"Error saving data to JSON: {e}")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure the WSZ_api package is available at the specified path.")
