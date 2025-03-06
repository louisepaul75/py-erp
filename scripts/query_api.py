import json
import os

import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings")
django.setup()

from pyerp.products.image_api import ImageAPIClient


def main():
    # Initialize the API client
    client = ImageAPIClient()

    print("Querying first page of API results...")

    # Get just the first page with more results
    first_page = client._make_request(
        "all-files-and-articles/",
        params={"page": 1, "page_size": 50},
    )

    if not first_page:
        print("No results found or API error")
        return

    print(f"Total records in API: {first_page.get('count', 0)}")
    print(f"Results on this page: {len(first_page.get('results', []))}")

    # Look for results with articles
    results_with_articles = []
    for i, result in enumerate(first_page.get("results", [])):
        if result.get("articles") and len(result["articles"]) > 0:
            results_with_articles.append((i, result))
            if len(results_with_articles) >= 3:  # Get max 3 examples
                break

    print(f"\nFound {len(results_with_articles)} results with article data")

    # Print article data for results with articles
    for idx, (result_idx, result) in enumerate(results_with_articles):
        print(f"\n--- Example {idx + 1} (Result #{result_idx + 1}) ---")

        # Print the article data
        articles = result.get("articles", [])
        print(f"Number of articles: {len(articles)}")
        print("\nFirst article data:")
        print(json.dumps(articles[0], indent=2))

        # Print image info as well
        print("\nImage data:")
        print(f"Original file type: {result.get('original_file', {}).get('type')}")
        print(f"Original URL: {result.get('original_file', {}).get('file_url')}")
        if "exported_files" in result:
            print(f"Number of exported files: {len(result.get('exported_files', []))}")
            if result.get("exported_files"):
                print(
                    f"First exported file URL: {result['exported_files'][0].get('image_url')}",
                )


if __name__ == "__main__":
    main()
