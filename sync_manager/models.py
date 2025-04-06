from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid
import json

class SyncWorkflow(models.Model):
    """Represents a type of data synchronization workflow."""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Workflow Name"))
    slug = models.SlugField(max_length=110, unique=True, blank=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    # Link to the external connection name defined in external_connections.json
    external_connection_name = models.CharField(
        max_length=50,
        blank=True, # Allow blank for now, maybe make required later
        db_index=True,
        verbose_name=_("External Connection Name"),
        help_text=_("The key from external_connections.json this workflow belongs to (e.g., 'legacy_erp').")
    )
    
    # Base command template. Parameters like {debug} or {force_update} can be added dynamically.
    command_template = models.CharField(max_length=500, verbose_name=_("Command Template"), default='')
    
    # Define expected parameters and their types (e.g., {"debug": "boolean", "force_update": "boolean"})
    parameters = models.JSONField(default=dict, blank=True, verbose_name=_("Parameters Definition"))
    
    # Store environment variables required for this workflow
    environment_variables = models.JSONField(default=dict, blank=True, verbose_name=_("Environment Variables"))

    # Store default parameters for triggering the workflow
    default_parameters = models.JSONField(
        default=dict, 
        blank=True, 
        verbose_name=_("Default Parameters"),
        help_text=_("Default parameters to use when triggering this workflow.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Sync Workflow")
        verbose_name_plural = _("Sync Workflows")
        ordering = ['external_connection_name', 'name'] # Order by connection then name


class SyncJob(models.Model):
    """Represents a single execution instance of a SyncWorkflow."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        STARTED = 'STARTED', _('Started')
        SUCCESS = 'SUCCESS', _('Success')
        FAILURE = 'FAILURE', _('Failure')
        RETRY = 'RETRY', _('Retry') # Celery specific

    workflow = models.ForeignKey(
        SyncWorkflow, on_delete=models.CASCADE, related_name='jobs',
        verbose_name=_("Workflow")
    )
    task_id = models.CharField(
        _("Celery Task ID"), max_length=255, null=True, blank=True, db_index=True,
        help_text=_("The ID of the background task processing this job.")
    )
    status = models.CharField(
        _("Status"), max_length=10, choices=Status.choices, 
        default=Status.PENDING, db_index=True
    )
    parameters = models.JSONField(
        _("Parameters"), default=dict, blank=True,
        help_text=_("Parameters used for this specific job run.")
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(_("Started At"), null=True, blank=True)
    completed_at = models.DateTimeField(_("Completed At"), null=True, blank=True)
    log_output = models.TextField(_("Log Output"), blank=True, default='')

    def __str__(self):
        job_id_display = self.task_id or str(getattr(self, 'id', 'N/A'))
        return f"{self.workflow.name} - Job {job_id_display} ({self.status})"

    class Meta:
        verbose_name = _("Sync Job")
        verbose_name_plural = _("Sync Jobs")
        ordering = ['-created_at']
