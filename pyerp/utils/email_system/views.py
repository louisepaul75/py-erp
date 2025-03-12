import json
import logging
import os
import re
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
from pyerp.utils.onepassword_connect import get_email_password

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
                'use_1password': getattr(settings, 'EMAIL_USE_1PASSWORD', False),
                '1password_item_name': getattr(settings, 'EMAIL_1PASSWORD_ITEM_NAME', ''),
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
            required_fields = ['host', 'port', 'username', 'from_email', 'encryption']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }, status=400)
            
            # Check if using 1Password
            use_1password = data.get('use_1password', False)
            op_item_name = data.get('1password_item_name', '')
            
            # If using 1Password, password is not required in the request
            if not use_1password and 'password' not in data:
                return JsonResponse({
                    'success': False,
                    'error': "Password is required when not using 1Password"
                }, status=400)
            
            # Determine which .env file to update based on environment
            env_file = os.environ.get('DJANGO_SETTINGS_MODULE', '')
            if 'development' in env_file:
                env_path = os.path.join(settings.BASE_DIR.parent, 'config', 'env', '.env.dev')
            elif 'production' in env_file:
                env_path = os.path.join(settings.BASE_DIR.parent, 'config', 'env', '.env.prod')
            else:
                env_path = os.path.join(settings.BASE_DIR.parent, 'config', 'env', '.env')
            
            # Check if the file exists
            if not os.path.exists(env_path):
                logger.error(f"Environment file not found: {env_path}")
                return JsonResponse({
                    'success': False,
                    'error': f"Environment file not found: {env_path}"
                }, status=500)
            
            # Read the current .env file
            with open(env_path, 'r') as f:
                env_content = f.read()
            
            # Update or add the SMTP settings
            env_lines = env_content.split('\n')
            updated_lines = []
            
            # Define the settings to update
            settings_map = {
                'EMAIL_HOST': data['host'],
                'EMAIL_PORT': str(data['port']),
                'EMAIL_HOST_USER': data['username'],
                'DEFAULT_FROM_EMAIL': data['from_email'],
                'EMAIL_USE_TLS': 'True' if data['encryption'] == 'tls' else 'False',
                'EMAIL_USE_SSL': 'True' if data['encryption'] == 'ssl' else 'False',
                'USE_ANYMAIL_IN_DEV': 'True',  # Enable anymail in development
                'ANYMAIL_ESP': 'smtp',  # Use SMTP as the ESP
                'EMAIL_USE_1PASSWORD': 'True' if use_1password else 'False',
                'EMAIL_1PASSWORD_ITEM_NAME': op_item_name if use_1password else '',
            }
            
            # Only include password in settings if not using 1Password
            if not use_1password and 'password' in data:
                settings_map['EMAIL_HOST_PASSWORD'] = data['password']
            
            # Track which settings have been updated
            updated_settings = set()
            
            # Update existing settings
            for line in env_lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    updated_lines.append(line)
                    continue
                
                if '=' in line:
                    key, _ = line.split('=', 1)
                    key = key.strip()
                    
                    if key in settings_map:
                        updated_lines.append(f"{key}={settings_map[key]}")
                        updated_settings.add(key)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Add any settings that weren't updated
            for key, value in settings_map.items():
                if key not in updated_settings:
                    updated_lines.append(f"{key}={value}")
            
            # Write the updated content back to the .env file
            with open(env_path, 'w') as f:
                f.write('\n'.join(updated_lines))
            
            # Update the Django settings in memory
            settings.EMAIL_HOST = data['host']
            settings.EMAIL_PORT = int(data['port'])
            settings.EMAIL_HOST_USER = data['username']
            settings.DEFAULT_FROM_EMAIL = data['from_email']
            settings.EMAIL_USE_TLS = data['encryption'] == 'tls'
            settings.EMAIL_USE_SSL = data['encryption'] == 'ssl'
            settings.EMAIL_USE_1PASSWORD = use_1password
            settings.EMAIL_1PASSWORD_ITEM_NAME = op_item_name if use_1password else ''
            
            # If using 1Password, retrieve the password
            if use_1password:
                password = get_email_password(
                    email_username=data['username'],
                    item_name=op_item_name or None
                )
                if password:
                    settings.EMAIL_HOST_PASSWORD = password
                    logger.info("Retrieved email password from 1Password")
                else:
                    logger.error("Failed to retrieve email password from 1Password")
                    return JsonResponse({
                        'success': False,
                        'error': "Failed to retrieve email password from 1Password"
                    }, status=500)
            else:
                # Use the password from the request
                settings.EMAIL_HOST_PASSWORD = data.get('password', '')
            
            logger.info(f"SMTP settings updated: {data['host']}:{data['port']} (user: {data['username']})")
            
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
            
            # Log current email settings for debugging
            logger.info(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, "
                       f"USER={settings.EMAIL_HOST_USER}, SSL={settings.EMAIL_USE_SSL}, TLS={settings.EMAIL_USE_TLS}")
            
            success = send_test_email(data['to_email'], data['subject'], context)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f"Test email sent to {data['to_email']}"
                })
            else:
                # Check logs for the most recent error
                from django.db.models import Q
                from .models import EmailLog
                recent_log = EmailLog.objects.filter(
                    Q(to_email__contains=data['to_email']) & 
                    Q(subject__contains=data['subject'])
                ).order_by('-created_at').first()
                
                error_message = "Unknown error sending email. Check server logs for details."
                if recent_log:
                    error_message = f"Email status: {recent_log.status}. Check server logs for details."
                
                return JsonResponse({
                    'success': False,
                    'error': error_message
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


class UpdateEmailSettingsView(View):
    """View to update email settings."""
    
    def get(self, request):
        """Get current email settings."""
        settings_data = {
            'host': settings.EMAIL_HOST,
            'port': settings.EMAIL_PORT,
            'username': settings.EMAIL_HOST_USER,
            'password': '********' if settings.EMAIL_HOST_PASSWORD else '',
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'encryption': 'tls' if settings.EMAIL_USE_TLS else ('ssl' if settings.EMAIL_USE_SSL else 'none'),
            'use_1password': getattr(settings, 'EMAIL_USE_1PASSWORD', False),
            '1password_item_name': getattr(settings, 'EMAIL_1PASSWORD_ITEM_NAME', ''),
        }
        
        return JsonResponse(settings_data)
    
    def post(self, request):
        """Update email settings."""
        try:
            data = json.loads(request.body)
            
            # Check if using 1Password
            use_1password = data.get('use_1password', False)
            op_item_name = data.get('1password_item_name', '')
            
            # Validate required fields
            required_fields = ['host', 'port', 'username', 'encryption']
            if not use_1password:
                required_fields.append('password')
                
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f"Missing required field: {field}"
                    }, status=400)
            
            # Validate port
            try:
                port = int(data['port'])
                if port < 1 or port > 65535:
                    return JsonResponse({
                        'success': False,
                        'error': "Port must be between 1 and 65535"
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': "Port must be a number"
                }, status=400)
            
            # Validate encryption
            if data['encryption'] not in ['none', 'tls', 'ssl']:
                return JsonResponse({
                    'success': False,
                    'error': "Encryption must be one of: none, tls, ssl"
                }, status=400)
            
            # Auto-correct encryption based on common ports
            if port == 465 and data['encryption'] != 'ssl':
                logger.info(f"Auto-correcting encryption from {data['encryption']} to 'ssl' for port 465")
                data['encryption'] = 'ssl'
            elif port == 587 and data['encryption'] != 'tls':
                logger.info(f"Auto-correcting encryption from {data['encryption']} to 'tls' for port 587")
                data['encryption'] = 'tls'
            
            # Update settings in .env file
            env_file = os.environ.get('DJANGO_ENV_FILE', os.path.join(settings.BASE_DIR, 'config', 'env', '.env.dev'))
            
            if os.path.exists(env_file):
                # Read current .env file
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                # Update settings
                env_vars = {
                    'EMAIL_HOST': data['host'],
                    'EMAIL_PORT': str(data['port']),
                    'EMAIL_HOST_USER': data['username'],
                    'DEFAULT_FROM_EMAIL': data.get('from_email', data['username']),
                    'EMAIL_USE_TLS': 'True' if data['encryption'] == 'tls' else 'False',
                    'EMAIL_USE_SSL': 'True' if data['encryption'] == 'ssl' else 'False',
                    'EMAIL_USE_1PASSWORD': 'True' if use_1password else 'False',
                    'EMAIL_1PASSWORD_ITEM_NAME': op_item_name if use_1password else '',
                }
                
                # Only include password in settings if not using 1Password
                if not use_1password and 'password' in data:
                    env_vars['EMAIL_HOST_PASSWORD'] = data['password']

                # Update each variable in the .env file
                for key, value in env_vars.items():
                    pattern = re.compile(f"^{key}=.*$", re.MULTILINE)
                    if pattern.search(env_content):
                        env_content = pattern.sub(f"{key}={value}", env_content)
                    else:
                        env_content += f"\n{key}={value}"
                
                # Write updated content back to .env file
                with open(env_file, 'w') as f:
                    f.write(env_content)
            
            # Update Django settings in memory
            settings.EMAIL_HOST = data['host']
            settings.EMAIL_PORT = port
            settings.EMAIL_HOST_USER = data['username']
            settings.DEFAULT_FROM_EMAIL = data.get('from_email', data['username'])
            settings.EMAIL_USE_TLS = data['encryption'] == 'tls'
            settings.EMAIL_USE_SSL = data['encryption'] == 'ssl'
            settings.EMAIL_USE_1PASSWORD = use_1password
            settings.EMAIL_1PASSWORD_ITEM_NAME = op_item_name if use_1password else ''
            
            # If using 1Password, retrieve the password
            if use_1password:
                password = get_email_password(
                    email_username=data['username'],
                    item_name=op_item_name or None
                )
                if password:
                    settings.EMAIL_HOST_PASSWORD = password
                    logger.info("Retrieved email password from 1Password")
                else:
                    logger.error("Failed to retrieve email password from 1Password")
                    return JsonResponse({
                        'success': False,
                        'error': "Failed to retrieve email password from 1Password"
                    }, status=500)
            else:
                # Use the password from the request
                settings.EMAIL_HOST_PASSWORD = data.get('password', '')
            
            logger.info(f"Email settings updated: {data['host']}:{data['port']} (user: {data['username']})")
            
            return JsonResponse({
                'success': True,
                'message': 'Email settings updated successfully'
            })
        except Exception as e:
            logger.error(f"Error updating email settings: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500) 