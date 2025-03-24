from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BusinessConfig(AppConfig):
    """Business app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pyerp.business_modules.business'
    verbose_name = _('Business Management')
    
    def ready(self):
        """Initialize app when ready."""
        # Import any signals or perform initialization
        pass
