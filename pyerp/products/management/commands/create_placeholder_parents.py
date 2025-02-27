from django.core.management.base import BaseCommand
from pyerp.products.models import VariantProduct, ParentProduct
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates placeholder parent products for variants without parents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate the operation without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS("\n=== CREATING PLACEHOLDER PARENT PRODUCTS ===\n"))
        
        # Get variants without parents
        variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)
        total_orphans = variants_without_parent.count()
        
        self.stdout.write(f"Found {total_orphans} variants without parent products.")
        
        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned variants found. Nothing to do."))
            return
        
        # Ask for confirmation if not forced
        if not force and not dry_run:
            self.stdout.write("\nThis command will create placeholder parent products for orphaned variants.")
            self.stdout.write("These placeholder parents will use data from their variants with a 'PLACEHOLDER' prefix.")
            
            confirm = input("Do you want to proceed? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return
        
        # Create parents and update relationships
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No actual changes will be made\n"))
        
        # Track results
        created_parents = 0
        updated_relationships = 0
        errors = 0
        error_details = []
        
        # Use transaction to ensure atomicity - only for dry run
        if dry_run:
            with transaction.atomic():
                # Create a savepoint for rollback in case of dry run
                sid = transaction.savepoint()
                
                for variant in variants_without_parent:
                    try:
                        # Create placeholder parent
                        parent = ParentProduct(
                            sku=f"PLACEHOLDER-{variant.sku}",
                            name=f"PLACEHOLDER - {variant.name}" if variant.name else f"PLACEHOLDER Parent for {variant.sku}",
                            is_active=variant.is_active,
                            # Set legacy_id to match the variant's legacy_familie for proper linking
                            legacy_id=variant.legacy_familie,
                            is_placeholder=True,
                            # Set base_sku to match the variant's base_sku if available
                            base_sku=variant.base_sku if hasattr(variant, 'base_sku') and variant.base_sku else variant.sku
                        )
                        
                        if not dry_run:
                            parent.save()
                        created_parents += 1
                        
                        # Update variant to link to this parent
                        if not dry_run:
                            variant.parent = parent
                            variant.save()
                        updated_relationships += 1
                        
                        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Created placeholder parent {parent.sku} for variant {variant.sku}")
                    except Exception as e:
                        errors += 1
                        error_details.append(f"Error processing variant {variant.sku}: {str(e)}")
                        self.stdout.write(self.style.ERROR(f"Error processing variant {variant.sku}: {str(e)}"))
                
                # If dry run, rollback all changes
                if dry_run:
                    transaction.savepoint_rollback(sid)
                    self.stdout.write(self.style.WARNING("\n[DRY RUN] All changes have been rolled back\n"))
        else:
            # Process each variant individually without a transaction
            for variant in variants_without_parent:
                try:
                    # Create placeholder parent
                    parent = ParentProduct(
                        sku=f"PLACEHOLDER-{variant.sku}",
                        name=f"PLACEHOLDER - {variant.name}" if variant.name else f"PLACEHOLDER Parent for {variant.sku}",
                        is_active=variant.is_active,
                        # Set legacy_id to match the variant's legacy_familie for proper linking
                        legacy_id=variant.legacy_familie,
                        is_placeholder=True,
                        # Set base_sku to match the variant's base_sku if available
                        base_sku=variant.base_sku if hasattr(variant, 'base_sku') and variant.base_sku else variant.sku
                    )
                    
                    parent.save()
                    created_parents += 1
                    
                    # Update variant to link to this parent
                    variant.parent = parent
                    variant.save()
                    updated_relationships += 1
                    
                    self.stdout.write(f"Created placeholder parent {parent.sku} for variant {variant.sku}")
                except Exception as e:
                    errors += 1
                    error_details.append(f"Error processing variant {variant.sku}: {str(e)}")
                    self.stdout.write(self.style.ERROR(f"Error processing variant {variant.sku}: {str(e)}"))
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION SUMMARY ==="))
        self.stdout.write(f"Total orphaned variants: {total_orphans}")
        self.stdout.write(f"Placeholder parents {'would be' if dry_run else ''} created: {created_parents}")
        self.stdout.write(f"Variant relationships {'would be' if dry_run else ''} updated: {updated_relationships}")
        self.stdout.write(f"Errors encountered: {errors}")
        
        if errors > 0:
            self.stdout.write(self.style.ERROR("\n=== ERROR DETAILS ==="))
            for error in error_details:
                self.stdout.write(self.style.ERROR(error))
        
        if total_orphans > 0:
            success_rate = (updated_relationships / total_orphans) * 100
            self.stdout.write(f"Success rate: {success_rate:.2f}%")
        
        # Next steps
        self.stdout.write(self.style.SUCCESS("\n=== NEXT STEPS ==="))
        self.stdout.write("1. Review the created placeholder parents in the admin interface")
        self.stdout.write("2. Add additional data to the placeholder parents as needed")
        self.stdout.write("3. Run validation checks to ensure proper parent-child relationships")
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION COMPLETE ===\n")) 