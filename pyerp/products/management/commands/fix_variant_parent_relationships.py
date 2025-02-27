"""
Management command to fix variant-parent relationships using Familie_ column from Artikel_Variante.
"""

import logging
import sys
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from pyerp.products.models import ParentProduct, VariantProduct

# Configure logging
logger = logging.getLogger(__name__)

# Add the WSZ_api path to the Python path
WSZ_API_PATH = r'C:\Users\Joan-Admin\PycharmProjects\WSZ_api'
if WSZ_API_PATH not in sys.path:
    sys.path.append(WSZ_API_PATH)

try:
    # Import the WSZ_api modules
    from wsz_api.getTable import fetch_data_from_api
except ImportError as e:
    logger.error(f"Failed to import WSZ_api modules: {e}")
    raise


class Command(BaseCommand):
    help = 'Fix variant-parent relationships using Familie_ column from Artikel_Variante'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Perform a dry run without saving to the database'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of variants to process'
        )
        parser.add_argument(
            '--orphans-only',
            action='store_true',
            help='Only process variants without a parent'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        orphans_only = options['orphans_only']

        self.stdout.write(self.style.NOTICE('Starting variant-parent relationship fix using Familie_ column...'))
        
        # Get variants to process
        if orphans_only:
            variants = VariantProduct.objects.filter(parent__isnull=True)
            self.stdout.write(self.style.NOTICE('Processing orphaned variants only'))
        else:
            variants = VariantProduct.objects.all()
            self.stdout.write(self.style.NOTICE('Processing all variants'))
        
        if limit:
            variants = variants[:limit]
        
        total_variants = variants.count()
        self.stdout.write(self.style.SUCCESS(f'Found {total_variants} variants to check'))
        
        # Fetch data from Artikel_Variante table
        self.stdout.write('Fetching data from Artikel_Variante table...')
        try:
            artikel_variante_df = fetch_data_from_api(
                table_name="Artikel_Variante",
                new_data_only=False
            )
            
            if artikel_variante_df is None or len(artikel_variante_df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Variante table"))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Fetched {len(artikel_variante_df)} records from Artikel_Variante'))
            
            # Create mappings for easier lookup
            legacy_id_to_familie = {}
            sku_to_familie = {}
            
            for index, row in artikel_variante_df.iterrows():
                uid = row['UID']
                nummer = row['Nummer'] if 'Nummer' in row and pd.notna(row['Nummer']) else None
                familie = row.get('Familie_')
                
                if familie is not None:
                    legacy_id_to_familie[uid] = familie
                    if nummer is not None:
                        sku_to_familie[str(nummer)] = familie
            
            # Fetch data from Artikel_Familie table
            self.stdout.write('Fetching data from Artikel_Familie table...')
            artikel_familie_df = fetch_data_from_api(
                table_name="Artikel_Familie",
                new_data_only=False
            )
            
            if artikel_familie_df is None or len(artikel_familie_df) == 0:
                self.stdout.write(self.style.ERROR("No data returned from Artikel_Familie table"))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Fetched {len(artikel_familie_df)} records from Artikel_Familie'))
            
            # Create mappings for easier lookup
            familie_id_to_parent = {}
            
            # Debug: Print some sample family_ids
            sample_familie_ids_uid = []
            sample_familie_ids_key = []
            
            # Debug: Print sample columns from Artikel_Familie
            if len(artikel_familie_df) > 0:
                sample_row = artikel_familie_df.iloc[0]
                self.stdout.write(f"Sample columns in Artikel_Familie: {list(sample_row.keys())}")
                
                # Print sample Nummer values
                self.stdout.write("Sample Nummer values from Artikel_Familie:")
                for idx, row in artikel_familie_df.head(10).iterrows():
                    if 'Nummer' in row and pd.notna(row['Nummer']):
                        self.stdout.write(f"  - UID: {row.get('UID', 'N/A')}, Nummer: {row['Nummer']}, Type: {type(row['Nummer'])}")
            
            for index, row in artikel_familie_df.iterrows():
                # Check for UID field
                familie_id_uid = row.get('UID', None)
                if familie_id_uid is not None and len(sample_familie_ids_uid) < 5:
                    sample_familie_ids_uid.append(familie_id_uid)
                
                # Check for KEY_ field
                familie_id_key = row.get('KEY_', None)
                if familie_id_key is not None and len(sample_familie_ids_key) < 5:
                    sample_familie_ids_key.append(familie_id_key)
                
                # Use __KEY as fallback
                familie_id = row.get('__KEY', None)
                
                # Get the Nummer field
                nummer = row['Nummer'] if 'Nummer' in row and pd.notna(row['Nummer']) else None
                
                if nummer is not None:
                    try:
                        parent = ParentProduct.objects.get(sku=str(nummer))
                        
                        # Add all possible ID fields to mapping
                        if familie_id_uid is not None:
                            familie_id_to_parent[familie_id_uid] = parent
                        if familie_id_key is not None:
                            familie_id_to_parent[familie_id_key] = parent
                        if familie_id is not None:
                            familie_id_to_parent[familie_id] = parent
                            
                    except ParentProduct.DoesNotExist:
                        pass
            
            # Debug: Print sample Familie IDs and see if they match any found in Artikel_Variante
            self.stdout.write(f"Sample Familie UID values from Artikel_Familie: {sample_familie_ids_uid}")
            self.stdout.write(f"Sample Familie KEY_ values from Artikel_Familie: {sample_familie_ids_key}")
            
            # Debug: Print sample Familie_ values from variants
            sample_variant_familie_ids = list(set(list(legacy_id_to_familie.values())[:5]))
            self.stdout.write(f"Sample Familie_ values from variants: {sample_variant_familie_ids}")
            
            # Verify if Familie_ from Artikel_Variante matches any of the ID fields from Artikel_Familie
            self.stdout.write("Checking if variant Familie_ values match any Familie IDs...")
            for familie_value in sample_variant_familie_ids:
                if familie_value in familie_id_to_parent:
                    self.stdout.write(f"  - Match found for Familie_ value: {familie_value}")
                else:
                    self.stdout.write(f"  - No match found for Familie_ value: {familie_value}")
            
            # Debug: Print total parents found
            self.stdout.write(f"Total parent products mapped: {len(familie_id_to_parent)}")
            
            # Debug: Sample mapping
            sample_mapping = dict(list(familie_id_to_parent.items())[:5])
            self.stdout.write(f"Sample family ID to parent mapping: {[(k, v.sku) for k, v in sample_mapping.items()]}")
            
            # Track statistics
            stats = {
                'total': total_variants,
                'fixed': 0,
                'already_correct': 0,
                'no_parent_found': 0,
                'errors': 0
            }
            
            # Process each variant
            with transaction.atomic():
                for variant in variants:
                    try:
                        # Print current status
                        parent_id = variant.parent.id if variant.parent else None
                        self.stdout.write(f"Checking variant: ID={variant.id}, SKU={variant.sku}, Legacy ID={variant.legacy_id}, Current Parent ID={parent_id}")
                        
                        # Try to find the parent using the Familie_ mapping
                        parent = None
                        familie_id = None
                        
                        # First, try to match by legacy_id
                        if variant.legacy_id in legacy_id_to_familie:
                            familie_id = legacy_id_to_familie[variant.legacy_id]
                            self.stdout.write(f"Found Familie ID {familie_id} by legacy_id")
                        # Second, try to match by SKU
                        elif variant.sku in sku_to_familie:
                            familie_id = sku_to_familie[variant.sku]
                            self.stdout.write(f"Found Familie ID {familie_id} by SKU")
                        # Third, try to match by legacy_sku if available
                        elif variant.legacy_sku and variant.legacy_sku in sku_to_familie:
                            familie_id = sku_to_familie[variant.legacy_sku]
                            self.stdout.write(f"Found Familie ID {familie_id} by legacy_sku")
                        
                        if familie_id and familie_id in familie_id_to_parent:
                            parent = familie_id_to_parent[familie_id]
                            self.stdout.write(f"Found parent product {parent.sku} by Familie ID {familie_id}")
                        
                        if parent:
                            # Check if the relationship is already correct
                            if variant.parent and variant.parent.id == parent.id:
                                self.stdout.write(f"Relationship already correct for variant {variant.id}")
                                stats['already_correct'] += 1
                            else:
                                # Update the relationship
                                old_parent_id = parent_id
                                
                                if not dry_run:
                                    variant.parent = parent
                                    # Also update the legacy_familie field for display
                                    if familie_id and not variant.legacy_familie:
                                        variant.legacy_familie = familie_id
                                    variant.save()
                                
                                self.stdout.write(self.style.SUCCESS(
                                    f"Fixed relationship: Variant ID={variant.id}, "
                                    f"Old Parent ID={old_parent_id} -> New Parent ID={parent.id}, "
                                    f"Familie_={familie_id}"
                                ))
                                stats['fixed'] += 1
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"No parent found for variant: {variant.id}"
                            ))
                            stats['no_parent_found'] += 1
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing variant {variant.id}: {str(e)}"))
                        stats['errors'] += 1
                
                # Commit or rollback based on dry_run
                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("DRY RUN - No changes were saved to the database"))
                else:
                    self.stdout.write(self.style.SUCCESS("Changes committed to the database"))
            
            # Print summary
            self.stdout.write(self.style.SUCCESS(
                f"\nFix summary:\n"
                f"Total variants: {stats['total']}\n"
                f"Fixed: {stats['fixed']}\n"
                f"Already correct: {stats['already_correct']}\n"
                f"No parent found: {stats['no_parent_found']}\n"
                f"Errors: {stats['errors']}"
            ))
            
            # Suggest next steps
            if stats['no_parent_found'] > 0:
                self.stdout.write(self.style.NOTICE(
                    "\nNext steps for variants without parents:\n"
                    "1. Run 'python manage.py fix_missing_variants --create-parents' to create placeholder parents\n"
                    "2. Run this command again to update the relationships"
                ))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing variants: {str(e)}"))
            raise 