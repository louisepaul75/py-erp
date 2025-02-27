from django.core.management.base import BaseCommand
from pyerp.products.models import VariantProduct, ParentProduct
from django.db import transaction

class Command(BaseCommand):
    help = 'Links variants without parents to existing parents with matching legacy_id values'

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
        
        self.stdout.write(self.style.SUCCESS("\n=== LINKING VARIANTS TO EXISTING PARENTS ===\n"))
        
        # Get variants without parents
        variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)
        total_orphans = variants_without_parent.count()
        
        self.stdout.write(f"Found {total_orphans} variants without parent products.")
        
        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned variants found. Nothing to do."))
            return
        
        # Ask for confirmation if not forced
        if not force and not dry_run:
            self.stdout.write("\nThis command will link variants without parents to existing parent products with matching legacy_id values.")
            
            confirm = input("Do you want to proceed? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return
        
        # Track results
        linked_variants = 0
        still_orphaned = 0
        errors = 0
        error_details = []
        
        # Create parents and update relationships
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No actual changes will be made\n"))
        
        # Use transaction to ensure atomicity for dry run
        if dry_run:
            with transaction.atomic():
                sid = transaction.savepoint()
                linked_variants, still_orphaned, errors = self._process_variants(variants_without_parent, dry_run, linked_variants, still_orphaned, errors, error_details)
                transaction.savepoint_rollback(sid)
                self.stdout.write(self.style.WARNING("\n[DRY RUN] All changes have been rolled back\n"))
        else:
            # Process each variant individually without a transaction
            linked_variants, still_orphaned, errors = self._process_variants(variants_without_parent, dry_run, linked_variants, still_orphaned, errors, error_details)
        
        # Summary
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION SUMMARY ==="))
        self.stdout.write(f"Total orphaned variants: {total_orphans}")
        self.stdout.write(f"Variants {'would be' if dry_run else ''} linked to existing parents: {linked_variants}")
        self.stdout.write(f"Variants still without parents: {still_orphaned}")
        self.stdout.write(f"Errors encountered: {errors}")
        
        if errors > 0:
            self.stdout.write(self.style.ERROR("\n=== ERROR DETAILS ==="))
            for error in error_details:
                self.stdout.write(self.style.ERROR(error))
        
        if total_orphans > 0:
            success_rate = (linked_variants / total_orphans) * 100
            self.stdout.write(f"Success rate: {success_rate:.2f}%")
        
        # Next steps
        self.stdout.write(self.style.SUCCESS("\n=== NEXT STEPS ==="))
        self.stdout.write("1. For variants still without parents, consider creating placeholder parents")
        self.stdout.write("2. Run validation checks to ensure proper parent-child relationships")
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION COMPLETE ===\n"))
    
    def _process_variants(self, variants, dry_run, linked_variants, still_orphaned, errors, error_details):
        """Process variants and link them to existing parents with matching legacy_id values"""
        for variant in variants:
            try:
                # Find parent with matching legacy_id
                matching_parent = ParentProduct.objects.filter(legacy_id=variant.legacy_familie).first()
                
                if matching_parent:
                    # Link variant to existing parent
                    if not dry_run:
                        variant.parent = matching_parent
                        variant.save()
                    
                    self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Linked variant {variant.sku} to existing parent {matching_parent.sku}")
                    linked_variants += 1
                else:
                    self.stdout.write(self.style.WARNING(f"{'[DRY RUN] ' if dry_run else ''}No matching parent found for variant {variant.sku} with Familie {variant.legacy_familie}"))
                    still_orphaned += 1
            except Exception as e:
                errors += 1
                error_msg = f"Error processing variant {variant.sku}: {str(e)}"
                error_details.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
        
        return linked_variants, still_orphaned, errors 