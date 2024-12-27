
from decimal import Decimal
from rest_framework import serializers
from django.utils.text import slugify
from django.db import transaction

from .models import Cart, CartItem, Category, Customer, Order, OrderItem, Product, Comment


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
            cart_item = CartItem.objects.create(cart_id=cart_id, **validated_data)

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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'birth_date']
        read_only_fields = ['user']


class OrderItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit_price']


class OrderCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255, source='user.first_name')
    last_name = serializers.CharField(max_length=255, source='user.last_name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model =Customer
        fields = ['id', 'first_name', 'last_name', 'email']


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    class Meta: 
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']



class OrderForAdminSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = OrderCustomerSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'datetime_created', 'items']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'status', 'datetime_created', 'items']


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status'] # Admin caan only update status



class OrderCreateSerializer(serializers.Serializer): # Model serializer doesn't work here
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id): # To check if there is any item in the cart

        # try:
        #     if Cart.objects.prefetch_related('items').get(id=cart_id).items.count() == 0:
        #         raise serializers.ValidationError('Your cart is empty!')
        # except Cart.DoesNotExist:
        #     raise serializers.ValidationError('There is no cart with this cart id!')

        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError('There is no cart with this cart id!')
        
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty!')
        
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = Customer.objects.get(user_id=user_id)
           
            order = Order()
            order.customer = customer
            order.save()

            # Cart.objects.prefetch_related('items').get(id=caart_id).items.all()
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)

            # order_items = list() # reduce hits to database
            # for cart_item in cart_items:
            #     order_item = OrderItem()
            #     order_item.order = order 
            #     order_item.product_id = cart_item.product_id
            #     order_item.unit_price = cart_item.product.unit_price
            #     order_item.quantity = cart_item.quantity
                
            #     order_items.append(order_item)

            # OrderItem.objects.bulk_create(order_items)


            order_items = [
                OrderItem(
                    order=order,
                    product = cart_item.product,
                    unit_price = cart_item.product.unit_price,
                    quantity = cart_item.quantity,
                ) for cart_item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.get(id=cart_id).delete()

            return order


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
    
    