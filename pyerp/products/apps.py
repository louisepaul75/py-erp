"""
App configuration for the products app.
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _  # noqa: F401


class ProductsConfig(AppConfig):
    """
    Configuration for the products app.
    """
    default_auto_field = 'django.db.models.BigAutoField'  # noqa: F841
    name = 'pyerp.products'  # noqa: F841
    verbose_name = _('Products')  # noqa: F841

    def ready(self):
        """
        Initialize app when Django starts.
        """
        try:
            import pyerp.products.signals  # noqa
        except ImportError:
            pass
