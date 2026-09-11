from django.contrib import admin
from classification.models import Classification, ClassificationAlternative, ProductAttribute

@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'category', 'confidence', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('product__product_name', 'product__product_number')

@admin.register(ClassificationAlternative)
class ClassificationAlternativeAdmin(admin.ModelAdmin):
    list_display = ('classification', 'category', 'confidence', 'rank')

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('classification', 'attribute', 'value', 'confidence')
