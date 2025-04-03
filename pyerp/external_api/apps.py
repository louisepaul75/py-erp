from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import importlib
import sys
import os


class ExternalApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pyerp.external_api"
    verbose_name = _("External API Integrations")

    def ready(self):
        # Debug output
        print(f"ExternalApiConfig.ready() called - app_name: {self.name}")
        
        # Explicitly import submodules to ensure they're loaded
        try:
            images_cms_path = os.path.join(os.path.dirname(__file__), 'images_cms')
            if os.path.exists(images_cms_path):
                print(f"images_cms directory exists at {images_cms_path}")
                
                # Import the management command directly to ensure it's registered
                management_cmd_path = os.path.join(images_cms_path, 'management', 'commands', 'sync_product_images.py')
                if os.path.exists(management_cmd_path):
                    print(f"sync_product_images.py command exists at {management_cmd_path}")
                else:
                    print(f"Command file NOT found at {management_cmd_path}")
        except Exception as e:
            print(f"Error during ExternalApiConfig.ready(): {e}")

        # Optional: Import signals or perform other setup here
        pass 