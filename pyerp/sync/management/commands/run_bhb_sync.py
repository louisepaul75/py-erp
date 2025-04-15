"""
Management command to trigger the BuchhaltungsButler Posting Accounts to Supplier sync task.
"""

from django.core.management.base import BaseCommand, CommandError
from pyerp.sync.tasks import sync_bhb_posting_accounts_to_supplier

class Command(BaseCommand):
    help = (
        'Triggers the Celery task to sync BuchhaltungsButler posting accounts '
        'to pyERP Supplier models.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--foreground',
            action='store_true',
            help='Run the task synchronously in the foreground instead of using Celery.',
        )

    def handle(self, *args, **options):
        run_in_foreground = options['foreground']

        if run_in_foreground:
            self.stdout.write(
                self.style.WARNING(
                    "Running sync task synchronously in the foreground..."
                )
            )
            try:
                result = sync_bhb_posting_accounts_to_supplier() 
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sync task finished synchronously. Status: {result.get('status')}"
                    )
                )
                # Optionally print more details from result dict
                self.stdout.write(f"Details: {result}")
            except Exception as e:
                raise CommandError(f"Synchronous task execution failed: {e}")
        else:
            self.stdout.write(
                self.style.NOTICE(
                    "Dispatching sync task to Celery worker..."
                )
            )
            try:
                task_result = sync_bhb_posting_accounts_to_supplier.delay()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully dispatched task. Task ID: {task_result.id}"
                    )
                )
                self.stdout.write(
                    self.style.NOTICE(
                        "Monitor your Celery worker logs for task progress and results."
                    )
                )
            except Exception as e:
                 # Catch potential errors during task dispatch (e.g., broker connection issues)
                raise CommandError(f"Failed to dispatch Celery task: {e}") 