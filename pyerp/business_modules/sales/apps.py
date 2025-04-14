from django.apps import AppConfig


class SalesConfig(AppConfig):
    """
    Configuration for the Sales application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.business_modules.sales"
    verbose_name = "Sales"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
