from django.core.management.base import BaseCommand
from pyerp.sync.pipeline import PipelineFactory
from pyerp.sync.models import SyncMapping
from pyerp.utils.constants import SyncStatus
from pyerp.utils.logging import get_logger

logger = get_logger(__name__)

class Command(BaseCommand):
    help = "Sync currencies and exchange rates using pipeline from Frankfurter API" 
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force full sync even if incremental sync is configured",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        debug = options.get("debug", False)
        force = options.get("force", False)

        if debug:
            logger.info("Debug mode enabled")

        self.stdout.write("🚀 Starting Frankfurter sync via pipeline...")

        # Sync currencies
        try:
            currency_mapping = SyncMapping.objects.get(entity_type="currency list", active=True)
            currency_pipeline = PipelineFactory.create_pipeline(currency_mapping)
            log = currency_pipeline.run(incremental=not force, batch_size=100)

            if log.status == SyncStatus.COMPLETED:
                self.stdout.write(self.style.SUCCESS("✅ Currencies synced via pipeline"))
            elif log.status == SyncStatus.COMPLETED_WITH_ERRORS:
                self.stdout.write(self.style.WARNING(f"⚠️ Sync completed with errors. Failed records: {log.records_failed}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sync failed. Status: {log.status}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to sync currencies: {e}"))

        # Sync exchange rates
        try:
            rate_mapping = SyncMapping.objects.get(entity_type="exchange_rate", active=True)
            rate_pipeline = PipelineFactory.create_pipeline(rate_mapping)
            log = rate_pipeline.run(incremental=not force, batch_size=100)
            if log.status == SyncStatus.COMPLETED:
                self.stdout.write(self.style.SUCCESS("✅ Currencies exchange rate synced via pipeline"))
            elif log.status == SyncStatus.COMPLETED_WITH_ERRORS:
                self.stdout.write(self.style.WARNING(f"⚠️ Sync completed with errors. Failed records: {log.records_failed}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sync failed. Status: {log.status}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to sync exchange rates: {e}"))
        
        # Sync historical rates
        try:
            rate_mapping = SyncMapping.objects.get(entity_type="historical_rate", active=True)
            rate_pipeline = PipelineFactory.create_pipeline(rate_mapping)
            log = rate_pipeline.run(incremental=not force, batch_size=100)
            if log.status == SyncStatus.COMPLETED:
                self.stdout.write(self.style.SUCCESS("✅ Currencies historical rate synced via pipeline"))
            elif log.status == SyncStatus.COMPLETED_WITH_ERRORS:
                self.stdout.write(self.style.WARNING(f"⚠️ Sync completed with errors. Failed records: {log.records_failed}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Sync failed. Status: {log.status}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to sync historical rates: {e}"))

        self.stdout.write(self.style.SUCCESS("🎯 Frankfurter sync completed."))
