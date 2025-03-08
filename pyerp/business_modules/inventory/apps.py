from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Configuration for the Inventory application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.business_modules.inventory"
    verbose_name = "Inventory"
