from django.core.management.base import BaseCommand
from pyerp.products.models import VariantProduct, ParentProduct
from django.db import transaction


class Command(BaseCommand):
    help = 'Links variants without parents to existing parents with matching legacy_id values'  # noqa: E501

    def add_arguments(self, parser):

        parser.add_argument(
            '--dry-run',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Simulate the operation without making changes',  # noqa: F841
        )
        parser.add_argument(
            '--force',  # noqa: E128
            action='store_true',  # noqa: F841
            help='Skip confirmation prompt',  # noqa: F841
  # noqa: F841
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS("\n=== LINKING VARIANTS TO EXISTING PARENTS ===\n"))  # noqa: E501

        # Get variants without parents
        variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)  # noqa: E501
        total_orphans = variants_without_parent.count()

        self.stdout.write(f"Found {total_orphans} variants without parent products.")  # noqa: E501

        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned variants found. Nothing to do."))  # noqa: E501
            return

        # Ask for confirmation if not forced
        if not force and not dry_run:
            self.stdout.write("\nThis command will link variants without parents to existing parent products with matching legacy_id values.")  # noqa: E501

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
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No actual changes will be made\n"))  # noqa: E501

        # Use transaction to ensure atomicity for dry run
        if dry_run:
            with transaction.atomic():
                sid = transaction.savepoint()
                linked_variants, still_orphaned, errors = self._process_variants(variants_without_parent, dry_run, linked_variants, still_orphaned, errors, error_details)  # noqa: E501
                transaction.savepoint_rollback(sid)
                self.stdout.write(self.style.WARNING("\n[DRY RUN] All changes have been rolled back\n"))  # noqa: E501
        else:
            # Process each variant individually without a transaction
            linked_variants, still_orphaned, errors = self._process_variants(variants_without_parent, dry_run, linked_variants, still_orphaned, errors, error_details)  # noqa: E501

        # Summary
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION SUMMARY ==="))
        self.stdout.write(f"Total orphaned variants: {total_orphans}")
        self.stdout.write(f"Variants {'would be' if dry_run else ''} linked to existing parents: {linked_variants}")  # noqa: E501
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
        self.stdout.write("1. For variants still without parents, consider creating placeholder parents")  # noqa: E501
        self.stdout.write("2. Run validation checks to ensure proper parent-child relationships")  # noqa: E501
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION COMPLETE ===\n"))

    def _process_variants(self, variants, dry_run, linked_variants, still_orphaned, errors, error_details):  # noqa: E501
        """Process variants and link them to existing parents with matching legacy_id values"""  # noqa: E501
        for variant in variants:
            try:
                # Find parent with matching legacy_id
                matching_parent = ParentProduct.objects.filter(legacy_id=variant.legacy_familie).first()  # noqa: E501

                if matching_parent:
                    # Link variant to existing parent
                    if not dry_run:
                        variant.parent = matching_parent
                        variant.save()

                    self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Linked variant {variant.sku} to existing parent {matching_parent.sku}")  # noqa: E501
                    linked_variants += 1
                else:
                    self.stdout.write(self.style.WARNING(f"{'[DRY RUN] ' if dry_run else ''}No matching parent found for variant {variant.sku} with Familie {variant.legacy_familie}"))  # noqa: E501
                    still_orphaned += 1
            except Exception as e:
                errors += 1
                error_msg = f"Error processing variant {variant.sku}: {str(e)}"
                error_details.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

        return linked_variants, still_orphaned, errors
