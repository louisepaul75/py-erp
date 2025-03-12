"""
API views for managing external API connections.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from . import connection_manager
from pyerp.utils.logging import get_logger

# Set up logging using the centralized logging system
logger = get_logger(__name__)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_connections(request: Request) -> Response:
    """
    Get status of all external API connections.
    
    Only accessible to admin users.
    """
    connections = connection_manager.get_connections()
    return Response(connections)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_connection(request: Request, connection_name: str) -> Response:
    """
    Update the status of a specific external API connection.
    
    Only accessible to admin users.
    
    Parameters:
    - connection_name: The name of the connection to update
    
    Request body:
    - enabled: Boolean value to enable/disable the connection
    """
    try:
        data = request.data
        if 'enabled' not in data:
            return Response(
                {"error": "Missing 'enabled' field in request body"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get enabled value as boolean
        enabled = data['enabled']
        if not isinstance(enabled, bool):
            enabled = str(enabled).lower() == 'true'
        
        success = connection_manager.set_connection_status(
            connection_name, enabled
        )
        
        if success:
            # Get all connections to return updated status
            connections = connection_manager.get_connections()
            return Response(connections)
        else:
            return Response(
                {"error": f"Failed to update connection: {connection_name}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        logger.error(f"Error updating connection {connection_name}: {e}")
        return Response(
            {"error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 