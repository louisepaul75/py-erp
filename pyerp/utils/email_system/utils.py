import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from pyerp.utils.onepassword_connect import get_email_password

logger = logging.getLogger('anymail')


def _ensure_password_from_1password():
    """
    Ensure that the email password is retrieved from 1Password if needed.
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
                return True
            else:
                logger.error("Failed to retrieve email password from 1Password")
                return False
    
    return True  # No need to retrieve password or already set


def send_test_email(to_email, subject=None, context=None):
    """
    Send a test email to verify email configuration.
    
    Args:
        to_email (str): Recipient email address
        subject (str, optional): Email subject. Defaults to "Test Email from pyERP".
        context (dict, optional): Context for the email template. Defaults to None.
    
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Ensure password is retrieved from 1Password if needed
    if not _ensure_password_from_1password():
        logger.error("Cannot send test email: Failed to retrieve password from 1Password")
        return False
    
    if subject is None:
        subject = "Test Email from pyERP"
    
    if context is None:
        context = {
            'title': 'Email Configuration Test',
            'message': 'This is a test email to verify that your email configuration is working correctly.',
            'system_name': 'pyERP',
            'support_email': settings.DEFAULT_FROM_EMAIL,
        }
    
    try:
        # Log current email settings
        logger.info(f"Sending test email with settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, "
                   f"USER={settings.EMAIL_HOST_USER}, SSL={settings.EMAIL_USE_SSL}, TLS={settings.EMAIL_USE_TLS}")
        
        # Render HTML content
        html_content = render_to_string('email_system/test_email.html', context)
        # Create plain text content
        text_content = strip_tags(html_content)
        
        # Create email message
        from_email = settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        
        # Send email
        msg.send()
        
        logger.info(f"Test email sent to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending test email: {str(e)}")
        # Log more detailed error information
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def send_html_email(to_email, subject, html_content, from_email=None, cc=None, bcc=None, attachments=None):
    """
    Send an HTML email with plain text alternative.
    
    Args:
        to_email (str or list): Recipient email address(es)
        subject (str): Email subject
        html_content (str): HTML content of the email
        from_email (str, optional): Sender email address. Defaults to DEFAULT_FROM_EMAIL.
        cc (list, optional): CC recipients. Defaults to None.
        bcc (list, optional): BCC recipients. Defaults to None.
        attachments (list, optional): List of attachments. Each attachment should be a tuple of 
                                     (filename, content, mimetype). Defaults to None.
    
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    # Ensure password is retrieved from 1Password if needed
    if not _ensure_password_from_1password():
        logger.error("Cannot send email: Failed to retrieve password from 1Password")
        return False
    
    try:
        # Convert to_email to list if it's a string
        if isinstance(to_email, str):
            to_email = [to_email]
        
        # Set default from_email if not provided
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL
        
        # Create plain text content
        text_content = strip_tags(html_content)
        
        # Create email message
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email, cc=cc, bcc=bcc)
        msg.attach_alternative(html_content, "text/html")
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
        
        # Send email
        msg.send()
        
        logger.info(f"Email '{subject}' sent to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending email '{subject}': {str(e)}")
        return False 