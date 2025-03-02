"""
Views for the monitoring app.
"""

from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

from pyerp.monitoring.services import run_all_health_checks


@user_passes_test(lambda u: u.is_superuser)
def run_health_checks(request):
    """
    Run all health checks and return the results as JSON.
    This is a basic API endpoint that can be used by external monitoring tools.
    """
    try:
        results = run_all_health_checks()
        return JsonResponse({
            'success': True,
            'results': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 