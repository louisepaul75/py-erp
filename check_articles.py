#!/usr/bin/env python
"""
Script to check for articles in the API response.
"""

import os
import sys
import json
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

from pyerp.products.image_api import ImageAPIClient

def main():
    """Check for articles in the API response."""
    client = ImageAPIClient()
    
    # Check multiple pages
    for page in range(1, 10):
        print(f"Checking page {page}...")
        data = client.get_all_images(page=page, page_size=10)
        
        if not data or not data.get('results'):
            print(f"No results found on page {page}")
            continue
        
        # Check for articles
        articles_found = False
        for item in data.get('results', []):
            if item.get('articles'):
                print(f"Found articles on page {page}:")
                print(json.dumps(item.get('articles'), indent=2))
                articles_found = True
                break
        
        if articles_found:
            break
        else:
            print(f"No articles found on page {page}")
    
    if not articles_found:
        print("No articles found in the first 10 pages")

if __name__ == '__main__':
    main() 