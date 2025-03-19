"""
Example queries demonstrating how to use the ImageAPIClient.

This script shows common usage patterns for the external image API client.
To run this script, use Django shell:
    python manage.py shell
Then import and run:
    from pyerp.external_api.images_cms.scripts import example_queries
    images = example_queries.fetch_all_images()
"""

from pyerp.external_api.images_cms.client import ImageAPIClient
from pyerp.external_api.images_cms.constants import DEFAULT_PAGE_SIZE


def fetch_all_images():
    """
    Example function demonstrating how to fetch all images from the API.
    Handles pagination and prints summary information.
    """
    # Initialize the client
    client = ImageAPIClient()

    # Start with page 1
    current_page = 1
    total_images = 0
    all_images = []

    while True:
        # Fetch the current page of results
        response = client.get_all_files(page=current_page, page_size=DEFAULT_PAGE_SIZE)

        if not response:
            print(f"Error fetching page {current_page}")
            break

        # Extract results and count
        results = response.get("results", [])
        total_count = response.get("count", 0)

        # Add results to our collection
        all_images.extend(results)
        total_images = len(all_images)

        print(f"Fetched page {current_page}: {len(results)} images")
        print(f"Total images so far: {total_images} of {total_count}")

        # Check if we've got all images
        if total_images >= total_count:
            break

        current_page += 1

    print("\nFinal Summary:")
    print(f"Total images fetched: {total_images}")
    return all_images


if __name__ == "__main__":
    print("Starting image fetch...")
    images = fetch_all_images()
    print("Image fetch complete!")
