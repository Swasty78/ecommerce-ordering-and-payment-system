from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'created_at')
    search_fields = ('name',)
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'price', 'stock', 'status', 'category', 'updated_at')
    search_fields = ('name', 'sku')
    list_filter = ('status', 'category', 'created_at')
    list_editable = ('price', 'stock', 'status')
