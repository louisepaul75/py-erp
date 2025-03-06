"""
App configuration for the products app.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    """
    Configuration for the products app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.products"
    verbose_name = _("Products")

    def ready(self):
        """
        Initialize app when Django starts.
        """
        try:
            import pyerp.products.signals
        except ImportError:
            pass
