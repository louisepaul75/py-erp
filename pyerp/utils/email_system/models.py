from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailLog(models.Model):
    """
    Model to store email activity logs.
    """
    # Email status choices
    STATUS_QUEUED = 'queued'
    STATUS_SENT = 'sent'
    STATUS_DELIVERED = 'delivered'
    STATUS_OPENED = 'opened'
    STATUS_CLICKED = 'clicked'
    STATUS_BOUNCED = 'bounced'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLAINED = 'complained'
    STATUS_UNSUBSCRIBED = 'unsubscribed'
    STATUS_FAILED = 'failed'
    
    STATUS_CHOICES = [
        (STATUS_QUEUED, _('Queued')),
        (STATUS_SENT, _('Sent')),
        (STATUS_DELIVERED, _('Delivered')),
        (STATUS_OPENED, _('Opened')),
        (STATUS_CLICKED, _('Clicked')),
        (STATUS_BOUNCED, _('Bounced')),
        (STATUS_REJECTED, _('Rejected')),
        (STATUS_COMPLAINED, _('Complained')),
        (STATUS_UNSUBSCRIBED, _('Unsubscribed')),
        (STATUS_FAILED, _('Failed')),
    ]
    
    # Basic email information
    message_id = models.CharField(
        _('Message ID'), 
        max_length=255, 
        unique=True,
        help_text=_('Unique identifier for the email message')
    )
    subject = models.CharField(
        _('Subject'), 
        max_length=255,
        help_text=_('Email subject')
    )
    from_email = models.EmailField(
        _('From Email'),
        help_text=_('Sender email address')
    )
    to_email = models.TextField(
        _('To Email'),
        help_text=_('Recipient email address(es), comma separated')
    )
    cc_email = models.TextField(
        _('CC Email'),
        blank=True,
        null=True,
        help_text=_('CC email address(es), comma separated')
    )
    bcc_email = models.TextField(
        _('BCC Email'),
        blank=True,
        null=True,
        help_text=_('BCC email address(es), comma separated')
    )
    
    # Content information
    body_text = models.TextField(
        _('Body Text'),
        blank=True,
        null=True,
        help_text=_('Plain text content of the email')
    )
    body_html = models.TextField(
        _('Body HTML'),
        blank=True,
        null=True,
        help_text=_('HTML content of the email')
    )
    
    # Status information
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_QUEUED,
        help_text=_('Current status of the email')
    )
    error_message = models.TextField(
        _('Error Message'),
        blank=True,
        null=True,
        help_text=_('Error message if the email failed to send')
    )
    
    # ESP information
    esp = models.CharField(
        _('ESP'),
        max_length=50,
        blank=True,
        null=True,
        help_text=_('Email Service Provider used to send this email')
    )
    esp_message_id = models.CharField(
        _('ESP Message ID'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Message ID assigned by the ESP')
    )
    
    # Tracking information
    opens = models.IntegerField(
        _('Opens'),
        default=0,
        help_text=_('Number of times the email was opened')
    )
    clicks = models.IntegerField(
        _('Clicks'),
        default=0,
        help_text=_('Number of times links in the email were clicked')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True,
        help_text=_('When the email was created')
    )
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True,
        help_text=_('When the email status was last updated')
    )
    sent_at = models.DateTimeField(
        _('Sent At'),
        blank=True,
        null=True,
        help_text=_('When the email was sent')
    )
    delivered_at = models.DateTimeField(
        _('Delivered At'),
        blank=True,
        null=True,
        help_text=_('When the email was delivered')
    )
    
    class Meta:
        verbose_name = _('Email Log')
        verbose_name_plural = _('Email Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['from_email']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.to_email} ({self.status})"


class EmailEvent(models.Model):
    """
    Model to store detailed email events (e.g., opens, clicks, bounces).
    """
    email_log = models.ForeignKey(
        EmailLog,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name=_('Email Log'),
        help_text=_('The email this event is related to')
    )
    event_type = models.CharField(
        _('Event Type'),
        max_length=50,
        help_text=_('Type of email event (e.g., open, click, bounce)')
    )
    timestamp = models.DateTimeField(
        _('Timestamp'),
        auto_now_add=True,
        help_text=_('When the event occurred')
    )
    data = models.JSONField(
        _('Event Data'),
        blank=True,
        null=True,
        help_text=_('Additional data related to the event')
    )
    user_agent = models.TextField(
        _('User Agent'),
        blank=True,
        null=True,
        help_text=_('User agent of the client that triggered the event')
    )
    ip_address = models.GenericIPAddressField(
        _('IP Address'),
        blank=True,
        null=True,
        help_text=_('IP address of the client that triggered the event')
    )
    
    class Meta:
        verbose_name = _('Email Event')
        verbose_name_plural = _('Email Events')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.email_log.subject} ({self.timestamp})" 