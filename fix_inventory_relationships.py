#!/usr/bin/env python
"""
Script to fix inventory relationships in pyERP.

This script addresses two main issues:
1. Storage location assignments for boxes are not being properly set
2. Product storage entries are not correctly linked to box slots

Usage:
    python fix_inventory_relationships.py
"""

import os
import sys
import django
import pandas as pd
from django.db import transaction
from django.db.models import Count, Q

# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Now import Django models after setup
from pyerp.business_modules.inventory.models import Box, BoxSlot, ProductStorage, StorageLocation
from pyerp.external_api.legacy_erp.client import LegacyERPClient


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def fix_box_storage_locations():
    """Fix storage location assignments for boxes."""
    print_section("Fixing Box Storage Location Assignments")
    
    # Get current stats
    total_boxes = Box.objects.count()
    boxes_with_location = Box.objects.filter(storage_location__isnull=False).count()
    
    print(f"Current status: {boxes_with_location}/{total_boxes} boxes have storage locations assigned ({boxes_with_location/total_boxes*100:.2f}%)")
    
    # Connect to legacy ERP
    legacy_client = LegacyERPClient(environment="live")
    
    # Fetch boxes and storage locations from legacy system
    print("Fetching data from legacy system...")
    legacy_boxes = legacy_client.fetch_table("Lager_Schuetten", top=10000)
    legacy_storage_locations = legacy_client.fetch_table("Stamm_Lagerorte", top=10000)
    
    print(f"Found {len(legacy_boxes)} boxes and {len(legacy_storage_locations)} storage locations in legacy system")
    
    # Create a mapping of storage location legacy IDs to StorageLocation objects
    storage_location_map = {
        sl.legacy_id: sl for sl in StorageLocation.objects.all()
    }
    
    # Track statistics
    updated_count = 0
    missing_storage_location_count = 0
    missing_box_count = 0
    
    # Process each legacy box
    with transaction.atomic():
        for _, row in legacy_boxes.iterrows():
            box_legacy_id = row.get('ID')
            storage_location_uuid = row.get('UUID_Stamm_Lagerorte')
            
            if not box_legacy_id:
                continue
                
            try:
                # Find the box in our system
                box = Box.objects.get(legacy_id=box_legacy_id)
                
                # Skip if already has a storage location
                if box.storage_location:
                    continue
                
                # Find and assign the storage location
                if storage_location_uuid and storage_location_uuid in storage_location_map:
                    storage_location = storage_location_map[storage_location_uuid]
                    box.storage_location = storage_location
                    box.save(update_fields=['storage_location'])
                    updated_count += 1
                    print(f"Updated box {box.code} (legacy_id: {box_legacy_id}) with storage location {storage_location.name}")
                else:
                    missing_storage_location_count += 1
                    print(f"Storage location with UUID {storage_location_uuid} not found for box {box_legacy_id}")
            except Box.DoesNotExist:
                missing_box_count += 1
                print(f"Box with legacy_id {box_legacy_id} not found in current system")
    
    # Get updated stats
    boxes_with_location_after = Box.objects.filter(storage_location__isnull=False).count()
    
    print("\nResults:")
    print(f"Updated {updated_count} boxes with storage locations")
    print(f"Missing storage locations: {missing_storage_location_count}")
    print(f"Missing boxes: {missing_box_count}")
    print(f"After fix: {boxes_with_location_after}/{total_boxes} boxes have storage locations assigned ({boxes_with_location_after/total_boxes*100:.2f}%)")


