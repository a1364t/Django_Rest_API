
from decimal import Decimal
from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=500)


class ProductSerializer(serializers.ModelSerializer):
    
    title = serializers.CharField(max_length=255, source='name') # what stored in db(as name)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_after_GST = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product):
        return round(product.unit_price * Decimal(1.1), 2)
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = ['id', 'title','price', 'price_after_GST', 'inventory', 'category']
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
    
    