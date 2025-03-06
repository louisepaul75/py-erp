from django.apps import AppConfig


class LegacySyncConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # noqa: F841
  # noqa: F841
    name = 'pyerp.legacy_sync'  # noqa: F841
    verbose_name = 'Legacy ERP Synchronization'  # noqa: F841
  # noqa: F841

    def ready(self):
        """
        Import signals when the app is ready.
        """
        import pyerp.legacy_sync.signals  # noqa
