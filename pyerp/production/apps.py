from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """
    Configuration for the Production application.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # noqa: F841
  # noqa: F841
    name = 'pyerp.production'  # noqa: F841
    verbose_name = 'Production'  # noqa: F841
  # noqa: F841
