from pyerp.external_api.legacy_erp.client import LegacyERPClient
import logging


# Configure logging to see detailed output
logging.basicConfig(level=logging.INFO)


def test_session_validation():
    # Initialize the client
    client = LegacyERPClient(environment="live")

    # Try to load existing session cookie
    print("\nTrying to load existing session cookie...")
    loaded = client.load_session_cookie()
    print(f"Load result: {loaded}")

    # Validate the session
    print("\nValidating session...")
    valid = client.validate_session()
    print(f"Validation result: {valid}")

    if not valid:
        print("\nSession invalid, attempting to ensure session...")
        success = client.ensure_session()
        print(f"Ensure session result: {success}")


if __name__ == "__main__":
    test_session_validation()
