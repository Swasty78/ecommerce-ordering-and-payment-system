from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True,
        required=False, 
        allow_null=True
    )
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'sku', 'description', 'price', 
            'stock', 'status', 'category', 'category_id', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
