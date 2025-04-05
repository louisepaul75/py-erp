import unittest
import pandas as pd
from datetime import datetime, timedelta

# Assuming LegacyERPClient is accessible like this. Adjust if necessary.
from pyerp.external_api.legacy_erp.client import LegacyERPClient
from pyerp.external_api import connection_manager

# --- Test Configuration ---
# Replace with actual field names from Artikel_Variante if different
TEST_TABLE = "Artikel_Variante"
# DATE_FIELD = "__TIMESTAMP"  # Confirmed from sample, but caused API 500 errors
DATE_FIELD = "created_date" # Trying this field instead, based on sample data
ID_FIELD = "Nummer"      # Updated from sample (was ArtikelNr)
STATUS_FIELD = "Aktiv"     # Updated from sample (was Status), seems boolean
# NUMERIC_FIELD = "Menge"     # No obvious numeric field in sample, commenting out

# --- Helper Functions ---
def is_legacy_erp_enabled():
    """Check if the legacy ERP connection is configured and enabled."""
    try:
        return connection_manager.is_connection_enabled("legacy_erp")
    except Exception:
        # Handle cases where connection manager might not be fully set up
        return False

# --- Test Class ---
@unittest.skipUnless(
    is_legacy_erp_enabled(), "Legacy ERP connection not enabled"
)
class LegacyERPFilterTests(unittest.TestCase):
    """
    Test filtering capabilities of the LegacyERPClient against the
    Artikel_Variante table. Tests run sequentially based on their definition order.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the LegacyERPClient once for all tests in this class."""
        print("\nSetting up LegacyERPClient for filter tests...")
        try:
            cls.client = LegacyERPClient(environment="live")  # Use appropriate env
            # Ensure connection is possible (might perform login)
            if not cls.client.ensure_session():
                raise ConnectionError(
                    "Failed to establish session with Legacy ERP."
                )
            print("LegacyERPClient setup complete.")
        except Exception as e:
            print(f"ERROR setting up LegacyERPClient: {e}")
            # Prevent tests from running if setup fails
            raise unittest.SkipTest(
                f"Skipping tests due to client setup failure: {e}"
            )

    def _run_fetch_test(self, test_name, filter_query=None, top=5):
        """Helper method to run fetch_table and perform basic validation."""
        print(f"\n--- Running Test: {test_name} ---")
        print(f"Filter: {filter_query}")
        try:
            df = self.client.fetch_table(
                table_name=TEST_TABLE,
                filter_query=filter_query,
                top=top,  # Limit results for testing efficiency
                all_records=False,  # Avoid fetching all records during tests
            )
            print(f"Result: Fetched {len(df)} records.")
            self.assertIsInstance(
                df, pd.DataFrame, "Result should be a Pandas DataFrame"
            )
            # Optional: Add more specific assertions based on expected data
            if not df.empty:
                print("Sample result (first row):\n", df.iloc[0])
            return df  # Return df for potential further checks
        except Exception as e:
            self.fail(f"Test '{test_name}' failed with exception: {e}")

    # --- Test Methods (will run in order) ---

    def test_01_fetch_basic(self):
        """Test fetching records without any specific filter."""
        self._run_fetch_test(
            "Basic Fetch (No Filter)", filter_query=None, top=2
        )

    def test_02_filter_equals(self):
        """Test filtering by an exact value match."""
        # Assumption: Using the 'Aktiv' field found in the sample.
        # Adjust if 'True' is not a common value.
        filter_q = [[STATUS_FIELD, "=", True]]  # Updated field and value type
        self._run_fetch_test("Filter Equals (Boolean)", filter_query=filter_q)

    def test_03_filter_date_greater_than(self):
        """Test filtering records created after a specific date."""
        yesterday = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        filter_q = [[DATE_FIELD, ">", yesterday]]
        self._run_fetch_test("Filter Date Greater Than", filter_query=filter_q)

    def test_04_filter_date_less_than(self):
        """Test filtering records created before a specific date."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        filter_q = [[DATE_FIELD, "<", tomorrow]]
        # This should likely return results unless the table is empty/very new
        self._run_fetch_test("Filter Date Less Than", filter_query=filter_q)

    def test_05_filter_in_list(self):
        """Test filtering where a field value is in a list (simulated with OR)."""
        # Assumption: Need known values for the ID_FIELD.
        # Fetch a couple of records first to get valid IDs.
        print("\nFetching sample IDs for 'IN LIST' test...")
        sample_df = self.client.fetch_table(table_name=TEST_TABLE, top=2)
        if len(sample_df) < 2:
            self.skipTest(
                f"Need >= 2 records in {TEST_TABLE} for IN LIST test."
            )

        id1 = sample_df.iloc[0][ID_FIELD]
        id2 = sample_df.iloc[1][ID_FIELD]
        print(f"Using IDs: {id1}, {id2}")

        filter_q = [
            [ID_FIELD, "=", id1],
            [ID_FIELD, "=", id2]
        ]
        # Since filters are on the same field, base.py joins them with 'OR'
        df = self._run_fetch_test(
            "Filter IN List (OR)", filter_query=filter_q, top=10
        )
        # We expect up to 2 results matching these IDs
        if not df.empty:
            self.assertTrue(
                all(item in [id1, id2] for item in df[ID_FIELD]),
                f"Results should only contain IDs {id1} or {id2}"
            )

    def test_06_filter_combined_and(self):
        """Test combining filters on different fields (implicit AND)."""
        # Combine a date filter and a status filter
        a_year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        # Use the boolean status value found in the sample
        assumed_status = True  # Updated value type
        filter_q = [
            [DATE_FIELD, ">", a_year_ago],
            [STATUS_FIELD, "=", assumed_status]  # Updated value type
        ]
        # Since filters are on different fields, base.py joins them with 'AND'
        self._run_fetch_test("Filter Combined (AND)", filter_query=filter_q)

    # def test_07_filter_numeric_greater_than(self):
    #     """Test filtering on a numeric field."""
    #     # Assuming NUMERIC_FIELD exists and has values > 0
    #     # Commenting out as no suitable field found in sample
    #     # filter_q = [[NUMERIC_FIELD, ">", 0]]  # Adjust value as needed
    #     # self._run_fetch_test(
    #     #     "Filter Numeric Greater Than", filter_query=filter_q
    #     # )


if __name__ == '__main__':
    unittest.main() 