from rest_framework import serializers
from classification.models import Classification, ClassificationAlternative, ProductAttribute
from products.models import Product
from taxonomy.models import TaxonomyCategory

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxonomyCategory
        fields = ['id', 'external_id', 'name', 'full_name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_number', 'product_name', 'product_category', 'image_urls']

class AlternativeSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = ClassificationAlternative
        fields = ['id', 'category', 'confidence', 'rank']

class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    value_name = serializers.CharField(source='value.name', read_only=True)
    
    class Meta:
        model = ProductAttribute
        fields = ['id', 'attribute_name', 'value_name', 'confidence']

class ClassificationSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    category = CategorySerializer()
    alternatives = AlternativeSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Classification
        fields = ['id', 'product', 'category', 'confidence', 'status', 'error', 'alternatives', 'attributes']

class ClassificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['category', 'status']
