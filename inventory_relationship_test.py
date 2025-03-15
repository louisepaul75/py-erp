#!/usr/bin/env python
"""
Inventory Relationship Test Script

This script tests the relationships between the tables in the inventory system,
specifically focusing on the connections between Box, BoxSlot, and ProductStorage.
It identifies any inconsistencies or issues in the data relationships.
"""

import os
import sys
import django
from collections import defaultdict
from django.db.models import Count, Q, F
from django.db import connection

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.settings.dev")
django.setup()

# Import models after Django setup
from pyerp.business_modules.inventory.models import Box, BoxSlot, ProductStorage, StorageLocation


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


def test_box_slot_lookup_integrity():
    """Test the integrity of box slot lookups used in the sync process."""
    print_section("Box Slot Lookup Integrity Test")
    
    # Simulate the lookup process used in ProductStorageTransformer._get_box_slot
    # This will help identify if there are issues with how box slots are being looked up
    
    # Get all boxes with legacy_id
    boxes_with_legacy_id = Box.objects.filter(legacy_id__isnull=False)
    print(f"Boxes with legacy_id: {boxes_with_legacy_id.count()}")
    
    # Check if each box has at least one slot with slot_number=1
    boxes_without_default_slot = 0
    for box in boxes_with_legacy_id:
        if not BoxSlot.objects.filter(box=box, slot_number=1).exists():
            boxes_without_default_slot += 1
    
    print(f"Boxes without a default slot (slot_number=1): {boxes_without_default_slot}")
    
    # Check for boxes with multiple slots having the same slot_number
    boxes_with_duplicate_slot_numbers = 0
    for box in boxes_with_legacy_id:
        slot_counts = BoxSlot.objects.filter(box=box).values('slot_number').annotate(count=Count('id')).filter(count__gt=1)
        if slot_counts.exists():
            boxes_with_duplicate_slot_numbers += 1
    
    print(f"Boxes with duplicate slot numbers: {boxes_with_duplicate_slot_numbers}")


def test_product_storage_box_slot_consistency():
    """Test the consistency between ProductStorage and BoxSlot."""
    print_section("ProductStorage to BoxSlot Consistency Test")
    
    # Check if all box_slot_id values in ProductStorage correspond to valid BoxSlot instances
    total_product_storage = ProductStorage.objects.count()
    valid_box_slot_ids = set(BoxSlot.objects.values_list('id', flat=True))
    
    # Use raw SQL for efficiency with large datasets
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pyerp_business_modules_inventory_productstorage 
            WHERE box_slot_id NOT IN (
                SELECT id FROM pyerp_business_modules_inventory_boxslot
            )
        """)
        invalid_box_slot_refs = cursor.fetchone()[0]
    
    print(f"Total ProductStorage entries: {total_product_storage}")
    print(f"ProductStorage entries with invalid box_slot_id: {invalid_box_slot_refs}")
    
    if invalid_box_slot_refs > 0:
        # Get some examples of invalid references
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, box_slot_id 
                FROM pyerp_business_modules_inventory_productstorage 
                WHERE box_slot_id NOT IN (
                    SELECT id FROM pyerp_business_modules_inventory_boxslot
                )
                LIMIT 5
            """)
            examples = cursor.fetchall()
        
        print("\nExamples of ProductStorage entries with invalid box_slot_id:")
        for example in examples:
            print(f"  ProductStorage ID: {example[0]}, Invalid box_slot_id: {example[1]}")


def main():
    """Run all tests."""
    print("Starting Inventory Relationship Tests...")
    
    test_box_boxslot_relationship()
    test_boxslot_productstorage_relationship()
    test_box_storage_location_relationship()
    test_legacy_id_consistency()
    test_box_slot_lookup_integrity()
    test_product_storage_box_slot_consistency()
    
    print("\nInventory Relationship Tests completed.")


if __name__ == "__main__":
    main() 