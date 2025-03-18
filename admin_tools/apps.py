from django.apps import AppConfig


class AdminToolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "admin_tools"
    verbose_name = "Admin Tools"
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        """
        pass
