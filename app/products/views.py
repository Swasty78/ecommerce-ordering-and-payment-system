from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from core.permissions import IsAdminOrReadOnly
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['price', 'created_at', 'stock']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        status = self.request.query_params.get('status')
        
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Optionally allow regular users to only see active products
        if status:
             queryset = queryset.filter(status=status)
        elif not self.request.user.is_staff:
             # Default: normal users only see active products
             queryset = queryset.filter(status=Product.Status.ACTIVE)
             
        return queryset
