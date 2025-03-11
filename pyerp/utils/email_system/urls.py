from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import webhooks
from . import api
from . import views

app_name = 'email_system'

# Create a router for the API
router = DefaultRouter()
router.register(r'logs', api.EmailLogViewSet)
router.register(r'events', api.EmailEventViewSet)

urlpatterns = [
    # Webhook URLs
    path('webhooks/anymail/', webhooks.anymail_webhook, name='anymail_webhook'),
    
    # API URLs
    path('', include(router.urls)),
    
    # SMTP Settings URLs
    path('settings/', views.SMTPSettingsView.as_view(), name='smtp_settings'),
    path('test-email/', views.TestEmailView.as_view(), name='test_email'),
    path('email-logs/', views.EmailLogAPIView.as_view(), name='email_logs'),
    path('email-stats/', views.email_stats, name='email_stats'),
] 