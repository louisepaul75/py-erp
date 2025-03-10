"""
Views for the monitoring app.
"""

from datetime import datetime
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from pyerp.monitoring.services import (
    get_database_statistics,
    get_host_resources,
    run_all_health_checks,
)


logger = logging.getLogger(__name__)


# Apply decorators to exempt this view from authentication and CSRF protection
@require_GET
@csrf_exempt
def run_health_checks(request):
    """
    Run all health checks and return the results as JSON.
    This is a basic API endpoint that can be used by external monitoring tools.
    This view is intentionally not protected by authentication to allow
    external monitoring.
    """
    try:
        # Check if the client prefers array or dictionary format
        format_param = request.GET.get("format", "array").lower()
        as_array = format_param != "dict"

        # Run health checks and get results
        results = run_all_health_checks(as_array=as_array)

        # Create response data
        response_data = {
            "success": True,
            "results": results,
            "authenticated": (
                request.user.is_authenticated
                if hasattr(request, "user")
                else False
            ),
            "server_time": datetime.now().isoformat(),
        }

        # Create response
        response = JsonResponse(response_data)

        # Store the response in case middleware needs to bypass auth
        if hasattr(request, "_auth_exempt"):
            request._auth_exempt_response = response

        return response

    except Exception as e:
        # Log the error for debugging
        logger.error(
            "Health check error: %s",
            str(e),
            exc_info=True,
        )

        # Create error response
        error_response = JsonResponse(
            {
                "success": False,
                "error": str(e),
                "error_type": e.__class__.__name__,
                "server_time": datetime.now().isoformat(),
            },
            status=500,
        )

        # Store the error response in case middleware needs to bypass auth
        if hasattr(request, "_auth_exempt"):
            request._auth_exempt_response = error_response

        return error_response


@require_GET
@csrf_exempt
def get_db_statistics(request):
    """
    Get database statistics and return them as JSON.
    This endpoint is intentionally not protected by authentication to allow
    external monitoring.
    """
    try:
        # Get database statistics
        stats = get_database_statistics()

        # Create response data
        response_data = {
            "success": True,
            "stats": stats,
            "server_time": datetime.now().isoformat(),
        }

        # Create response
        response = JsonResponse(response_data)

        # Store the response in case middleware needs to bypass auth
        if hasattr(request, "_auth_exempt"):
            request._auth_exempt_response = response

        return response

    except Exception as e:
        # Log the error for debugging
        logger.error(
            "Database statistics error: %s",
            str(e),
            exc_info=True,
        )

        # Create error response
        error_response = JsonResponse(
            {
                "success": False,
                "error": str(e),
                "error_type": e.__class__.__name__,
                "server_time": datetime.now().isoformat(),
            },
            status=500,
        )

        # Store the error response in case middleware needs to bypass auth
        if hasattr(request, "_auth_exempt"):
            request._auth_exempt_response = error_response

        return error_response


@require_GET
@csrf_exempt
def get_host_resources_view(request):
    """
    Get system resource metrics including CPU, memory, and disk usage.
    This endpoint provides real-time information about the host system.
    """
    try:
        # Get host resource metrics
        resources = get_host_resources()
        
        # Create response data
        response_data = {
            "success": True,
            "data": resources,
            "authenticated": (
                request.user.is_authenticated
                if hasattr(request, "user")
                else False
            ),
            "server_time": datetime.now().isoformat(),
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.exception("Error retrieving host resources")
        return JsonResponse(
            {
                "success": False,
                "error": str(e),
                "server_time": datetime.now().isoformat(),
            },
            status=500,
        )
