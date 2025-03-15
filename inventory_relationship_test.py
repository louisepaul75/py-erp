#!/usr/bin/env python
"""
Inventory Relationship Test Script

This script tests the relationships between the tables in the inventory system,
specifically focusing on the connections between Box, BoxSlot, and ProductStorage.
It identifies any inconsistencies or issues in the data relationships.
It also compares the current structure with the legacy ERP tables.
"""

import os
import sys
import django
from collections import defaultdict
from django.db.models import Count, Q, F, Max, Min, Avg, Sum
from django.db import connection
import pandas as pd

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Import models after Django setup
from pyerp.business_modules.inventory.models import Box, BoxSlot, ProductStorage, StorageLocation
from pyerp.external_api.legacy_erp import LegacyERPClient


def print_section(title):
    """Print a section header for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def test_box_boxslot_relationship():
    """Test the relationship between Box and BoxSlot."""
    print_section("Box to BoxSlot Relationship Test")
    
    # Get counts
    total_boxes = Box.objects.count()
    total_box_slots = BoxSlot.objects.count()
    boxes_with_slots = Box.objects.annotate(slot_count=Count('slots')).filter(slot_count__gt=0).count()
    boxes_without_slots = Box.objects.annotate(slot_count=Count('slots')).filter(slot_count=0).count()
    
    print(f"Total Boxes: {total_boxes}")
    print(f"Total BoxSlots: {total_box_slots}")
    print(f"Boxes with at least one slot: {boxes_with_slots}")
    print(f"Boxes without any slots: {boxes_without_slots}")
    
    # Check for BoxSlots with invalid Box references
    invalid_box_slots = BoxSlot.objects.filter(box__isnull=True).count()
    print(f"BoxSlots with invalid Box references: {invalid_box_slots}")
    
    # Check slot distribution
    slot_distribution = Box.objects.annotate(slot_count=Count('slots')).values('slot_count').annotate(box_count=Count('id')).order_by('slot_count')
    print("\nSlot distribution (slots per box):")
    for item in slot_distribution:
        print(f"  {item['slot_count']} slots: {item['box_count']} boxes")


def test_boxslot_productstorage_relationship():
    """Test the relationship between BoxSlot and ProductStorage."""
    print_section("BoxSlot to ProductStorage Relationship Test")
    
    # Get counts
    total_box_slots = BoxSlot.objects.count()
    total_product_storage = ProductStorage.objects.count()
    slots_with_products = BoxSlot.objects.annotate(product_count=Count('stored_products')).filter(product_count__gt=0).count()
    slots_without_products = BoxSlot.objects.annotate(product_count=Count('stored_products')).filter(product_count=0).count()
    
    print(f"Total BoxSlots: {total_box_slots}")
    print(f"Total ProductStorage entries: {total_product_storage}")
    print(f"BoxSlots with at least one product: {slots_with_products}")
    print(f"BoxSlots without any products: {slots_without_products}")
    
    # Check for ProductStorage with invalid BoxSlot references
    invalid_product_storage = ProductStorage.objects.filter(box_slot__isnull=True).count()
    print(f"ProductStorage entries with invalid BoxSlot references: {invalid_product_storage}")
    
    # Check product distribution
    product_distribution = BoxSlot.objects.annotate(product_count=Count('stored_products')).values('product_count').annotate(slot_count=Count('id')).order_by('product_count')
    print("\nProduct distribution (products per slot):")
    for item in product_distribution:
        print(f"  {item['product_count']} products: {item['slot_count']} slots")


def test_box_storage_location_relationship():
    """Test the relationship between Box and StorageLocation."""
    print_section("Box to StorageLocation Relationship Test")
    
    # Get counts
    total_boxes = Box.objects.count()
    total_storage_locations = StorageLocation.objects.count()
    boxes_with_location = Box.objects.filter(storage_location__isnull=False).count()
    boxes_without_location = Box.objects.filter(storage_location__isnull=True).count()
    
    print(f"Total Boxes: {total_boxes}")
    print(f"Total StorageLocations: {total_storage_locations}")
    print(f"Boxes with a storage location: {boxes_with_location}")
    print(f"Boxes without a storage location: {boxes_without_location}")
    
    # Check location distribution
    location_distribution = StorageLocation.objects.annotate(box_count=Count('boxes')).values('id', 'name', 'box_count').filter(box_count__gt=0).order_by('-box_count')[:10]
    print("\nTop 10 storage locations by box count:")
    for item in location_distribution:
        print(f"  {item['name']}: {item['box_count']} boxes")


def test_legacy_id_consistency():
    """Test the consistency of legacy IDs across the system."""
    print_section("Legacy ID Consistency Test")
    
    # Check for boxes with duplicate legacy_ids
    duplicate_box_legacy_ids = Box.objects.values('legacy_id').annotate(count=Count('id')).filter(count__gt=1, legacy_id__isnull=False)
    print(f"Boxes with duplicate legacy_ids: {duplicate_box_legacy_ids.count()}")
    if duplicate_box_legacy_ids.exists():
        print("Duplicate legacy_ids in Box:")
        for item in duplicate_box_legacy_ids:
            print(f"  legacy_id: {item['legacy_id']}, count: {item['count']}")
    
    # Check for box slots with duplicate legacy_slot_ids
    duplicate_slot_legacy_ids = BoxSlot.objects.values('legacy_slot_id').annotate(count=Count('id')).filter(count__gt=1, legacy_slot_id__isnull=False)
    print(f"BoxSlots with duplicate legacy_slot_ids: {duplicate_slot_legacy_ids.count()}")
    if duplicate_slot_legacy_ids.exists():
        print("Duplicate legacy_slot_ids in BoxSlot:")
        for item in duplicate_slot_legacy_ids:
            print(f"  legacy_slot_id: {item['legacy_slot_id']}, count: {item['count']}")


# def test_box_slot_lookup_integrity():
#     """Test the integrity of box slot lookups used in the sync process."""
#     print_section("Box Slot Lookup Integrity Test")
    
#     # Simulate the lookup process used in ProductStorageTransformer._get_box_slot
#     # This will help identify if there are issues with how box slots are being looked up
    
#     # Get all boxes with legacy_id
#     boxes_with_legacy_id = Box.objects.filter(legacy_id__isnull=False)
#     print(f"Boxes with legacy_id: {boxes_with_legacy_id.count()}")
    
#     # Check if each box has at least one slot with slot_number=1
#     boxes_without_default_slot = 0
#     for box in boxes_with_legacy_id:
#         if not BoxSlot.objects.filter(box=box, slot_number=1).exists():
#             boxes_without_default_slot += 1
    
#     print(f"Boxes without a default slot (slot_number=1): {boxes_without_default_slot}")
    
#     # Check for boxes with multiple slots having the same slot_number
#     boxes_with_duplicate_slot_numbers = 0
#     for box in boxes_with_legacy_id:
#         slot_counts = BoxSlot.objects.filter(box=box).values('slot_number').annotate(count=Count('id')).filter(count__gt=1)
#         if slot_counts.exists():
#             boxes_with_duplicate_slot_numbers += 1
    
#     print(f"Boxes with duplicate slot numbers: {boxes_with_duplicate_slot_numbers}")


def test_product_storage_box_slot_consistency():
    """Test the consistency between ProductStorage and BoxSlot."""
    print_section("ProductStorage to BoxSlot Consistency Test")
    
    # Check if all box_slot_id values in ProductStorage correspond to valid BoxSlot instances
    total_product_storage = ProductStorage.objects.count()
    
    # Get all box slot IDs
    valid_box_slot_ids = set(BoxSlot.objects.values_list('id', flat=True))
    
    # Find ProductStorage entries with invalid box_slot references
    invalid_product_storage = ProductStorage.objects.exclude(box_slot_id__in=valid_box_slot_ids).count()
    
    print(f"Total ProductStorage entries: {total_product_storage}")
    print(f"ProductStorage entries with invalid box_slot_id: {invalid_product_storage}")
    
    if invalid_product_storage > 0:
        # Get some examples of invalid references
        examples = ProductStorage.objects.exclude(box_slot_id__in=valid_box_slot_ids)[:5]
        
        print("\nExamples of ProductStorage entries with invalid box_slot_id:")
        for example in examples:
            print(f"  ProductStorage ID: {example.id}, Invalid box_slot_id: {example.box_slot_id}")


def analyze_legacy_data_relationships(boxes_df, product_storage_df, product_variants_df):
    """Analyze relationships between legacy data tables in more detail."""
    print_section("Legacy Data Relationship Analysis")
    
    if boxes_df is None or product_storage_df is None or product_variants_df is None:
        print("Missing required legacy data tables. Skipping analysis.")
        return
    
    # Analyze product variants
    print(f"Total product variants in legacy system: {len(product_variants_df)}")
    
    # Check for active vs inactive products
    if 'Aktiv' in product_variants_df.columns:
        active_products = product_variants_df[product_variants_df['Aktiv'] == True].shape[0]
        inactive_products = product_variants_df[product_variants_df['Aktiv'] == False].shape[0]
        print(f"Active products: {active_products} ({active_products/len(product_variants_df)*100:.1f}%)")
        print(f"Inactive products: {inactive_products} ({inactive_products/len(product_variants_df)*100:.1f}%)")
    
    # Check for products with SKUs
    if 'Nummer' in product_variants_df.columns:
        products_with_sku = product_variants_df[product_variants_df['Nummer'].notna()].shape[0]
        print(f"Products with SKU: {products_with_sku} ({products_with_sku/len(product_variants_df)*100:.1f}%)")
    
    # Analyze product storage
    print(f"\nTotal product storage entries in legacy system: {len(product_storage_df)}")
    
    # Check for products with inventory
    if 'Bestand' in product_storage_df.columns:
        total_inventory = product_storage_df['Bestand'].sum()
        print(f"Total inventory quantity in legacy system: {total_inventory}")
        
        # Distribution of inventory quantities
        zero_inventory = product_storage_df[product_storage_df['Bestand'] == 0].shape[0]
        low_inventory = product_storage_df[(product_storage_df['Bestand'] > 0) & (product_storage_df['Bestand'] <= 10)].shape[0]
        medium_inventory = product_storage_df[(product_storage_df['Bestand'] > 10) & (product_storage_df['Bestand'] <= 100)].shape[0]
        high_inventory = product_storage_df[product_storage_df['Bestand'] > 100].shape[0]
        
        print("\nInventory quantity distribution:")
        print(f"  Zero inventory (0): {zero_inventory} entries ({zero_inventory/len(product_storage_df)*100:.1f}%)")
        print(f"  Low inventory (1-10): {low_inventory} entries ({low_inventory/len(product_storage_df)*100:.1f}%)")
        print(f"  Medium inventory (11-100): {medium_inventory} entries ({medium_inventory/len(product_storage_df)*100:.1f}%)")
        print(f"  High inventory (>100): {high_inventory} entries ({high_inventory/len(product_storage_df)*100:.1f}%)")
    
    # Analyze relationship between products and storage
    if 'ID_Artikel_Stamm' in product_storage_df.columns and 'UID' in product_variants_df.columns:
        # Count unique products in storage
        unique_products_in_storage = product_storage_df['ID_Artikel_Stamm'].nunique()
        print(f"\nUnique products with storage entries: {unique_products_in_storage}")
        
        # Compare with total products
        total_products = len(product_variants_df)
        print(f"Products with no storage entries: {total_products - unique_products_in_storage} ({(total_products - unique_products_in_storage)/total_products*100:.1f}%)")
        
        # Products with multiple storage locations
        product_storage_counts = product_storage_df['ID_Artikel_Stamm'].value_counts()
        products_with_multiple_locations = (product_storage_counts > 1).sum()
        print(f"Products stored in multiple locations: {products_with_multiple_locations} ({products_with_multiple_locations/unique_products_in_storage*100:.1f}%)")
        
        # Top products by storage count
        top_stored_products = product_storage_counts.nlargest(5)
        print("\nTop 5 products by number of storage locations:")
        for product_id, count in top_stored_products.items():
            product_info = product_variants_df[product_variants_df['UID'] == product_id]
            product_name = product_info['Bezeichnung'].iloc[0] if not product_info.empty and 'Bezeichnung' in product_info.columns else "Unknown"
            product_sku = product_info['Nummer'].iloc[0] if not product_info.empty and 'Nummer' in product_info.columns else "N/A"
            print(f"  {product_name} (SKU: {product_sku}): {count} storage locations")
    
    # Analyze boxes
    print(f"\nTotal boxes in legacy system: {len(boxes_df)}")
    
    # Compare with current system
    current_boxes = Box.objects.count()
    print(f"Boxes in current system: {current_boxes}")
    print(f"Difference: {len(boxes_df) - current_boxes} ({(len(boxes_df) - current_boxes)/len(boxes_df)*100:.1f}%)")
    
    # Check for boxes with products
    if 'UUID_Artikel_Lagerorte' in boxes_df.columns:
        boxes_with_products = boxes_df[boxes_df['UUID_Artikel_Lagerorte'].notna()].shape[0]
        print(f"Boxes with product assignments: {boxes_with_products} ({boxes_with_products/len(boxes_df)*100:.1f}%)")


def analyze_legacy_tables():
    """Analyze the legacy ERP tables related to inventory."""
    print_section("Legacy ERP Tables Analysis")
    
    boxes_df = None
    box_slots_df = None
    product_storage_df = None
    product_variants_df = None
    stamm_lager_df = None
    stamm_lager_slots_df = None
    
    try:
        # Connect to legacy ERP
        legacy_client = LegacyERPClient(environment="live")
        
        # Fetch relevant legacy tables
        print("Fetching legacy tables (this may take a while)...")
        
        try:
            # Stamm_Lagerorte table
            stamm_lagerorte_df = legacy_client.fetch_table("Stamm_Lagerorte", top=10000)
            print(f"\nLegacy Stamm_Lagerorte: {len(stamm_lagerorte_df)} records")
            print("Columns:", ", ".join(stamm_lagerorte_df.columns.tolist()))
            
            # Boxes table (Lager_Schuetten)
            boxes_df = legacy_client.fetch_table("Lager_Schuetten", top=10000)
            print(f"\nLegacy Boxes (Lager_Schuetten): {len(boxes_df)} records")
            print("Columns:", ", ".join(boxes_df.columns.tolist()))
            
            # Product storage table (Artikel_Lagerorte)
            product_storage_df = legacy_client.fetch_table("Artikel_Lagerorte", top=10000)
            print(f"\nLegacy Product Storage (Artikel_Lagerorte): {len(product_storage_df)} records")
            print("Columns:", ", ".join(product_storage_df.columns.tolist()))
            
            # Product variants table (Artikel_Variante)
            product_variants_df = legacy_client.fetch_table("Artikel_Variante", top=10000)
            print(f"\nLegacy Product Variants (Artikel_Variante): {len(product_variants_df)} records")
            print("Columns:", ", ".join(product_variants_df.columns.tolist()))
            
            # Stamm_Lager_Schuetten table
            stamm_lager_df = legacy_client.fetch_table("Stamm_Lager_Schuetten", top=10000)
            print(f"\nLegacy Stamm_Lager_Schuetten: {len(stamm_lager_df)} records")
            print("Columns:", ", ".join(stamm_lager_df.columns.tolist()))
            
            # Stamm_Lager_Schuetten_Slots table
            stamm_lager_slots_df = legacy_client.fetch_table("Stamm_Lager_Schuetten_Slots", top=10000)
            print(f"\nLegacy Stamm_Lager_Schuetten_Slots: {len(stamm_lager_slots_df)} records")
            print("Columns:", ", ".join(stamm_lager_slots_df.columns.tolist()))
            
            # Compare counts with our system
            print("\nComparison with current system:")
            print(f"Boxes: Legacy={len(boxes_df)}, Current={Box.objects.count()}")
            print(f"Product Storage: Legacy={len(product_storage_df)}, Current={ProductStorage.objects.count()}")
            
            # Perform detailed analysis of legacy data relationships
            analyze_legacy_data_relationships(boxes_df, product_storage_df, product_variants_df)
            
            # Merge and compare legacy data with current structure
            merge_and_compare_legacy_data(boxes_df, product_storage_df, stamm_lager_df, 
                                         stamm_lager_slots_df, stamm_lagerorte_df)
        
        except Exception as e:
            print(f"Error fetching legacy tables: {str(e)}")
    
    except Exception as e:
        print(f"Error connecting to legacy ERP system: {str(e)}")
        print("Skipping legacy tables analysis.")


def merge_and_compare_legacy_data(boxes_df, product_storage_df, stamm_lager_df, 
                                 stamm_lager_slots_df, stamm_lagerorte_df):
    """Merge legacy data tables to resemble our structure and compare with current system."""
    print_section("Legacy Data Structure Comparison")
    
    if (boxes_df is None or product_storage_df is None or stamm_lager_df is None or 
        stamm_lager_slots_df is None or stamm_lagerorte_df is None):
        print("Missing required legacy data tables. Skipping merge and comparison.")
        return
    
    try:
        # Create merged dataframes that resemble our current structure
        print("Merging legacy data to match current structure...")
        
        # Check column names in each dataframe to help with debugging
        print("\nColumns in boxes_df (Lager_Schuetten):", boxes_df.columns.tolist())
        print("\nColumns in product_storage_df (Artikel_Lagerorte):", product_storage_df.columns.tolist())
        print("\nColumns in stamm_lager_df (Stamm_Lager_Schuetten):", stamm_lager_df.columns.tolist())
        print("\nColumns in stamm_lager_slots_df (Stamm_Lager_Schuetten_Slots):", stamm_lager_slots_df.columns.tolist())
        print("\nColumns in stamm_lagerorte_df (Stamm_Lagerorte):", stamm_lagerorte_df.columns.tolist())
        
        # 1. Merge boxes with storage locations (similar to Box model)
        # Based on the schema, boxes (Lager_Schuetten) connect to storage locations (Stamm_Lagerorte)
        # through product storage (Artikel_Lagerorte)
        if 'UUID_Artikel_Lagerorte' in boxes_df.columns and 'UUID' in product_storage_df.columns and 'UUID_Stamm_Lagerorte' in product_storage_df.columns:
            # First merge boxes with product storage
            merged_boxes_storage = pd.merge(
                boxes_df,
                product_storage_df,
                left_on='UUID_Artikel_Lagerorte',
                right_on='UUID',
                how='left',
                suffixes=('_box', '_storage')
            )
            
            # Then merge with storage locations
            if 'UUID_Stamm_Lagerorte' in merged_boxes_storage.columns and 'UUID' in stamm_lagerorte_df.columns:
                merged_boxes = pd.merge(
                    merged_boxes_storage,
                    stamm_lagerorte_df,
                    left_on='UUID_Stamm_Lagerorte',
                    right_on='UUID',
                    how='left',
                    suffixes=('', '_location')
                )
                
                print(f"\nMerged boxes with locations: {len(merged_boxes)} records")
                
                # Count boxes with valid storage locations
                boxes_with_valid_location = merged_boxes[merged_boxes['UUID_location'].notna()].shape[0]
                print(f"Boxes with valid storage location in legacy system: {boxes_with_valid_location} "
                      f"({boxes_with_valid_location/len(merged_boxes)*100:.1f}%)")
                
                # Compare with our system
                current_boxes_with_location = Box.objects.filter(storage_location__isnull=False).count()
                current_boxes_total = Box.objects.count()
                
                print(f"Boxes with storage location in current system: {current_boxes_with_location} "
                      f"({current_boxes_with_location/current_boxes_total*100:.1f}%)")
                
                # Calculate the difference
                location_assignment_diff = boxes_with_valid_location - current_boxes_with_location
                print(f"Difference in box-location assignments: {location_assignment_diff} "
                      f"({location_assignment_diff/boxes_with_valid_location*100:.1f}% of legacy assignments)")
        
        # 2. Analyze box slots (similar to BoxSlot model)
        # Based on the schema, Stamm_Lager_Schuetten_Slots connects to Lager_Schuetten
        if 'ID_Lager_Schuetten_Slots' in stamm_lager_slots_df.columns and 'ID' in boxes_df.columns:
            merged_slots = pd.merge(
                stamm_lager_slots_df,
                boxes_df,
                left_on='ID_Lager_Schuetten_Slots',
                right_on='ID',
                how='left',
                suffixes=('_slot', '_box')
            )
            
            print(f"\nMerged slots with boxes: {len(merged_slots)} records")
            
            # Count slots with valid box references
            slots_with_valid_box = merged_slots[merged_slots['ID_box'].notna()].shape[0]
            print(f"Slots with valid box reference in legacy system: {slots_with_valid_box} "
                  f"({slots_with_valid_box/len(merged_slots)*100:.1f}%)")
            
            # Count slots per box
            if 'ID_Lager_Schuetten_Slots' in merged_slots.columns:
                slots_per_box = merged_slots.groupby('ID_Lager_Schuetten_Slots').size()
                avg_slots_per_box = slots_per_box.mean()
                max_slots_per_box = slots_per_box.max()
                
                print(f"Average slots per box in legacy system: {avg_slots_per_box:.2f}")
                print(f"Maximum slots per box in legacy system: {max_slots_per_box}")
                
                # Compare with our system
                current_avg_slots = BoxSlot.objects.count() / Box.objects.count() if Box.objects.exists() else 0
                print(f"Average slots per box in current system: {current_avg_slots:.2f}")
                
                # Calculate the difference
                slots_diff = avg_slots_per_box - current_avg_slots
                print(f"Difference in average slots per box: {slots_diff:.2f}")
        
        # 3. Analyze product storage (similar to ProductStorage model)
        # Based on the schema, Artikel_Lagerorte connects to Lager_Schuetten
        if 'UUID' in product_storage_df.columns and 'UUID_Artikel_Lagerorte' in boxes_df.columns:
            # Merge product storage with boxes
            merged_product_storage = pd.merge(
                product_storage_df,
                boxes_df,
                left_on='UUID',
                right_on='UUID_Artikel_Lagerorte',
                how='left',
                suffixes=('_storage', '_box')
            )
            
            print(f"\nMerged product storage with boxes: {len(merged_product_storage)} records")
            
            # Count product storage entries with valid box references
            storage_with_valid_box = merged_product_storage[merged_product_storage['ID_box'].notna()].shape[0]
            print(f"Product storage entries with valid box reference in legacy system: {storage_with_valid_box} "
                  f"({storage_with_valid_box/len(merged_product_storage)*100:.1f}%)")
            
            # Compare with our system
            current_storage_with_box = ProductStorage.objects.filter(box_slot__box__isnull=False).count()
            current_storage_total = ProductStorage.objects.count()
            
            print(f"Product storage entries with valid box reference in current system: {current_storage_with_box} "
                  f"({current_storage_with_box/current_storage_total*100:.1f}% if total is non-zero)")
            
            # Calculate the difference
            storage_box_diff = storage_with_valid_box - current_storage_with_box
            print(f"Difference in product storage-box assignments: {storage_box_diff} "
                  f"({storage_box_diff/storage_with_valid_box*100:.1f}% of legacy assignments)")
        
        # 4. Analyze box utilization
        analyze_box_utilization_discrepancy(boxes_df, product_storage_df)
        
    except Exception as e:
        print(f"Error during legacy data merge and comparison: {str(e)}")


def analyze_box_utilization_discrepancy(boxes_df, product_storage_df):
    """Analyze the discrepancy in box utilization between legacy and current system."""
    print_section("Box Utilization Discrepancy Analysis")
    
    if boxes_df is None or product_storage_df is None:
        print("Missing required legacy data tables. Skipping box utilization analysis.")
        return
    
    try:
        # 1. Calculate box utilization in legacy system
        if 'UUID_Artikel_Lagerorte' in boxes_df.columns and 'UUID' in product_storage_df.columns:
            # Get unique boxes with products in legacy system
            boxes_with_products = boxes_df[boxes_df['UUID_Artikel_Lagerorte'].notna()]
            legacy_boxes_with_products = len(boxes_with_products)
            legacy_total_boxes = len(boxes_df)
            legacy_utilization_rate = legacy_boxes_with_products / legacy_total_boxes if legacy_total_boxes > 0 else 0
            
            print(f"Legacy system box utilization:")
            print(f"  Total boxes: {legacy_total_boxes}")
            print(f"  Boxes with products: {legacy_boxes_with_products} ({legacy_utilization_rate*100:.1f}%)")
            
            # 2. Calculate box utilization in current system
            current_boxes_with_products = Box.objects.filter(slots__stored_products__isnull=False).distinct().count()
            current_total_boxes = Box.objects.count()
            current_utilization_rate = current_boxes_with_products / current_total_boxes if current_total_boxes > 0 else 0
            
            print(f"\nCurrent system box utilization:")
            print(f"  Total boxes: {current_total_boxes}")
            print(f"  Boxes with products: {current_boxes_with_products} ({current_utilization_rate*100:.1f}%)")
            
            # 3. Calculate the discrepancy
            utilization_diff = legacy_utilization_rate - current_utilization_rate
            print(f"\nBox utilization rate discrepancy: {utilization_diff*100:.1f}%")
            
            # 4. Identify potential causes
            print("\nPotential causes of discrepancy:")
            
            # 4.1 Check for boxes in legacy system that are not in current system
            if 'ID' in boxes_df.columns:
                legacy_box_ids = set(boxes_df['ID'].dropna())
                current_box_legacy_ids = set(Box.objects.filter(legacy_id__isnull=False).values_list('legacy_id', flat=True))
                missing_boxes = legacy_box_ids - current_box_legacy_ids
                
                print(f"  Boxes in legacy system not imported to current system: {len(missing_boxes)} "
                      f"({len(missing_boxes)/len(legacy_box_ids)*100:.1f}% of legacy boxes)")
                
                # 4.2 Check for product storage entries that couldn't be imported
                if 'UUID_Artikel_Lagerorte' in boxes_df.columns and 'ID_Artikel_Stamm' in product_storage_df.columns:
                    # Count product storage entries for boxes that are missing in current system
                    boxes_with_missing_ids = boxes_df[boxes_df['ID'].isin(missing_boxes)]
                    missing_box_storage_entries = 0
                    if not boxes_with_missing_ids.empty and 'UUID_Artikel_Lagerorte' in boxes_with_missing_ids.columns:
                        missing_storage_uuids = set(boxes_with_missing_ids['UUID_Artikel_Lagerorte'].dropna())
                        missing_box_storage_entries = product_storage_df[product_storage_df['UUID'].isin(missing_storage_uuids)].shape[0]
                    
                    print(f"  Product storage entries for missing boxes: {missing_box_storage_entries} "
                          f"({missing_box_storage_entries/len(product_storage_df)*100:.1f}% of legacy storage entries)")
                    
                    # 4.3 Check for boxes with products in legacy system but not in current system
                    legacy_boxes_with_products_ids = set(boxes_with_products['ID'].dropna())
                    current_boxes_with_products_legacy_ids = set(
                        Box.objects.filter(
                            slots__stored_products__isnull=False, 
                            legacy_id__isnull=False
                        ).values_list('legacy_id', flat=True)
                    )
                    
                    boxes_missing_products = legacy_boxes_with_products_ids - current_boxes_with_products_legacy_ids
                    
                    print(f"  Boxes with products in legacy but not in current system: {len(boxes_missing_products)} "
                          f"({len(boxes_missing_products)/len(legacy_boxes_with_products_ids)*100:.1f}% of legacy boxes with products)")
                    
                    # 4.4 Provide recommendations
                    print("\nRecommendations to address discrepancy:")
                    print("  1. Verify the box import process to ensure all legacy boxes are imported")
                    print("  2. Check for filters in the import process that might be excluding certain boxes")
                    print("  3. Verify the product storage import process to ensure all products are assigned to boxes")
                    print("  4. Check for data quality issues in the legacy system that might be causing import failures")
                    print("  5. Consider running a targeted import for the missing boxes and their product assignments")
    
    except Exception as e:
        print(f"Error during box utilization discrepancy analysis: {str(e)}")


def identify_missing_box_assignments():
    """Identify specific boxes that should have product assignments but don't."""
    print_section("Missing Box Assignment Identification")
    
    try:
        # Connect to legacy ERP
        legacy_client = LegacyERPClient(environment="live")
        
        # Fetch relevant legacy tables
        print("Fetching legacy data for box assignment analysis...")
        
        # Boxes table (Lager_Schuetten)
        boxes_df = legacy_client.fetch_table("Lager_Schuetten", top=10000)
        
        # Product storage table (Artikel_Lagerorte)
        product_storage_df = legacy_client.fetch_table("Artikel_Lagerorte", top=10000)
        
        if boxes_df is None or product_storage_df is None:
            print("Could not fetch required legacy data. Skipping analysis.")
            return
        
        # Print column names to help with debugging
        print("\nColumns in boxes_df (Lager_Schuetten):", boxes_df.columns.tolist())
        print("\nColumns in product_storage_df (Artikel_Lagerorte):", product_storage_df.columns.tolist())
        
        # 1. Get boxes with products in legacy system
        if 'UUID_Artikel_Lagerorte' in boxes_df.columns and 'ID' in boxes_df.columns:
            legacy_boxes_with_products = set(boxes_df[boxes_df['UUID_Artikel_Lagerorte'].notna()]['ID'].dropna())
            
            # 2. Get boxes with products in current system
            current_boxes_with_products = set(
                Box.objects.filter(
                    slots__stored_products__isnull=False
                ).filter(
                    legacy_id__isnull=False
                ).values_list('legacy_id', flat=True)
            )
            
            # 3. Find boxes that should have products but don't
            missing_product_assignments = legacy_boxes_with_products - current_boxes_with_products
            
            print(f"Found {len(missing_product_assignments)} boxes with missing product assignments")
            
            # 4. Get details for a sample of these boxes
            if missing_product_assignments:
                sample_size = min(10, len(missing_product_assignments))
                sample_boxes = list(missing_product_assignments)[:sample_size]
                
                print(f"\nSample of {sample_size} boxes with missing product assignments:")
                
                for box_id in sample_boxes:
                    # Get box details from legacy system
                    box_info = boxes_df[boxes_df['ID'] == box_id]
                    
                    if not box_info.empty:
                        # Try different column names for box name
                        box_name = "Unknown"
                        for name_col in ['Bezeichnung', 'data_', 'ID_Stamm_Lager_Schuetten']:
                            if name_col in box_info.columns and not box_info[name_col].iloc[0] is None:
                                box_name = str(box_info[name_col].iloc[0])
                                break
                        
                        # Get product count for this box
                        product_uuid = box_info['UUID_Artikel_Lagerorte'].iloc[0] if 'UUID_Artikel_Lagerorte' in box_info.columns else None
                        product_count = 0
                        if product_uuid is not None:
                            box_products = product_storage_df[product_storage_df['UUID'] == product_uuid]
                            product_count = len(box_products)
                        
                        print(f"  Legacy Box ID: {box_id}")
                        print(f"    Name/Identifier: {box_name}")
                        print(f"    Products in legacy system: {product_count}")
                        
                        # Check if box exists in current system
                        current_box = Box.objects.filter(legacy_id=box_id).first()
                        if current_box:
                            print(f"    Current Box ID: {current_box.id}")
                            print(f"    Current Box Name: {current_box.name}")
                            print(f"    Slots in current system: {current_box.slots.count()}")
                            print(f"    Products in current system: {ProductStorage.objects.filter(box_slot__box=current_box).count()}")
                        else:
                            print("    Not found in current system")
                        
                        print("")
                
                # 5. Provide recommendations
                print("\nRecommendations to fix missing product assignments:")
                print("  1. Verify the product storage import process for these specific boxes")
                print("  2. Check if these boxes have slots in the current system")
                print("  3. Investigate if there were errors during the import of these specific boxes")
                print("  4. Consider running a targeted import for these boxes and their product assignments")
                print("  5. Check for data quality issues in the legacy data for these boxes")
            else:
                print("No boxes with missing product assignments found.")
        else:
            print("Required columns not found in legacy data. Skipping analysis.")
            print("Expected columns 'UUID_Artikel_Lagerorte' and 'ID' in boxes_df.")
            print("Available columns in boxes_df:", boxes_df.columns.tolist())
    
    except Exception as e:
        print(f"Error during missing box assignment identification: {str(e)}")


