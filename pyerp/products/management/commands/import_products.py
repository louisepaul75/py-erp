"""Management command to import products from the legacy 4D system."""
import logging
import os
import sys
import pandas as pd
import math
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from django.db import transaction

from pyerp.products.models import Product, ProductCategory

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

# Import the necessary functions from WSZ_api
from wsz_api.getTable import fetch_data_from_api

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import products from the legacy 4D system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit the number of products to import',
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing products',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to the database',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print debug information',
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        self.stdout.write("Starting product import from 4D...")
        
        # Command options
        self.limit = options['limit']
        self.update = options['update']
        self.dry_run = options['dry_run']
        self.debug = options['debug']
        
        # Get or create default category
        self.default_category, _ = ProductCategory.objects.get_or_create(
            code='UNCATEGORIZED',
            defaults={
                'name': 'Uncategorized',
                'description': 'Default category for products without a specific category'
            }
        )
        
        # Fetch data from Artikel_Stamm
        self.stdout.write("Fetching data from Artikel_Stamm table...")
        try:
            # Import fetch_data_from_api from WSZ_API
            data = fetch_data_from_api("Artikel_Stamm")
            self.stdout.write(f"Retrieved {len(data)} records")
            
            if self.debug:
                # Print column names
                self.stdout.write("Column names:")
                for column in data[0].keys():
                    self.stdout.write(f"- {column}")
                
                # Print first few rows for debugging
                self.stdout.write("\nFirst 5 rows:")
                for i in range(min(5, len(data))):
                    self.stdout.write(f"\nRow {i}:")
                    for key, value in data[i].items():
                        self.stdout.write(f"  {key}: {value}")
            
            # Process data
            skipped = 0
            created = 0
            updated = 0
            
            # Limit the number of records to process if specified
            if self.limit > 0:
                data = data[:self.limit]
            
            # Process each record
            for index, row in enumerate(data):
                # Get product data
                product_data = self.extract_product_data(row, index)
                
                if not product_data:
                    skipped += 1
                    continue
                
                # Skip processing in dry run mode
                if self.dry_run:
                    self.stdout.write(f"[DRY RUN] Would create product: {product_data['base_sku']} - {product_data['name']}")
                    continue
                
                # Check if product exists
                try:
                    product = Product.objects.get(base_sku=product_data['base_sku'], variant_code=product_data['variant_code'])
                    
                    # Update product if --update flag is set
                    if self.update:
                        for key, value in product_data.items():
                            setattr(product, key, value)
                        product.save()
                        updated += 1
                        self.stdout.write(f"Updated product: {product.base_sku}-{product.variant_code} - {product.name}")
                    else:
                        skipped += 1
                        self.stdout.write(f"Skipped existing product: {product.base_sku}-{product.variant_code}")
                
                except Product.DoesNotExist:
                    # Create new product
                    Product.objects.create(**product_data)
                    created += 1
                    self.stdout.write(f"Created product: {product_data['base_sku']}-{product_data['variant_code']} - {product_data['name']}")
                
                # Print progress every 100 records
                if (index + 1) % 100 == 0:
                    self.stdout.write(f"Processed {index + 1} records...")
            
            if self.dry_run:
                self.stdout.write("DRY RUN - No changes were made to the database")
            
            self.stdout.write("Import completed:")
            self.stdout.write(f"  Products created: {created}")
            self.stdout.write(f"  Products updated: {updated}")
            self.stdout.write(f"  Products skipped: {skipped}")
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            raise

    def extract_product_data(self, row, index):
        """Extract product data from a row."""
        try:
            # Check if row is a dictionary as expected
            if not isinstance(row, dict):
                self.stdout.write(self.style.ERROR(f"Row {index} is not a dictionary, but a {type(row)}"))
                return None
            
            # Get ID for debugging
            legacy_id = self.get_value(row, 'ID', '')
            
            # Debug log
            if self.debug:
                self.stdout.write(f"\nProcessing row {index}:")
                self.stdout.write(f"  ID: {legacy_id}")
                self.stdout.write(f"  Bezeichnung: {self.get_value(row, 'Bezeichnung', '')}")
                self.stdout.write(f"  ArtikelArt: {self.get_value(row, 'ArtikelArt', '')}")
                
            # Try to get SKU from different possible fields
            base_sku = None
            variant_code = self.get_value(row, 'ArtikelArt', '')
            
            # First try ArtNr which seems to be the main field
            full_sku = self.get_value(row, 'ArtNr', '')
            if full_sku:
                # If SKU contains a dash, split into base and variant
                if '-' in full_sku:
                    parts = full_sku.split('-', 1)
                    base_sku = parts[0]
                    variant_code = parts[1]
                else:
                    base_sku = full_sku
                    
                if self.debug:
                    self.stdout.write(f"  Found SKU in column ArtNr: {full_sku}")
            
            # If still no SKU, try fk_ArtNr
            if not base_sku:
                base_sku = self.get_value(row, 'fk_ArtNr', '')
                if base_sku and self.debug:
                    self.stdout.write(f"  Found SKU in column fk_ArtNr: {base_sku}")
            
            # If still no SKU, try ID as last resort
            if not base_sku:
                base_sku = str(legacy_id)
                if self.debug:
                    self.stdout.write(f"  Using ID as SKU: {base_sku}")
            
            # Skip if no valid SKU
            if not base_sku:
                if self.debug:
                    self.stdout.write(f"  Skipping row {index} - No valid SKU")
                return None
            
            # Try to find category from ArtGruppe
            category = self.default_category
            art_gruppe_code = self.get_value(row, 'ArtGruppe', '')
            if art_gruppe_code:
                try:
                    category_obj = ProductCategory.objects.get(code=art_gruppe_code)
                    category = category_obj
                except ProductCategory.DoesNotExist:
                    # Create a new category if it doesn't exist
                    category_name = art_gruppe_code  # Use code as name if no mapping exists
                    category = ProductCategory.objects.create(
                        code=art_gruppe_code,
                        name=category_name,
                        description=f'Category imported from legacy system with code {art_gruppe_code}'
                    )
                    
            # Extract dimensions from 'Masse' field
            dimensions = self.get_value(row, 'Masse', '')
            
            # Create product data dictionary with all available fields
            product_data = {
                'base_sku': base_sku,
                'variant_code': variant_code,
                'name': self.get_value(row, 'Bezeichnung', ''),
                'name_en': self.get_value(row, 'Bezeichnung_ENG', ''),
                'legacy_id': str(legacy_id),
                'short_description': self.get_value(row, 'Beschreibung_kurz', '')[:500] if self.get_value(row, 'Beschreibung_kurz', '') else '',
                'short_description_en': self.get_value(row, 'Beschreibung_kurz_ENG', '')[:500] if self.get_value(row, 'Beschreibung_kurz_ENG', '') else '',
                'description': self.get_value(row, 'Beschreibung', ''),
                'description_en': self.get_value(row, 'Beschreibung_ENG', ''),
                'keywords': self.get_value(row, 'Keywords', ''),
                'dimensions': dimensions,
                'weight': self.get_value(row, 'Gewicht', 0) or 0,
                'list_price': self.get_value(row, 'PreisL', 0) or 0,
                'wholesale_price': self.get_value(row, 'PreisH', 0) or 0,
                'gross_price': self.get_value(row, 'PreisL_Brutto', 0) or 0,
                'cost_price': self.get_value(row, 'PreisEinkauf', 0) or 0,
                'stock_quantity': self.get_value(row, 'Bestand', 0) or 0,
                'min_stock_quantity': self.get_value(row, 'MindBestand', 0) or 0,
                'backorder_quantity': self.get_value(row, 'Auftragsbestand', 0) or 0,
                'open_purchase_quantity': self.get_value(row, 'bestelltOffen', 0) or 0,
                'is_active': True,  # Default to active
                'is_discontinued': bool(self.get_value(row, 'Auslauf', False)),
                'has_bom': bool(self.get_value(row, 'Stückliste', False)),
                'is_one_sided': bool(self.get_value(row, 'eineSeite', False)),
                'is_hanging': bool(self.get_value(row, 'haengen', False)),
                'category': category,
            }
            
            # Set created_at if Aufnahme_Datum exists
            aufnahme_datum = self.get_value(row, 'Aufnahme_Datum', None)
            if aufnahme_datum and not isinstance(aufnahme_datum, str) and not pd.isna(aufnahme_datum):
                try:
                    product_data['created_at'] = aufnahme_datum
                except (ValueError, TypeError):
                    pass  # Ignore invalid dates
            
            return product_data
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing row {index}: {str(e)}"))
            return None

    def get_value(self, row, key, default):
        """Helper method to safely get values from row"""
        # First check if row is a dictionary
        if not isinstance(row, dict):
            return default
        
        if key in row:
            value = row[key]
            # Handle NaN values from pandas
            if isinstance(value, float) and math.isnan(value):
                return default
            # Handle NaT (Not a Time) values
            if pd.isna(value):
                return default
            return value
        return default

    @staticmethod
    def add_arguments(parser):
        """Add command arguments."""
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit the number of products to import'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing products'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without making changes to the database'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Print debug information'
        ) 