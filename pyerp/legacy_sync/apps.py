from django.apps import AppConfig


class LegacySyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pyerp.legacy_sync'
    verbose_name = 'Legacy ERP Synchronization'

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import pyerp.legacy_sync.signals  # noqa 