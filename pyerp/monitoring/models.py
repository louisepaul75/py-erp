"""
Models for the monitoring app.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _  # noqa: F401
from django.utils import timezone


class HealthCheckResult(models.Model):
    """
    Stores the results of system health checks.
    """

    STATUS_SUCCESS = 'success'
    STATUS_WARNING = 'warning'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, _('Success')),  # noqa: E128
        (STATUS_WARNING, _('Warning')),
        (STATUS_ERROR, _('Error')),
    ]

    COMPONENT_DATABASE = 'database'
    COMPONENT_LEGACY_ERP = 'legacy_erp'
    COMPONENT_PICTURES_API = 'pictures_api'
    COMPONENT_DATABASE_VALIDATION = 'database_validation'

    COMPONENT_CHOICES = [
        (COMPONENT_DATABASE, _('Database')),  # noqa: E128
        (COMPONENT_LEGACY_ERP, _('Legacy ERP')),
        (COMPONENT_PICTURES_API, _('Pictures API')),
        (COMPONENT_DATABASE_VALIDATION, _('Database Validation')),
    ]

    component = models.CharField(
        _('Component'),  # noqa: E128
        max_length=50,  # noqa: F841
        choices=COMPONENT_CHOICES,  # noqa: F841
        help_text=_('System component being checked')  # noqa: F841
    )

    status = models.CharField(  # noqa: F841
        _('Status'),  # noqa: E128
        max_length=20,  # noqa: F841
  # noqa: F841
        choices=STATUS_CHOICES,  # noqa: F841
  # noqa: F841
        help_text=_('Health check result status')  # noqa: F841
    )

    timestamp = models.DateTimeField(  # noqa: F841
        _('Timestamp'),  # noqa: E128
        default=timezone.now,  # noqa: F841
  # noqa: F841
        help_text=_('When the health check was performed')  # noqa: F841
    )

    details = models.TextField(  # noqa: F841
        _('Details'),  # noqa: E128
        blank=True,  # noqa: F841
        null=True,  # noqa: F841
        help_text=_('Additional details about the health check result')  # noqa: F841
    )

    response_time = models.FloatField(  # noqa: F841
  # noqa: F841
        _('Response Time (ms)'),
        null=True,  # noqa: F841
  # noqa: F841
        blank=True,  # noqa: F841
  # noqa: F841
        help_text=_('Time taken to complete the health check in milliseconds')  # noqa: F841
  # noqa: F841
    )

    class Meta:

        verbose_name = _('Health Check Result')  # noqa: F841
        verbose_name_plural = _('Health Check Results')  # noqa: F841
  # noqa: F841
        ordering = ['-timestamp']  # noqa: F841
  # noqa: F841
        indexes = [  # noqa: F841
  # noqa: F841
            models.Index(fields=['component', '-timestamp']),
  # noqa: F841
        ]

    def __str__(self):

        return f"{self.get_component_display()} - {self.get_status_display()} - {self.timestamp}"  # noqa: E501

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
            return cls.objects.filter(component=component).latest('timestamp')
  # noqa: F841
        except cls.DoesNotExist:
            return None
