"""
Models for the monitoring app.
"""

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class HealthCheckResult(models.Model):
    """
    Stores the results of system health checks.
    """

    STATUS_SUCCESS = "success"
    STATUS_WARNING = "warning"
    STATUS_ERROR = "error"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, _("Success")),
        (STATUS_WARNING, _("Warning")),
        (STATUS_ERROR, _("Error")),
    ]

    COMPONENT_DATABASE = "database"
    COMPONENT_LEGACY_ERP = "legacy_erp"
    COMPONENT_PICTURES_API = "pictures_api"
    COMPONENT_DATABASE_VALIDATION = "database_validation"

    COMPONENT_CHOICES = [
        (COMPONENT_DATABASE, _("Database")),
        (COMPONENT_LEGACY_ERP, _("Legacy ERP")),
        (COMPONENT_PICTURES_API, _("Pictures API")),
        (COMPONENT_DATABASE_VALIDATION, _("Database Validation")),
    ]

    component = models.CharField(
        _("Component"),
        max_length=50,
        choices=COMPONENT_CHOICES,
        help_text=_("System component being checked"),
    )

    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        help_text=_("Health check result status"),
    )

    timestamp = models.DateTimeField(
        _("Timestamp"),
        default=timezone.now,
        help_text=_("When the health check was performed"),
    )

    details = models.TextField(
        _("Details"),
        blank=True,
        null=True,
        help_text=_("Additional details about the health check result"),
    )

    response_time = models.FloatField(
        _("Response Time (ms)"),
        null=True,
        blank=True,
        help_text=_("Time taken to complete the health check in milliseconds"),
    )

    class Meta:
        verbose_name = _("Health Check Result")
        verbose_name_plural = _("Health Check Results")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["component", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.get_component_display()} - {self.get_status_display()} - {self.timestamp}"

    @classmethod
    def get_latest_result(cls, component):
        """
        Get the latest health check result for a specific component.

        Args:
            component: The component to get results for

        Returns:
            HealthCheckResult: The most recent result, or None if no results exist  # noqa: E501
        """
        try:
            return cls.objects.filter(component=component).latest("timestamp")
        except cls.DoesNotExist:
            return None
