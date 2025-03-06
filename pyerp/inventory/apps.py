from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Configuration for the Inventory application.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # noqa: F841
    name = 'pyerp.inventory'  # noqa: F841
    verbose_name = 'Inventory'  # noqa: F841
