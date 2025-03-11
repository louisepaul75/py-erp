import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger('anymail')


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