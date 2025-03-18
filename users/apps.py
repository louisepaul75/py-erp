from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = "User Management"

    def ready(self):
        """
        Connect signal handlers when the app is ready.
        This is needed for audit logging and other event-based functionality.
        """
        import users.signals  # noqa
