import uuid
import logging
from datetime import datetime
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils import timezone
from django.conf import settings
# from anymail.backends.smtp import EmailBackend as AnymailSMTPBackend
from .models import EmailLog
from pyerp.utils.onepassword_connect import get_email_password

logger = logging.getLogger('anymail')


class LoggingEmailBackend(SMTPBackend):
    """
    A wrapper around Django's SMTP email backend that logs emails to the database.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the backend and retrieve the password from 1Password if needed.
        """
        # Check if 1Password integration is enabled
        use_1password = getattr(settings, 'EMAIL_USE_1PASSWORD', False)
        if use_1password and not settings.EMAIL_HOST_PASSWORD:
            # Get the item name and username
            item_name = getattr(settings, 'EMAIL_1PASSWORD_ITEM_NAME', '')
            username = getattr(settings, 'EMAIL_HOST_USER', '')
            
            if username:
                # Retrieve the password
                password = get_email_password(
                    email_username=username,
                    item_name=item_name or None
                )
                
                if password:
                    # Update the password in settings
                    settings.EMAIL_HOST_PASSWORD = password
                    logger.info("Retrieved email password from 1Password")
                else:
                    logger.error("Failed to retrieve email password from 1Password")
        
        super().__init__(*args, **kwargs)
    
    def send_messages(self, email_messages):
        """
        Send email messages and log them to the database.
        """
        if not email_messages:
            return 0
        
        # Log each message before sending
        for message in email_messages:
            self._log_message(message)
        
        # Send messages using the parent class
        sent_count = super().send_messages(email_messages)
        
        # Update status for sent messages
        for i, message in enumerate(email_messages):
            if hasattr(message, '_email_log_id') and i < sent_count:
                try:
                    email_log = EmailLog.objects.get(id=message._email_log_id)
                    email_log.status = EmailLog.STATUS_SENT
                    email_log.sent_at = timezone.now()
                    email_log.save(update_fields=['status', 'sent_at'])
                except EmailLog.DoesNotExist:
                    logger.error(f"Could not find EmailLog with ID {message._email_log_id}")
        
        return sent_count
    
    def _log_message(self, message):
        """
        Log an email message to the database.
        """
        # Generate a unique message ID if not present
        if not hasattr(message, 'message_id') or not message.message_id:
            message.message_id = f"<{uuid.uuid4()}@pyerp.local>"
        
        # Extract recipients
        to_emails = ', '.join(message.to) if hasattr(message, 'to') else ''
        cc_emails = ', '.join(message.cc) if hasattr(message, 'cc') else ''
        bcc_emails = ', '.join(message.bcc) if hasattr(message, 'bcc') else ''
        
        # Extract content
        if hasattr(message, 'body'):
            body_text = message.body
        else:
            body_text = ''
        
        body_html = None
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    body_html = content
                    break
        
        # Create log entry
        try:
            email_log = EmailLog.objects.create(
                message_id=message.message_id,
                subject=message.subject,
                from_email=message.from_email,
                to_email=to_emails,
                cc_email=cc_emails,
                bcc_email=bcc_emails,
                body_text=body_text,
                body_html=body_html,
                status=EmailLog.STATUS_QUEUED,
                esp='smtp',  # Default to SMTP
            )
            
            # Store the log ID on the message for later reference
            message._email_log_id = email_log.id
            
            logger.info(f"Logged email: {email_log.subject} to {email_log.to_email}")
            
        except Exception as e:
            logger.error(f"Error logging email: {str(e)}")


class LoggingAnymailBackend(SMTPBackend):
    """
    A wrapper around Django's SMTP email backend that logs emails to the database.
    This is a simplified version that doesn't use Anymail's backend directly.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the backend and retrieve the password from 1Password if needed.
        """
        # Check if 1Password integration is enabled
        use_1password = getattr(settings, 'EMAIL_USE_1PASSWORD', False)
        if use_1password and not settings.EMAIL_HOST_PASSWORD:
            # Get the item name and username
            item_name = getattr(settings, 'EMAIL_1PASSWORD_ITEM_NAME', '')
            username = getattr(settings, 'EMAIL_HOST_USER', '')
            
            if username:
                # Retrieve the password
                password = get_email_password(
                    email_username=username,
                    item_name=item_name or None
                )
                
                if password:
                    # Update the password in settings
                    settings.EMAIL_HOST_PASSWORD = password
                    logger.info("Retrieved email password from 1Password")
                else:
                    logger.error("Failed to retrieve email password from 1Password")
        
        super().__init__(*args, **kwargs)
    
    def send_messages(self, email_messages):
        """
        Send email messages and log them to the database.
        """
        if not email_messages:
            return 0
        
        # Log each message before sending
        for message in email_messages:
            self._log_message(message)
        
        # Send messages using the parent class
        sent_count = super().send_messages(email_messages)
        
        # Update status for sent messages
        for i, message in enumerate(email_messages):
            if hasattr(message, '_email_log_id') and i < sent_count:
                try:
                    email_log = EmailLog.objects.get(id=message._email_log_id)
                    email_log.status = EmailLog.STATUS_SENT
                    email_log.sent_at = timezone.now()
                    
                    # If ESP message ID is available from Anymail
                    if hasattr(message, 'anymail_status'):
                        if message.anymail_status.message_id:
                            email_log.esp_message_id = message.anymail_status.message_id
                        if message.anymail_status.esp_name:
                            email_log.esp = message.anymail_status.esp_name
                    
                    email_log.save()
                except EmailLog.DoesNotExist:
                    logger.error(f"Could not find EmailLog with ID {message._email_log_id}")
        
        return sent_count
    
    def _log_message(self, message):
        """
        Log an email message to the database.
        """
        # Generate a unique message ID if not present
        if not hasattr(message, 'message_id') or not message.message_id:
            message.message_id = f"<{uuid.uuid4()}@pyerp.local>"
        
        # Extract recipients
        to_emails = ', '.join(message.to) if hasattr(message, 'to') else ''
        cc_emails = ', '.join(message.cc) if hasattr(message, 'cc') else ''
        bcc_emails = ', '.join(message.bcc) if hasattr(message, 'bcc') else ''
        
        # Extract content
        if hasattr(message, 'body'):
            body_text = message.body
        else:
            body_text = ''
        
        body_html = None
        if hasattr(message, 'alternatives'):
            for content, mimetype in message.alternatives:
                if mimetype == 'text/html':
                    body_html = content
                    break
        
        # Determine ESP
        esp = 'anymail'
        if hasattr(message, 'esp_name'):
            esp = message.esp_name
        
        # Create log entry
        try:
            email_log = EmailLog.objects.create(
                message_id=message.message_id,
                subject=message.subject,
                from_email=message.from_email,
                to_email=to_emails,
                cc_email=cc_emails,
                bcc_email=bcc_emails,
                body_text=body_text,
                body_html=body_html,
                status=EmailLog.STATUS_QUEUED,
                esp=esp,
            )
            
            # Store the log ID on the message for later reference
            message._email_log_id = email_log.id
            
            logger.info(f"Logged email: {email_log.subject} to {email_log.to_email}")
            
        except Exception as e:
            logger.error(f"Error logging email: {str(e)}") 