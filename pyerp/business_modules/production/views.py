from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count

from pyerp.business_modules.production.models import Mold, MoldProduct
from pyerp.business_modules.production.serializers import MoldSerializer, MoldProductSerializer
from pyerp.business_modules.products.models import ParentProduct


class MoldViewSet(viewsets.ModelViewSet):
    """ViewSet for the Mold model."""
    queryset = Mold.objects.all()
    serializer_class = MoldSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='technologies')
    def technologies(self, request):
        """Return unique technologies used in molds."""
        # For now, return placeholder values
        # In the future, this would be a actual field in the model
        return Response(['Die Casting', 'Injection Molding', 'Sand Casting'])
    
    @action(detail=False, methods=['get'], url_path='alloys')
    def alloys(self, request):
        """
        Return unique alloys used in molds.
        These alloys are products that can be used in various molds.
        """
        # Get alloys from existing ParentProducts
        # In a real implementation, you would filter by a category 
        # or type field to identify products that are alloys
        alloys = ParentProduct.objects.filter(
            is_active=True
        ).values_list('name', flat=True).distinct()
        
        # If no alloys are found in the database, provide some defaults
        if not alloys:
            alloys = ['Aluminum', 'Steel', 'Brass']
            
        return Response(list(alloys))
        
    @action(detail=False, methods=['get'], url_path='tags')
    def tags(self, request):
        """Return unique tags used in molds."""
        # For now, return placeholder values
        # In the future, this would be pulled from a tags model
        return Response([
            'High Priority', 
            'New Design', 
            'Maintenance Required', 
            'Prototype'
        ])

    @action(detail=False, methods=['get'], url_path='mold_sizes')
    def mold_sizes(self, request):
        """Return available mold sizes."""
        # For now, return placeholder values
        # In the future, this would be pulled from a sizes model
        return Response([
            {'id': '1', 'name': 'Small', 'description': 'Small mold size (up to 10cm)'},
            {'id': '2', 'name': 'Medium', 'description': 'Medium mold size (10-20cm)'},
            {'id': '3', 'name': 'Large', 'description': 'Large mold size (20-30cm)'},
            {
                'id': '4', 
                'name': 'Extra Large', 
                'description': 'Extra large mold size (over 30cm)'
            }
        ])


class MoldProductViewSet(viewsets.ModelViewSet):
    """ViewSet for the MoldProduct model."""
    queryset = MoldProduct.objects.all()
    serializer_class = MoldProductSerializer
    permission_classes = [permissions.IsAuthenticated] 