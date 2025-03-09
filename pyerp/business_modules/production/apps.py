from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """
    Configuration for the Production application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.business_modules.production"
    verbose_name = "Production"
