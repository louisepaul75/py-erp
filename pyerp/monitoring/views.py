"""
Views for the monitoring app.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from datetime import datetime

from pyerp.monitoring.services import run_all_health_checks


# Apply decorators to exempt this view from authentication and CSRF protection
@require_GET
@csrf_exempt
def run_health_checks(request):
    """
    Run all health checks and return the results as JSON.
    This is a basic API endpoint that can be used by external monitoring tools.
    This view is intentionally not protected by authentication to allow external monitoring.
    """
    try:
        results = run_all_health_checks()
        response = JsonResponse({
            'success': True,
            'results': results,
            'authenticated': request.user.is_authenticated if hasattr(request, 'user') else False,
            'server_time': datetime.now().isoformat(),
            'hot_reload_test': 'SUCCESS'
        })
        
        # Store the response in case the middleware needs to bypass authentication
        if hasattr(request, '_auth_exempt'):
            request._auth_exempt_response = response
            
        return response
    except Exception as e:
        error_response = JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
        # Store the error response in case the middleware needs to bypass authentication
        if hasattr(request, '_auth_exempt'):
            request._auth_exempt_response = error_response
            
        return error_response 