def analyze_product_distribution():
    """Analyze the distribution of products across box slots in more detail."""
    print_section("Detailed Product Distribution Analysis")
    
    # Get total counts
    total_boxes = Box.objects.count()
    total_box_slots = BoxSlot.objects.count()
    total_product_storage = ProductStorage.objects.count()
    
    # Analyze products per slot
    slots_with_products = BoxSlot.objects.annotate(product_count=Count('stored_products')).filter(product_count__gt=0)
    
    # Get distribution statistics
    if slots_with_products.exists():
        max_products = slots_with_products.aggregate(Max('product_count'))['product_count__max']
        min_products = slots_with_products.aggregate(Min('product_count'))['product_count__min']
        avg_products = slots_with_products.aggregate(Avg('product_count'))['product_count__avg']
        
        print(f"Product distribution in slots that have products:")
        print(f"  Minimum products per slot: {min_products}")
        print(f"  Maximum products per slot: {max_products}")
        print(f"  Average products per slot: {avg_products:.2f}")
        
        # Distribution by ranges
        ranges = [(1, 10), (11, 50), (51, 100), (101, 200), (201, 500), (501, 1000), (1001, float('inf'))]
        print("\nProduct count distribution:")
        for start, end in ranges:
            if end == float('inf'):
                count = slots_with_products.filter(product_count__gte=start).count()
                print(f"  {start}+ products: {count} slots ({count/slots_with_products.count()*100:.1f}%)")
            else:
                count = slots_with_products.filter(product_count__gte=start, product_count__lte=end).count()
                print(f"  {start}-{end} products: {count} slots ({count/slots_with_products.count()*100:.1f}%)")
    
    # Analyze top slots by product count - using a different approach
    print("\nTop 10 slots by product count:")
    # Get the IDs of the top slots
    top_slot_ids = slots_with_products.values('id', 'product_count').order_by('-product_count')[:10]
    
    # Fetch the complete BoxSlot objects for these IDs
    for slot_data in top_slot_ids:
        slot_id = slot_data['id']
        product_count = slot_data['product_count']
        slot = BoxSlot.objects.get(id=slot_id)
        box = slot.box
        print(f"  Box {box.id} (legacy_id: {box.legacy_id}), Slot {slot.slot_number}: {product_count} products")
    
    # Analyze product quantities
    print("\nProduct quantity analysis:")
    total_quantity = ProductStorage.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f"  Total product quantity across all storage: {total_quantity}")
    
    # Products with highest quantities
    top_quantity_products = ProductStorage.objects.order_by('-quantity')[:10]
    if top_quantity_products.exists():
        print("\nTop 10 products by quantity:")
        for ps in top_quantity_products:
            product_name = ps.product.name if ps.product else "Unknown"
            box_slot_info = f"Box {ps.box_slot.box.id}, Slot {ps.box_slot.slot_number}" if ps.box_slot else "No box slot"
            print(f"  {product_name} (SKU: {ps.product.sku if ps.product else 'N/A'}): {ps.quantity} units in {box_slot_info}")
    
    # Analyze box utilization
    print("\nBox utilization analysis:")
    boxes_with_products = Box.objects.filter(slots__stored_products__isnull=False).distinct()
    print(f"  Boxes with at least one product: {boxes_with_products.count()} ({boxes_with_products.count()/total_boxes*100:.1f}%)")
    
    # Analyze storage locations
    print("\nStorage location analysis:")
    locations_with_boxes = StorageLocation.objects.annotate(box_count=Count('boxes')).filter(box_count__gt=0)
    print(f"  Storage locations with at least one box: {locations_with_boxes.count()}")
    
    if locations_with_boxes.exists():
        top_locations = locations_with_boxes.order_by('-box_count')[:5]
        print("\n  Top 5 storage locations by box count:")
        for location in top_locations:
            print(f"    {location.name}: {location.box_count} boxes")


def main():
    """Run all tests."""
    print("Starting Inventory Relationship Tests...")
    
    # Run all tests
    test_box_boxslot_relationship()
    test_boxslot_productstorage_relationship()
    test_box_storage_location_relationship()
    test_legacy_id_consistency()
    test_product_storage_box_slot_consistency()
    analyze_product_distribution()
    analyze_legacy_tables()
    identify_missing_box_assignments()  # Add the new analysis
    
    print("\nInventory Relationship Tests completed.")


if __name__ == "__main__":
    main() 