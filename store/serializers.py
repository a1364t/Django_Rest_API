
from decimal import Decimal
from rest_framework import serializers
from django.utils.text import slugify

from .models import Cart, CartItem, Category, Product, Comment


class CategorySerializer(serializers.ModelSerializer):
    num_of_products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'description', 'num_of_products']

    def get_num_of_products(self, categoty:Category):
        return categoty.products.count()

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'name', 'body']

    def create(self, validated_data):
        product_id = self.context['product_pk']
        return Comment.objects.create(product_id=product_id, **validated_data)

class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class UpdateCartItemSerializer(serializers.ModelSerializer): # To change the quantity of a product
    class Meta:
        model = CartItem
        fields = ['quantity']


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def create(self, validated_data):
        cart_id = self.context['cart_pk']

        product = validated_data.get('product')
        quantity = validated_data.get('quantity')

        try:
             #try to see if product exisit in the cartitem, add to it.
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product.id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart_id=cart_id, **validated_data)

        self.instance = cart_item
        return cart_item

class CartItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer()
    item_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']

    def get_item_total(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    # id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']
        read_only_fields = ['id']

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])


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
    
    # def update(self, instance, validated_data):
    #     instance.inventory = validated_data.get('inventory')
    #     instance.save()
    #     return instance
 
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
    
    