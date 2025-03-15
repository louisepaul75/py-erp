#!/usr/bin/env python
"""
Script to check legacy box data, focusing on storage locations and box types.
"""

import os
import sys
import json
import django
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

from pyerp.external_api.legacy_erp.client import LegacyERPClient

def check_legacy_boxes():
    """Check legacy box data for storage locations and box types."""
    print("Checking legacy box data...")
    
    # Initialize client
    client = LegacyERPClient(environment="live")
    

    slots = client.fetch_table("Stamm_Lager_Schuetten_Slots", top=10000)
    slots = slots[['ID','ID_Lager_Schuetten_Slots']]
    slots = slots.rename(columns={'ID':'ID_Slots'})
    print(slots.tail())

    # Fetch a larger sample of boxes
    boxes = client.fetch_table("Stamm_Lager_Schuetten", top=10000)
    print(boxes.tail())
    breakpoint()
    boxes = boxes[['ID','data_']]
    boxes = boxes.rename(columns={'ID':'ID_Stamm_Lager_Schuetten'})

    boxes = boxes.merge(slots, left_on='ID_Stamm_Lager_Schuetten', right_on='ID_Lager_Schuetten_Slots', how='right')

    boxes_locations = client.fetch_table("Lager_Schuetten", top=10000)
    boxes_locations = boxes_locations[['ID_Stamm_Lager_Schuetten','UUID_Artikel_Lagerorte','ID']]
    boxes_locations = boxes_locations.rename(columns={'ID':'ID_Lager_Schuetten'})
    # print(boxes.tail())
    # print(boxes_locations.tail())


    merged_locations = pd.merge(boxes_locations, boxes, left_on='ID_Stamm_Lager_Schuetten', right_on='ID_Stamm_Lager_Schuetten', how='left')

    product_locations = client.fetch_table("Artikel_Lagerorte", top=10000)
    product_locations = product_locations[['UUID', 'ID_Artikel_Stamm','UUID_Stamm_Lagerorte']]
    print(product_locations.tail())
    print(merged_locations.tail())
    merged_product_locations = pd.merge(product_locations, merged_locations, left_on='UUID', right_on='UUID_Artikel_Lagerorte', how='outer')

    products = client.fetch_table("Artikel_Variante", top=10000)
    products = products[['refOld','Bezeichnung']]
    products = products.loc[products['refOld'] != 0]

    merged_products = pd.merge(merged_product_locations, products, left_on='ID_Artikel_Stamm', right_on='refOld', how='left')

    print(merged_products.tail(50))
    # breakpoint()
    
if __name__ == "__main__":
    check_legacy_boxes() 