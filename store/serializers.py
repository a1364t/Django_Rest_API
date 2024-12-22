
from decimal import Decimal
from rest_framework import serializers
from django.utils.text import slugify

from .models import Category, Product


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)


class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, source='name') # what stored in db(as name)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_after_GST = serializers.SerializerMethodField(method_name='calculate_tax')

    class Meta:
        model = Product
        fields = ['id', 'title','price', 'category', 'price_after_GST', 'inventory', 'slug']

    def calculate_tax(self, product):
        return round(Decimal(product.unit_price) * Decimal(1.1), 2)
    # category = CategorySerializer()

    def validate(self, data):
        if len(data['name']) < 6:
            raise serializers.ValidationError('Product title should be at least 6 character.')
        return data
    
    def create(self, validated_data):
        product = Product(**validated_data)
        product.slug = slugify(product.name)
        product.save()
        return product
 
#     category = serializers.HyperlinkedRelatedField(
#          queryset=Category.objects.all(),
#          view_name='category-detail',
#    )

###########################################################################
# DOLLARS_TO_CENTS = 100

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255, source='name') # what stored in db(as name)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
#     price_after_GST = serializers.SerializerMethodField(method_name='calculate_tax')
#     price_cents = serializers.SerializerMethodField()
#     inventory = serializers.IntegerField()
#     category = serializers.HyperlinkedRelatedField(
#         queryset=Category.objects.all(),
#         view_name='category-detail',
#     )
   
       
#     def calculate_tax(self, product):
#         return round(product.unit_price * Decimal(1.1), 2)
    
#     def get_price_cents(self, product):
#         return int(product.unit_price * DOLLARS_TO_CENTS)
    
    