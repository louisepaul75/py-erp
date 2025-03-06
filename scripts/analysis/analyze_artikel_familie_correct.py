"""
Script to analyze the structure of the Artikel_Familie table from the legacy 4D system.
This script uses the WSZ_api getTable functionality with the correct parameters
to fetch data from Artikel_Familie and analyze it to help with product categorization.
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

    from wsz_api.auth import get_session_cookie

    # Import the necessary functions from WSZ_api
    from wsz_api.getTable import fetch_data_from_api

    def analyze_artikel_familie():
        """
        Fetch data from the Artikel_Familie table and analyze its structure.
        Uses the correct parameters for fetch_data_from_api.
        """
        print("Fetching data from Artikel_Familie table...")
        try:
            # Fetch data from the 4D database using the working command format
            df = fetch_data_from_api("Artikel_Familie", top=10000, new_data_only=False)

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
                print(f"\nRecord {i + 1}:")
                for col in df.columns:
                    val = df.iloc[i][col]
                    if (
                        val is not None and str(val).strip()
                    ):  # Only print non-empty values
                        print(f"  {col}: {val}")

            # Analyze category names if available
            name_field = None
            # Try to find a name field with different possible column names
            for possible_name in [
                "Name",
                "Bezeichnung",
                "name",
                "bezeichnung",
                "Description",
                "description",
            ]:
                if possible_name in df.columns:
                    name_field = possible_name
                    break

            if name_field:
                print(f"\nCategory Names Analysis (using field '{name_field}'):")
                name_counter = Counter(df[name_field].dropna())
                print(f"Total unique category names: {len(name_counter)}")
                print("\nMost common category names:")
                for name, count in name_counter.most_common(20):
                    print(f"  {name}: {count} occurrences")

            # Check for hierarchical structure
            parent_field = None
            # Try to find parent field with different possible column names
            for possible_parent in [
                "ParentID",
                "Parent_ID",
                "Eltern_ID",
                "parent",
                "Parent",
                "parent_id",
                "ParentKey",
                "Eltern",
            ]:
                if possible_parent in df.columns:
                    parent_field = possible_parent
                    break

            if parent_field:
                print(f"\nHierarchy Analysis using '{parent_field}':")
                non_empty_parents = df[parent_field].dropna()
                non_zero_parents = (
                    non_empty_parents[non_empty_parents != 0]
                    if non_empty_parents.dtype in ["int64", "float64"]
                    else non_empty_parents
                )
                parent_counts = Counter(non_zero_parents)

                print(f"Number of unique parent IDs: {len(parent_counts)}")
                root_count = (
                    (df[parent_field].isna() | (df[parent_field] == 0)).sum()
                    if df[parent_field].dtype in ["int64", "float64"]
                    else df[parent_field].isna().sum()
                )
                print(f"Number of root categories (no parent): {root_count}")

                # Build a hierarchy structure
                hierarchy = defaultdict(list)
                id_field = next(
                    (
                        col
                        for col in ["__KEY", "ID", "UID", "id", "uid"]
                        if col in df.columns
                    ),
                    None,
                )

                if id_field:
                    print(f"Using '{id_field}' as the identifier field.")
                    # Map each category to its parent
                    for i, row in df.iterrows():
                        parent_id = row[parent_field]
                        if not pd.isna(parent_id) and (
                            parent_id != 0
                            if df[parent_field].dtype in ["int64", "float64"]
                            else True
                        ):
                            hierarchy[parent_id].append(row[id_field])

                    # Calculate max depth
                    def get_depth(parent_id, visited=None):
                        if visited is None:
                            visited = set()
                        if parent_id in visited:  # Avoid cycles
                            return 0
                        visited.add(parent_id)
                        if parent_id not in hierarchy:
                            return 1
                        return 1 + max(
                            (
                                get_depth(child, visited.copy())
                                for child in hierarchy[parent_id]
                            ),
                            default=0,
                        )

                    root_ids = []
                    for i, row in df.iterrows():
                        if pd.isna(row[parent_field]) or (
                            row[parent_field] == 0
                            if df[parent_field].dtype in ["int64", "float64"]
                            else False
                        ):
                            root_ids.append(row[id_field])

                    max_depth = max(
                        (get_depth(root_id) for root_id in root_ids),
                        default=1,
                    )
                    print(f"Maximum hierarchy depth: {max_depth}")

                    # Print some statistics about the hierarchy
                    print("\nHierarchy Statistics:")
                    print(f"Categories with children: {len(hierarchy)}")
                    child_counts = [len(children) for children in hierarchy.values()]
                    avg_children = (
                        sum(child_counts) / len(child_counts) if child_counts else 0
                    )
                    print(f"Average children per parent: {avg_children:.2f}")
                    print(
                        f"Max children per parent: {max(child_counts) if child_counts else 0}",
                    )

                    # Print top-level categories
                    if name_field and root_ids:
                        print("\nTop-level Categories:")
                        for i, root_id in enumerate(
                            root_ids[:10],
                        ):  # Show first 10 root categories
                            root_name = (
                                df.loc[df[id_field] == root_id, name_field].iloc[0]
                                if not df.loc[df[id_field] == root_id, name_field].empty
                                else "Unknown"
                            )
                            children_count = len(hierarchy.get(root_id, []))
                            print(
                                f"  {i + 1}. {root_name} (ID: {root_id}) - {children_count} direct children",
                            )

            # Return the DataFrame for further processing if needed
            return df

        except Exception as e:
            print(f"Error analyzing Artikel_Familie: {e}")
            traceback.print_exc()
            return None

    if __name__ == "__main__":
        # Execute the analysis
        familie_data = analyze_artikel_familie()

        # Save to JSON if data was retrieved
        if familie_data is not None:
            try:
                # Convert to records format for easier JSON serialization
                records = familie_data.to_dict(orient="records")
                output_file = "artikel_familie_analysis.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                print(f"\nSaved {len(records)} records to {output_file}")
            except Exception as e:
                print(f"Error saving data to JSON: {e}")

except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure the WSZ_api package is available at the specified path.")
