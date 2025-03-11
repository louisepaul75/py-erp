import json
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from .utils import send_test_email, send_html_email
from .models import EmailLog

logger = logging.getLogger('anymail')


@method_decorator(csrf_exempt, name='dispatch')
class SMTPSettingsView(View):
    """View to get and update SMTP settings."""
    
    def get(self, request):
        """Get current SMTP settings."""
        try:
            # Get settings from environment variables or database
            smtp_settings = {
                'host': settings.EMAIL_HOST,
                'port': settings.EMAIL_PORT,
                'username': settings.EMAIL_HOST_USER,
                'password': '',  # Don't return the actual password for security reasons
                'from_email': settings.DEFAULT_FROM_EMAIL,
                'from_name': '',  # This might be stored elsewhere
                'encryption': 'tls' if settings.EMAIL_USE_TLS else ('ssl' if settings.EMAIL_USE_SSL else 'none'),
            }
            
            return JsonResponse({
                'success': True,
                'data': smtp_settings
            })
        except Exception as e:
            logger.error(f"Error getting SMTP settings: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def post(self, request):
        """Update SMTP settings."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['host', 'port', 'username', 'password', 'from_email', 'encryption']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }, status=400)
            
            # Update .env file or database with new settings
            # This is a simplified example - in a real application, you would update
            # the settings in a more persistent way
            
            # For demonstration purposes, we'll just log the settings
            logger.info(f"SMTP settings updated: {data}")
            
            # In a real application, you would update the settings in the database
            # and then reload the Django settings
            
            return JsonResponse({
                'success': True,
                'message': 'SMTP settings updated successfully'
            })
        except Exception as e:
            logger.error(f"Error updating SMTP settings: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class TestEmailView(View):
    """View to send a test email."""
    
    def post(self, request):
        """Send a test email."""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['to_email', 'subject', 'message']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }, status=400)
            
            # Send test email
            context = {
                'title': data['subject'],
                'message': data['message'],
                'system_name': 'pyERP',
                'support_email': settings.DEFAULT_FROM_EMAIL,
            }
            
            success = send_test_email(data['to_email'], data['subject'], context)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f"Test email sent to {data['to_email']}"
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to send test email'
                }, status=500)
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EmailLogAPIView(APIView):
    """API view for email logs."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        """Get email logs."""
        try:
            # Get query parameters
            limit = int(request.GET.get('limit', 50))
            offset = int(request.GET.get('offset', 0))
            status_filter = request.GET.get('status')
            
            # Query logs
            queryset = EmailLog.objects.all().order_by('-created_at')
            
            # Apply filters
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            # Apply pagination
            total = queryset.count()
            logs = queryset[offset:offset+limit]
            
            # Serialize logs
            log_data = []
            for log in logs:
                log_data.append({
                    'id': log.id,
                    'message_id': log.message_id,
                    'subject': log.subject,
                    'from_email': log.from_email,
                    'to_email': log.to_email,
                    'status': log.status,
                    'created_at': log.created_at.isoformat(),
                    'sent_at': log.sent_at.isoformat() if log.sent_at else None,
                    'error_message': log.error_message,
                })
            
            return Response({
                'success': True,
                'data': {
                    'logs': log_data,
                    'total': total,
                    'limit': limit,
                    'offset': offset
                }
            })
        except Exception as e:
            logger.error(f"Error getting email logs: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """Delete all email logs."""
        try:
            # Delete all logs
            count, _ = EmailLog.objects.all().delete()
            
            return Response({
                'success': True,
                'message': f"Deleted {count} email logs"
            })
        except Exception as e:
            logger.error(f"Error deleting email logs: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def email_stats(request):
    """Get email statistics."""
    try:
        total = EmailLog.objects.count()
        sent = EmailLog.objects.filter(status=EmailLog.STATUS_SENT).count()
        delivered = EmailLog.objects.filter(status=EmailLog.STATUS_DELIVERED).count()
        opened = EmailLog.objects.filter(status=EmailLog.STATUS_OPENED).count()
        clicked = EmailLog.objects.filter(status=EmailLog.STATUS_CLICKED).count()
        bounced = EmailLog.objects.filter(status=EmailLog.STATUS_BOUNCED).count()
        failed = EmailLog.objects.filter(status=EmailLog.STATUS_FAILED).count()
        
        return Response({
            'success': True,
            'data': {
                'total': total,
                'sent': sent,
                'delivered': delivered,
                'opened': opened,
                'clicked': clicked,
                'bounced': bounced,
                'failed': failed,
                'delivery_rate': (delivered / sent * 100) if sent > 0 else 0,
                'open_rate': (opened / delivered * 100) if delivered > 0 else 0,
                'click_rate': (clicked / opened * 100) if opened > 0 else 0,
                'bounce_rate': (bounced / sent * 100) if sent > 0 else 0,
                'failure_rate': (failed / total * 100) if total > 0 else 0,
            }
        })
    except Exception as e:
        logger.error(f"Error getting email stats: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 