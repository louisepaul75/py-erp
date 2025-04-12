from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .views import EmployeeViewSet, SupplierViewSet
from pyerp.business_modules.products.models import ParentProduct
from pyerp.business_modules.products.serializers import ParentProductSummarySerializer


# Extend SupplierViewSet to include product actions
class SupplierViewSetWithProducts(SupplierViewSet):

    @action(detail=True, methods=['get'], url_path='products', url_name='supplier_products')
    def list_products(self, request, pk=None):
        """Return a list of parent products assigned to this supplier."""
        supplier = self.get_object()
        products = ParentProduct.objects.filter(supplier=supplier).order_by('name')
        serializer = ParentProductSummarySerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign-product', url_name='supplier_assign_product')
    def assign_product(self, request, pk=None):
        """Assign a parent product to this supplier."""
        supplier = self.get_object()
        product_id = request.data.get('product_id')

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = get_object_or_404(ParentProduct, pk=int(product_id))
        except (ValueError, TypeError):
            return Response({'error': 'Invalid product_id'}, status=status.HTTP_400_BAD_REQUEST)

        # Assign supplier to the product
        product.supplier = supplier
        product.save()

        return Response({'status': 'product assigned'}, status=status.HTTP_200_OK)


router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'suppliers', SupplierViewSetWithProducts)
print(router.urls)  # Add this line for debugging

app_name = 'business_api' # Optional: Define an app namespace

urlpatterns = [
    path('', include(router.urls)),
] 