def fix_product_storage_box_slot_links():
    """Fix product storage links to box slots."""
    print_section("Fixing Product Storage to Box Slot Links")
    
    # Get current stats
    total_product_storage = ProductStorage.objects.count()
    product_storage_with_valid_slot = ProductStorage.objects.filter(box_slot__isnull=False).count()
    
    print(f"Current status: {product_storage_with_valid_slot}/{total_product_storage} product storage entries have valid box slots ({product_storage_with_valid_slot/total_product_storage*100:.2f}%)")
    
    # Connect to legacy ERP
    legacy_client = LegacyERPClient(environment="live")
    
    # Fetch product storage and boxes from legacy system
    print("Fetching data from legacy system...")
    legacy_product_storage = legacy_client.fetch_table("Artikel_Lagerorte", top=10000)
    legacy_boxes = legacy_client.fetch_table("Lager_Schuetten", top=10000)
    
    print(f"Found {len(legacy_product_storage)} product storage entries and {len(legacy_boxes)} boxes in legacy system")
    
    # Create mappings
    box_map = {box.legacy_id: box for box in Box.objects.all()}
    
    # Create a mapping of box legacy IDs to their first slot
    box_slot_map = {}
    for box in Box.objects.prefetch_related('slots'):
        if box.legacy_id and box.slots.exists():
            box_slot_map[box.legacy_id] = box.slots.first()
    
    # Track statistics
    updated_count = 0
    missing_box_count = 0
    missing_slot_count = 0
    
    # Process each legacy product storage entry
    with transaction.atomic():
        for _, row in legacy_product_storage.iterrows():
            product_storage_uuid = row.get('UUID')
            box_id = None
            
            # Find the box ID from the legacy data
            # First check if there's a direct link to a box
            if 'UUID_Lager_Schuetten' in row and row['UUID_Lager_Schuetten']:
                box_id = row['UUID_Lager_Schuetten']
            
            # If no direct link, try to find a box that references this product storage
            if not box_id:
                matching_boxes = legacy_boxes[legacy_boxes['UUID_Artikel_Lagerorte'] == product_storage_uuid]
                if not matching_boxes.empty:
                    box_id = matching_boxes.iloc[0]['ID']
            
            if not product_storage_uuid or not box_id:
                continue
                
            try:
                # Find the product storage in our system
                product_storage = ProductStorage.objects.get(legacy_id=product_storage_uuid)
                
                # Skip if already has a valid box slot
                if product_storage.box_slot_id:
                    continue
                
                # Find and assign the box slot
                if box_id in box_slot_map:
                    box_slot = box_slot_map[box_id]
                    product_storage.box_slot = box_slot
                    product_storage.save(update_fields=['box_slot'])
                    updated_count += 1
                    print(f"Updated product storage {product_storage.id} (legacy_id: {product_storage_uuid}) with box slot {box_slot.slot_code}")
                elif box_id in box_map:
                    # Box exists but no slot found
                    box = box_map[box_id]
                    # Create a slot if needed
                    if not box.slots.exists():
                        box_slot = BoxSlot.objects.create(
                            box=box,
                            slot_number=1,
                            slot_code=f"{box.code}-1",
                            unit_number=1
                        )
                        box_slot_map[box_id] = box_slot
                        product_storage.box_slot = box_slot
                        product_storage.save(update_fields=['box_slot'])
                        updated_count += 1
                        print(f"Created new slot and updated product storage {product_storage.id} (legacy_id: {product_storage_uuid})")
                    else:
                        # This shouldn't happen if our mapping is correct, but just in case
                        missing_slot_count += 1
                else:
                    missing_box_count += 1
                    print(f"Box with legacy_id {box_id} not found for product storage {product_storage_uuid}")
            except ProductStorage.DoesNotExist:
                print(f"Product storage with legacy_id {product_storage_uuid} not found in current system")
    
    # Get updated stats
    product_storage_with_valid_slot_after = ProductStorage.objects.filter(box_slot__isnull=False).count()
    
    print("\nResults:")
    print(f"Updated {updated_count} product storage entries with box slots")
    print(f"Missing boxes: {missing_box_count}")
    print(f"Missing slots: {missing_slot_count}")
    print(f"After fix: {product_storage_with_valid_slot_after}/{total_product_storage} product storage entries have valid box slots ({product_storage_with_valid_slot_after/total_product_storage*100:.2f}%)")


def update_box_occupied_status():
    """Update the occupied status of all box slots."""
    print_section("Updating Box Slot Occupied Status")
    
    # Get all box slots with products
    slots_with_products = BoxSlot.objects.annotate(
        stored_product_count=Count('stored_products')
    ).filter(stored_product_count__gt=0)
    
    print(f"Updating occupied status for {slots_with_products.count()} box slots with products...")
    
    # Update occupied status
    with transaction.atomic():
        for slot in slots_with_products:
            if not slot.occupied:
                slot.occupied = True
                slot.save(update_fields=['occupied'])
                print(f"Updated box slot {slot.slot_code} to occupied=True")
    
    print("Box slot occupied status update complete")


def main():
    """Main function to run all fixes."""
    print_section("Inventory Relationship Fix Script")
    
    # Fix storage location assignments for boxes
    fix_box_storage_locations()
    
    # Fix product storage links to box slots
    fix_product_storage_box_slot_links()
    
    # Update box occupied status
    update_box_occupied_status()
    
    print_section("Fix Complete")
    print("Run inventory_relationship_test.py to verify the fixes")


if __name__ == "__main__":
    main() 