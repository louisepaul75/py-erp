#!/usr/bin/env python
"""
Script to analyze inventory structure and compare with legacy ERP tables.

This script reads the actual inventory structure from the database and compares
it with the legacy ERP tables to provide a comprehensive comparison.
"""

import os
import sys
import django
from django.db import connection
from django.db.models import Count, Sum, F, Q
import pandas as pd
from tabulate import tabulate

# Set up Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pyerp.config.settings.development")
django.setup()

# Import models after Django setup
from pyerp.business_modules.inventory.models import (
    StorageLocation,
    BoxType,
    Box,
    BoxSlot,
    ProductStorage,
    BoxStorage,
    InventoryMovement
)
from pyerp.business_modules.products.models import VariantProduct
from pyerp.external_api.legacy_erp.client import LegacyERPClient


def print_section(title):
    """Print a section title with decorative formatting."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")


def analyze_storage_locations():
    """Analyze storage locations and compare with legacy data."""
    print_section("STORAGE LOCATIONS")
    
    # Get current data
    locations = StorageLocation.objects.all()
    location_count = locations.count()
    
    # Get legacy data
    legacy_client = LegacyERPClient(environment="live")
    legacy_locations = legacy_client.fetch_table("Stamm_Lagerorte", top=10000)
    legacy_location_count = len(legacy_locations)
    
    # Print summary
    print(f"Current system has {location_count} storage locations")
    print(f"Legacy system has {legacy_location_count} storage locations")
    print(f"Synchronization rate: {(location_count / legacy_location_count * 100):.2f}%")
    
    # Sample data comparison
    print("\nSample data comparison:")
    
    # Current system sample
    current_sample = locations.order_by('?')[:5]
    current_data = []
    for loc in current_sample:
        current_data.append({
            'ID': loc.id,
            'Legacy ID': loc.legacy_id,
            'Country': loc.country,
            'City/Building': loc.city_building,
            'Unit': loc.unit,
            'Compartment': loc.compartment,
            'Shelf': loc.shelf,
            'Location Code': loc.location_code,
            'Name': loc.name,
            'Is Active': loc.is_active,
        })
    
    # Legacy system sample
    legacy_sample = legacy_locations.sample(min(5, len(legacy_locations)))
    legacy_data = []
    for _, row in legacy_sample.iterrows():
        legacy_data.append({
            'UUID': row.get('UUID', ''),
            'Land_LKZ': row.get('Land_LKZ', ''),
            'Ort_Gebaeude': row.get('Ort_Gebaeude', ''),
            'Regal': row.get('Regal', ''),
            'Fach': row.get('Fach', ''),
            'Boden': row.get('Boden', ''),
            'Lagerort': row.get('Lagerort', ''),
            'Abverkauf': row.get('Abverkauf', ''),
            'Sonderlager': row.get('Sonderlager', ''),
        })
    
    print("\nCurrent System Sample:")
    print(tabulate(current_data, headers="keys", tablefmt="grid"))
    
    print("\nLegacy System Sample:")
    print(tabulate(legacy_data, headers="keys", tablefmt="grid"))
    
    # Field mapping
    print("\nField Mapping:")
    field_mapping = [
        {'Current Field': 'country', 'Legacy Field': 'Land_LKZ', 'Description': 'Country code'},
        {'Current Field': 'city_building', 'Legacy Field': 'Ort_Gebaeude', 'Description': 'City and building'},
        {'Current Field': 'unit', 'Legacy Field': 'Regal', 'Description': 'Storage unit identifier'},
        {'Current Field': 'compartment', 'Legacy Field': 'Fach', 'Description': 'Compartment within unit'},
        {'Current Field': 'shelf', 'Legacy Field': 'Boden', 'Description': 'Shelf identifier'},
        {'Current Field': 'location_code', 'Legacy Field': 'Lagerort', 'Description': 'Formatted location code'},
        {'Current Field': 'sale', 'Legacy Field': 'Abverkauf', 'Description': 'Whether products are for sale'},
        {'Current Field': 'special_spot', 'Legacy Field': 'Sonderlager', 'Description': 'Special storage spot'},
    ]
    print(tabulate(field_mapping, headers="keys", tablefmt="grid"))


def analyze_box_types():
    """Analyze box types and compare with legacy data."""
    print_section("BOX TYPES")
    
    # Get current data
    box_types = BoxType.objects.all()
    box_type_count = box_types.count()
    
    # Get legacy data - box types might be in a parameter table
    try:
        legacy_client = LegacyERPClient(environment="live")
        legacy_params = legacy_client.fetch_table("parameter", top=10000)
        legacy_box_types = legacy_params[legacy_params['Gruppe'] == 'Schüttentypen']
        legacy_box_type_count = len(legacy_box_types)
        
        # Print summary
        print(f"Current system has {box_type_count} box types")
        print(f"Legacy system has {legacy_box_type_count} box types in Parameter table")
        
        # Sample data comparison
        print("\nSample data comparison:")
        
        # Current system sample
        current_sample = box_types.order_by('?')[:5]
        current_data = []
        for bt in current_sample:
            current_data.append({
                'ID': bt.id,
                'Name': bt.name,
                'Length': bt.length,
                'Width': bt.width,
                'Height': bt.height,
                'Weight': bt.weight_empty,
                'Slot Count': bt.slot_count,
                'Color': bt.color,
            })
        
        print("\nCurrent System Sample:")
        print(tabulate(current_data, headers="keys", tablefmt="grid"))
        
        # Legacy system might have different structure, so we'll just show what's available
        if not legacy_box_types.empty:
            legacy_sample = legacy_box_types.sample(min(5, len(legacy_box_types)))
            legacy_data = []
            for _, row in legacy_sample.iterrows():
                legacy_data.append({
                    'Schlüssel': row.get('Schlüssel', ''),
                    'Wert': row.get('Wert', ''),
                    'Beschreibung': row.get('Beschreibung', ''),
                })
            
            print("\nLegacy System Sample (from Parameter table):")
            print(tabulate(legacy_data, headers="keys", tablefmt="grid"))
    except Exception as e:
        print(f"Error accessing legacy Parameter table: {e}")
        print(f"Current system has {box_type_count} box types")
        
        # Still show current system data
        current_sample = box_types.order_by('?')[:5]
        current_data = []
        for bt in current_sample:
            current_data.append({
                'ID': bt.id,
                'Name': bt.name,
                'Length': bt.length,
                'Width': bt.width,
                'Height': bt.height,
                'Weight': bt.weight_empty,
                'Slot Count': bt.slot_count,
                'Color': bt.color,
            })
        
        print("\nCurrent System Sample:")
        print(tabulate(current_data, headers="keys", tablefmt="grid"))
        
        # Try to find box types in other tables
        try:
            # Box types might be in Lager_Schuetten table
            legacy_boxes = legacy_client.fetch_table("Lager_Schuetten", top=10000)
            if 'Schüttentyp' in legacy_boxes.columns:
                box_types_in_boxes = legacy_boxes['Schüttentyp'].unique()
                print(f"\nFound {len(box_types_in_boxes)} unique box types in Lager_Schuetten table:")
                for bt in box_types_in_boxes[:10]:  # Show first 10
                    print(f"  - {bt}")
                if len(box_types_in_boxes) > 10:
                    print(f"  ... and {len(box_types_in_boxes) - 10} more")
        except Exception as inner_e:
            print(f"Error trying to find box types in other tables: {inner_e}")


def analyze_boxes():
    """Analyze boxes and compare with legacy data."""
    print_section("BOXES")
    
    # Get current data
    boxes = Box.objects.all()
    box_count = boxes.count()
    
    # Get legacy data
    legacy_client = LegacyERPClient(environment="live")
    legacy_boxes = legacy_client.fetch_table("Lager_Schuetten", top=10000)
    legacy_box_count = len(legacy_boxes)
    
    # Print summary
    print(f"Current system has {box_count} boxes")
    print(f"Legacy system has {legacy_box_count} boxes")
    print(f"Synchronization rate: {(box_count / legacy_box_count * 100):.2f}%")
    
    # Sample data comparison
    print("\nSample data comparison:")
    
    # Current system sample
    current_sample = boxes.select_related('box_type', 'storage_location').order_by('?')[:5]
    current_data = []
    for box in current_sample:
        current_data.append({
            'ID': box.id,
            'Legacy ID': box.legacy_id,
            'Code': box.code,
            'Box Type': box.box_type.name if box.box_type else '',
            'Storage Location': box.storage_location.location_code if box.storage_location else '',
            'Status': box.status,
            'Purpose': box.purpose,
        })
    
    # Legacy system sample
    legacy_sample = legacy_boxes.sample(min(5, len(legacy_boxes)))
    legacy_data = []
    for _, row in legacy_sample.iterrows():
        legacy_data.append({
            'UUID': row.get('UUID', ''),
            'Schütte': row.get('Schütte', ''),
            'UUID_Stamm_Lagerorte': row.get('UUID_Stamm_Lagerorte', ''),
            'Schüttentyp': row.get('Schüttentyp', ''),
            'Status': row.get('Status', ''),
        })
    
    print("\nCurrent System Sample:")
    print(tabulate(current_data, headers="keys", tablefmt="grid"))
    
    print("\nLegacy System Sample:")
    print(tabulate(legacy_data, headers="keys", tablefmt="grid"))
    
    # Field mapping
    print("\nField Mapping:")
    field_mapping = [
        {'Current Field': 'code', 'Legacy Field': 'Schütte', 'Description': 'Box identifier'},
        {'Current Field': 'storage_location', 'Legacy Field': 'UUID_Stamm_Lagerorte', 'Description': 'Storage location reference'},
        {'Current Field': 'box_type', 'Legacy Field': 'Schüttentyp', 'Description': 'Box type reference'},
        {'Current Field': 'status', 'Legacy Field': 'Status', 'Description': 'Box status'},
    ]
    print(tabulate(field_mapping, headers="keys", tablefmt="grid"))


def analyze_product_storage():
    """Analyze product storage and compare with legacy data."""
    print_section("PRODUCT STORAGE")
    
    # Get current data
    product_storage = ProductStorage.objects.all()
    product_storage_count = product_storage.count()
    
    # Get legacy data
    legacy_client = LegacyERPClient(environment="live")
    legacy_product_storage = legacy_client.fetch_table("Artikel_Lagerorte", top=10000)
    legacy_product_storage_count = len(legacy_product_storage)
    
    # Print summary
    print(f"Current system has {product_storage_count} product storage entries")
    print(f"Legacy system has {legacy_product_storage_count} product storage entries")
    print(f"Synchronization rate: {(product_storage_count / legacy_product_storage_count * 100):.2f}%")
    
    # Sample data comparison
    print("\nSample data comparison:")
    
    # Current system sample
    current_sample = product_storage.select_related('product', 'storage_location').order_by('?')[:5]
    current_data = []
    for ps in current_sample:
        current_data.append({
            'ID': ps.id,
            'Legacy ID': ps.legacy_id,
            'Product': ps.product.sku if ps.product else '',
            'Storage Location': ps.storage_location.location_code if ps.storage_location else '',
            'Quantity': ps.quantity,
            'Reservation Status': ps.reservation_status,
        })
    
    # Legacy system sample
    legacy_sample = legacy_product_storage.sample(min(5, len(legacy_product_storage)))
    legacy_data = []
    for _, row in legacy_sample.iterrows():
        legacy_data.append({
            'UUID': row.get('UUID', ''),
            'UUID_Artikel_Variante': row.get('UUID_Artikel_Variante', ''),
            'UUID_Stamm_Lagerorte': row.get('UUID_Stamm_Lagerorte', ''),
            'Bestand': row.get('Bestand', ''),
            'Reserviert': row.get('Reserviert', ''),
        })
    
    print("\nCurrent System Sample:")
    print(tabulate(current_data, headers="keys", tablefmt="grid"))
    
    print("\nLegacy System Sample:")
    print(tabulate(legacy_data, headers="keys", tablefmt="grid"))
    
    # Field mapping
    print("\nField Mapping:")
    field_mapping = [
        {'Current Field': 'product', 'Legacy Field': 'UUID_Artikel_Variante', 'Description': 'Product reference'},
        {'Current Field': 'storage_location', 'Legacy Field': 'UUID_Stamm_Lagerorte', 'Description': 'Storage location reference'},
        {'Current Field': 'quantity', 'Legacy Field': 'Bestand', 'Description': 'Quantity in stock'},
        {'Current Field': 'reservation_status', 'Legacy Field': 'Reserviert', 'Description': 'Reservation status'},
    ]
    print(tabulate(field_mapping, headers="keys", tablefmt="grid"))


def analyze_box_storage():
    """Analyze box storage and compare with legacy data."""
    print_section("BOX STORAGE")
    
    # Get current data
    box_storage = BoxStorage.objects.all()
    box_storage_count = box_storage.count()
    
    # Get legacy data - this might be in Lager_Schuetten_Slots or similar
    legacy_client = LegacyERPClient(environment="live")
    legacy_box_slots = legacy_client.fetch_table("Lager_Schuetten_Slots", top=10000)
    legacy_box_slot_count = len(legacy_box_slots)
    
    # Print summary
    print(f"Current system has {box_storage_count} box storage entries")
    print(f"Legacy system has {legacy_box_slot_count} box slot entries")
    
    # Sample data comparison
    print("\nSample data comparison:")
    
    # Current system sample
    current_sample = box_storage.select_related(
        'product_storage__product', 
        'box_slot__box'
    ).order_by('?')[:5]
    
    current_data = []
    for bs in current_sample:
        current_data.append({
            'ID': bs.id,
            'Legacy ID': bs.legacy_id,
            'Product': bs.product_storage.product.sku if bs.product_storage and bs.product_storage.product else '',
            'Box Slot': f"{bs.box_slot.box.code}.{bs.box_slot.slot_code}" if bs.box_slot and bs.box_slot.box else '',
            'Quantity': bs.quantity,
            'Position': bs.position_in_slot,
            'Batch': bs.batch_number,
        })
    
    # Legacy system sample
    if not legacy_box_slots.empty:
        legacy_sample = legacy_box_slots.sample(min(5, len(legacy_box_slots)))
        legacy_data = []
        for _, row in legacy_sample.iterrows():
            legacy_data.append({
                'UUID': row.get('UUID', ''),
                'ID_Lager_Schuetten': row.get('ID_Lager_Schuetten', ''),
                'Lfd_Nr': row.get('Lfd_Nr', ''),
                'Einheiten_Nr': row.get('Einheiten_Nr', ''),
                'Einheitenfabe': row.get('Einheitenfabe', ''),
            })
        
        print("\nCurrent System Sample:")
        print(tabulate(current_data, headers="keys", tablefmt="grid"))
        
        print("\nLegacy System Sample (from Lager_Schuetten_Slots):")
        print(tabulate(legacy_data, headers="keys", tablefmt="grid"))


def analyze_inventory_movements():
    """Analyze inventory movements and compare with legacy data."""
    print_section("INVENTORY MOVEMENTS")
    
    # Get current data
    movements = InventoryMovement.objects.all()
    movement_count = movements.count()
    
    # Get movement types distribution
    movement_types = movements.values('movement_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Print summary
    print(f"Current system has {movement_count} inventory movements")
    
    # Movement types distribution
    print("\nMovement Types Distribution:")
    movement_type_data = []
    for mt in movement_types:
        movement_type_data.append({
            'Movement Type': mt['movement_type'],
            'Count': mt['count'],
            'Percentage': f"{(mt['count'] / movement_count * 100):.2f}%",
        })
    
    print(tabulate(movement_type_data, headers="keys", tablefmt="grid"))
    
    # Sample data
    print("\nSample data:")
    current_sample = movements.select_related('product', 'from_slot', 'to_slot').order_by('?')[:5]
    current_data = []
    for m in current_sample:
        current_data.append({
            'ID': m.id,
            'Legacy ID': m.legacy_id,
            'Product': m.product.sku if m.product else '',
            'From Slot': str(m.from_slot) if m.from_slot else 'None',
            'To Slot': str(m.to_slot) if m.to_slot else 'None',
            'Quantity': m.quantity,
            'Movement Type': m.movement_type,
            'Reference': m.reference,
            'Timestamp': m.timestamp,
        })
    
    print(tabulate(current_data, headers="keys", tablefmt="grid"))


def analyze_inventory_structure():
    """Analyze the complete inventory structure and compare with legacy data."""
    print_section("INVENTORY STRUCTURE ANALYSIS")
    
    # Analyze each component with error handling
    try:
        analyze_storage_locations()
    except Exception as e:
        print(f"Error analyzing storage locations: {e}")
    
    try:
        analyze_box_types()
    except Exception as e:
        print(f"Error analyzing box types: {e}")
    
    try:
        analyze_boxes()
    except Exception as e:
        print(f"Error analyzing boxes: {e}")
    
    try:
        analyze_product_storage()
    except Exception as e:
        print(f"Error analyzing product storage: {e}")
    
    try:
        analyze_box_storage()
    except Exception as e:
        print(f"Error analyzing box storage: {e}")
    
    try:
        analyze_inventory_movements()
    except Exception as e:
        print(f"Error analyzing inventory movements: {e}")
    
    # Print overall summary
    print_section("OVERALL SUMMARY")
    
    # Count records in each table
    storage_location_count = StorageLocation.objects.count()
    box_type_count = BoxType.objects.count()
    box_count = Box.objects.count()
    box_slot_count = BoxSlot.objects.count()
    product_storage_count = ProductStorage.objects.count()
    box_storage_count = BoxStorage.objects.count()
    movement_count = InventoryMovement.objects.count()
    
    # Create summary table
    summary_data = [
        {'Entity': 'Storage Locations', 'Count': storage_location_count},
        {'Entity': 'Box Types', 'Count': box_type_count},
        {'Entity': 'Boxes', 'Count': box_count},
        {'Entity': 'Box Slots', 'Count': box_slot_count},
        {'Entity': 'Product Storage Entries', 'Count': product_storage_count},
        {'Entity': 'Box Storage Entries', 'Count': box_storage_count},
        {'Entity': 'Inventory Movements', 'Count': movement_count},
    ]
    
    print(tabulate(summary_data, headers="keys", tablefmt="grid"))
    
    # Legacy system mapping
    print("\nLegacy System Mapping:")
    legacy_mapping = [
        {'Current Entity': 'StorageLocation', 'Legacy Table': 'Stamm_Lagerorte', 'Description': 'Physical storage locations'},
        {'Current Entity': 'BoxType', 'Legacy Table': 'Parameter (Schüttentypen) or Lager_Schuetten.Schüttentyp', 'Description': 'Box type definitions'},
        {'Current Entity': 'Box', 'Legacy Table': 'Lager_Schuetten', 'Description': 'Physical boxes'},
        {'Current Entity': 'BoxSlot', 'Legacy Table': 'Lager_Schuetten_Slots', 'Description': 'Slots within boxes'},
        {'Current Entity': 'ProductStorage', 'Legacy Table': 'Artikel_Lagerorte', 'Description': 'Product storage locations'},
        {'Current Entity': 'BoxStorage', 'Legacy Table': 'Lager_Schuetten_Artikel', 'Description': 'Products in box slots'},
        {'Current Entity': 'InventoryMovement', 'Legacy Table': 'Various tables', 'Description': 'Movement tracking'},
    ]
    
    print(tabulate(legacy_mapping, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    analyze_inventory_structure()
