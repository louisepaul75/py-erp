from django.core.management.base import BaseCommand
from pyerp.products.models import VariantProduct, ParentProduct
from django.db import transaction


class Command(BaseCommand):
    help = 'Creates placeholder parent products for variants without parents'  # noqa: F841

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
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(self.style.SUCCESS("\n=== CREATING PLACEHOLDER PARENT PRODUCTS ===\n"))  # noqa: E501

 # Get variants without parents
        variants_without_parent = VariantProduct.objects.filter(parent__isnull=True)  # noqa: E501
        total_orphans = variants_without_parent.count()

        self.stdout.write(f"Found {total_orphans} variants without parent products.")  # noqa: E501

        if total_orphans == 0:
            self.stdout.write(self.style.SUCCESS("No orphaned variants found. Nothing to do."))  # noqa: E501
            return

 # Ask for confirmation if not forced
        if not force and not dry_run:
            self.stdout.write("\nThis command will create placeholder parent products for orphaned variants.")  # noqa: E501
            self.stdout.write("These placeholder parents will use data from their variants with a 'PLACEHOLDER' prefix.")  # noqa: E501

            confirm = input("Do you want to proceed? (y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING("Operation cancelled."))
                return

 # Create parents and update relationships
        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN] No actual changes will be made\n"))  # noqa: E501

 # Track results
        created_parents = 0
        updated_relationships = 0
        errors = 0
        error_details = []

 # Use transaction to ensure atomicity - only for dry run
        if dry_run:
            with transaction.atomic():
                sid = transaction.savepoint()

                for variant in variants_without_parent:
                    try:
                        parent = ParentProduct(
                            sku=f"PLACEHOLDER-{variant.sku}",  # noqa: E128
                            name=f"PLACEHOLDER - {variant.name}" if variant.name else f"PLACEHOLDER Parent for {variant.sku}",  # noqa: E501
                            is_active=variant.is_active,  # noqa: F841
                            legacy_id=variant.legacy_familie,  # noqa: F841
                            is_placeholder=True,  # noqa: F841
                            base_sku=variant.base_sku if hasattr(variant, 'base_sku') and variant.base_sku else variant.sku  # noqa: E501
                        )

                        if not dry_run:
                            parent.save()
                        created_parents += 1

 # Update variant to link to this parent
                        if not dry_run:
                            variant.parent = parent
                            variant.save()
                        updated_relationships += 1

                        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Created placeholder parent {parent.sku} for variant {variant.sku}")  # noqa: E501
                    except Exception as e:
                        errors += 1
                        error_details.append(f"Error processing variant {variant.sku}: {str(e)}")  # noqa: E501
                        self.stdout.write(self.style.ERROR(f"Error processing variant {variant.sku}: {str(e)}"))  # noqa: E501

 # If dry run, rollback all changes
                if dry_run:
                    transaction.savepoint_rollback(sid)
                    self.stdout.write(self.style.WARNING("\n[DRY RUN] All changes have been rolled back\n"))  # noqa: E501
        else:
            for variant in variants_without_parent:
                try:
                    parent = ParentProduct(
                        sku=f"PLACEHOLDER-{variant.sku}",  # noqa: E128
                        name=f"PLACEHOLDER - {variant.name}" if variant.name else f"PLACEHOLDER Parent for {variant.sku}",  # noqa: E501
                        is_active=variant.is_active,  # noqa: F841
                        legacy_id=variant.legacy_familie,  # noqa: F841
                        is_placeholder=True,  # noqa: F841
                        base_sku=variant.base_sku if hasattr(variant, 'base_sku') and variant.base_sku else variant.sku  # noqa: E501
                    )

                    parent.save()
                    created_parents += 1

 # Update variant to link to this parent
                    variant.parent = parent
                    variant.save()
                    updated_relationships += 1

                    self.stdout.write(f"Created placeholder parent {parent.sku} for variant {variant.sku}")  # noqa: E501
                except Exception as e:
                    errors += 1
                    error_details.append(f"Error processing variant {variant.sku}: {str(e)}")  # noqa: E501
                    self.stdout.write(self.style.ERROR(f"Error processing variant {variant.sku}: {str(e)}"))  # noqa: E501

 # Summary
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION SUMMARY ==="))
        self.stdout.write(f"Total orphaned variants: {total_orphans}")
        self.stdout.write(f"Placeholder parents {'would be' if dry_run else ''} created: {created_parents}")  # noqa: E501
        self.stdout.write(f"Variant relationships {'would be' if dry_run else ''} updated: {updated_relationships}")  # noqa: E501
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
        self.stdout.write("1. Review the created placeholder parents in the admin interface")  # noqa: E501
        self.stdout.write("2. Add additional data to the placeholder parents as needed")  # noqa: E501
        self.stdout.write("3. Run validation checks to ensure proper parent-child relationships")  # noqa: E501
        self.stdout.write(self.style.SUCCESS("\n=== OPERATION COMPLETE ===\n"))
