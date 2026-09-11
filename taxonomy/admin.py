from django.contrib import admin
from taxonomy.models import TaxonomyCategory, TaxonomyAttribute, TaxonomyAttributeValue, CategoryAttribute

@admin.register(TaxonomyCategory)
class TaxonomyCategoryAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name', 'level', 'is_leaf', 'is_root')
    search_fields = ('name', 'external_id')
    list_filter = ('level', 'is_leaf')

@admin.register(TaxonomyAttribute)
class TaxonomyAttributeAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'name')
    search_fields = ('name',)

@admin.register(TaxonomyAttributeValue)
class TaxonomyAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'attribute', 'name')
    search_fields = ('name', 'attribute__name')

@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    list_display = ('category', 'attribute')
