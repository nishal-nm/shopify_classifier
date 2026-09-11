from django.contrib import admin
from products.models import Product, ProductBatch

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_number', 'product_name', 'product_category', 'product_sub_category', 'created_at')
    search_fields = ('product_number', 'product_name')

@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'total_products', 'processed_products', 'created_at')
    list_filter = ('status',)
