import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import EmailLog, EmailEvent

logger = logging.getLogger('anymail')


@csrf_exempt
@require_POST
def anymail_webhook(request):
    """
    Webhook handler for Anymail events.
    This endpoint receives webhook notifications from email service providers.
    """
    try:
        # Parse the webhook data
        payload = json.loads(request.body.decode('utf-8'))
        
        # Log the raw webhook data for debugging
        logger.debug(f"Received webhook: {payload}")
        
        # Process the event based on the ESP
        esp = request.GET.get('esp', 'unknown')
        
        if esp == 'sendgrid':
            return _process_sendgrid_webhook(payload)
        elif esp == 'mailgun':
            return _process_mailgun_webhook(payload)
        elif esp == 'mailjet':
            return _process_mailjet_webhook(payload)
        else:
            # Generic processing for other ESPs
            return _process_generic_webhook(payload, esp)
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def _process_sendgrid_webhook(payload):
    """Process SendGrid webhook events."""
    try:
        for event in payload:
            # Extract data from the event
            event_type = event.get('event')
            message_id = event.get('sg_message_id', '').split('.')[0]
            timestamp = event.get('timestamp')
            
            # Find the corresponding email log
            try:
                email_log = EmailLog.objects.get(esp_message_id=message_id)
            except EmailLog.DoesNotExist:
                logger.warning(f"Could not find email with ESP message ID: {message_id}")
                continue
            
            # Update email status based on event type
            _update_email_status(email_log, event_type)
            
            # Create an event record
            EmailEvent.objects.create(
                email_log=email_log,
                event_type=event_type,
                data=event,
                ip_address=event.get('ip'),
                user_agent=event.get('useragent')
            )
            
        return HttpResponse("OK")
    except Exception as e:
        logger.error(f"Error processing SendGrid webhook: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def _process_mailgun_webhook(payload):
    """Process Mailgun webhook events."""
    try:
        event_data = payload.get('event-data', {})
        event_type = event_data.get('event')
        message_id = event_data.get('message', {}).get('headers', {}).get('message-id')
        
        if not message_id:
            logger.warning("No message ID in Mailgun webhook")
            return HttpResponse("No message ID", status=400)
        
        # Find the corresponding email log
        try:
            email_log = EmailLog.objects.get(message_id=message_id)
        except EmailLog.DoesNotExist:
            logger.warning(f"Could not find email with message ID: {message_id}")
            return HttpResponse("Email not found", status=404)
        
        # Update email status based on event type
        _update_email_status(email_log, event_type)
        
        # Create an event record
        EmailEvent.objects.create(
            email_log=email_log,
            event_type=event_type,
            data=event_data,
            ip_address=event_data.get('ip'),
            user_agent=event_data.get('client-info', {}).get('user-agent')
        )
        
        return HttpResponse("OK")
    except Exception as e:
        logger.error(f"Error processing Mailgun webhook: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def _process_mailjet_webhook(payload):
    """Process Mailjet webhook events."""
    try:
        for event in payload.get('Events', []):
            event_type = event.get('event')
            message_id = event.get('MessageID')
            
            # Find the corresponding email log
            try:
                email_log = EmailLog.objects.get(esp_message_id=str(message_id))
            except EmailLog.DoesNotExist:
                logger.warning(f"Could not find email with ESP message ID: {message_id}")
                continue
            
            # Update email status based on event type
            _update_email_status(email_log, event_type)
            
            # Create an event record
            EmailEvent.objects.create(
                email_log=email_log,
                event_type=event_type,
                data=event,
                ip_address=event.get('ip'),
                user_agent=event.get('useragent')
            )
            
        return HttpResponse("OK")
    except Exception as e:
        logger.error(f"Error processing Mailjet webhook: {str(e)}")
        return HttpResponse(f"Error: {str(e)}", status=500)


def _process_generic_webhook(payload, esp):
    """Process webhook events from other ESPs."""
    logger.info(f"Processing generic webhook for ESP: {esp}")
    logger.info(f"Payload: {payload}")
    return HttpResponse("OK")


def _update_email_status(email_log, event_type):
    """Update email status based on event type."""
    now = timezone.now()
    
    # Map event types to status
    if event_type in ['delivered', 'delivery']:
        email_log.status = EmailLog.STATUS_DELIVERED
        email_log.delivered_at = now
    elif event_type in ['open', 'opened']:
        email_log.status = EmailLog.STATUS_OPENED
        email_log.opens += 1
    elif event_type in ['click', 'clicked']:
        email_log.status = EmailLog.STATUS_CLICKED
        email_log.clicks += 1
    elif event_type in ['bounce', 'bounced', 'hard_bounce']:
        email_log.status = EmailLog.STATUS_BOUNCED
    elif event_type in ['dropped', 'rejected']:
        email_log.status = EmailLog.STATUS_REJECTED
    elif event_type in ['spam', 'complained', 'complaint']:
        email_log.status = EmailLog.STATUS_COMPLAINED
    elif event_type in ['unsubscribe', 'unsubscribed']:
        email_log.status = EmailLog.STATUS_UNSUBSCRIBED
    
    email_log.save() 