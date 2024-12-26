from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, DjangoModelPermissions
from .permissions import IsAdminOrReadOnly, SendPrivateEmailToCustomerPermission, CustomDjangoModelPermission

from .paginations import DefaultPagination
from .models import Cart, CartItem, Category, Customer, Order, OrderItem, Product, Comment
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CategorySerializer, CommentSerializer, CustomerSerializer, OrderForAdminSerializer, OrderSerializer, ProductSerializer, UpdateCartItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from .filters import ProductFilter
from django.db.models import Prefetch



#################### Model Viewset############################
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['name', 'unit_price', 'inventory'] #?ordering=-inventory,-name
    search_fields = ['name', 'category__title']
    # filterset_fields = ['category_id']
    pagination_class = DefaultPagination
    filterset_class = ProductFilter
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()

    # def get_queryset(self): #get category ID from URL (http://127.0.0.1:8000/store/products/?category_id=2)
    #     queryset = Product.objects.all()
    #     category_id_params = self.request.query_params.get('category_id')
    #     if category_id_params is not None:
    #           queryset = queryset.filter(category_id=category_id_params)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, pk):
            product = get_object_or_404(
                Product.objects.select_related('category'), 
                pk=pk,
            )
            if product.order_items.count() > 0:
                return Response({'error': 'There is some order items including this product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.prefetch_related('products').all()
    permission_classes = [IsAdminOrReadOnly]
    

    def destroy(self, request, pk):
        category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
        if category.products.count() > 0:
            return Response({'error': 'There is some products related to this category. Please first remove the products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    
    def get_queryset(self):
         product_pk = self.kwargs['product_pk'] #get product ID to show its comments
         return Comment.objects.filter(product_id=product_pk).all() 

    def get_serializer_context(self): # send product_id or pk to serializer
         return {'product_pk': self.kwargs['product_pk']}


class CartItemsViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete'] # remove put request
    #  serializer_class = CartItemSerializer # Defive manually => we don't want to add product information when add a new CartItem (Only ID)
    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects.select_related('product').filter(cart_id=cart_pk).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
             return AddCartItemSerializer
        elif self.request.method == "PATCH":
             return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
         return {'cart_pk': self.kwargs['cart_pk']}

class CartViewSet(CreateModelMixin, # Remoce List, Update
                  RetrieveModelMixin,
                  DestroyModelMixin, 
                  GenericViewSet):
     serializer_class = CartSerializer
     queryset = Cart.objects.prefetch_related('items__product').all()


class CustomerViewSet(ModelViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes = [IsAuthenticated]) # No ID is needed
    def me(self, request):
        user_id = request.user.id
        customer = Customer.objects.get(user_id=user_id)
        if request.method == 'GET':      
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[SendPrivateEmailToCustomerPermission]) # Detail=True => ID is needed
    def send_private_email(self, request, pk):
        return Response(f'Sending email to cusstomer {pk=}')
    

class OrderViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self): # Define basename in urls is neceessary
        queryset= Order.objects.prefetch_related(
            Prefetch(
                    'items',
                    queryset=OrderItem.objects.select_related('product'),
                )
        ).select_related('customer__user').all()
        
        user = self.request.user

        if user.is_staff:
            return queryset
        return queryset.filter(customer__user_id=user.id)
    
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return OrderForAdminSerializer
        return OrderSerializer


##################### Calss based View ###################################
# class ProductList(ListCreateAPIView):
#     serializer_class = ProductSerializer
#     queryset = Product.objects.select_related('category').all()
    
#     def get_serializer_context(self):
#         return {'request': self.request}


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     serializer_class = ProductSerializer
#     queryset = Product.objects.select_related('category').all()

#     def delete(self, request, pk):
#         product = get_object_or_404(
#             Product.objects.select_related('category'), 
#             pk=pk,
#         )
#         if product.order_items.count() > 0:
#             return Response({'error': 'There is some order items including this product'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CategoryList(ListCreateAPIView):
#     serializer_class = CategorySerializer
#     queryset = Category.objects.prefetch_related('products').all()


# class CategoryDetail(RetrieveUpdateDestroyAPIView):
#     serializer_class = CategorySerializer
#     queryset = Category.objects.prefetch_related('products')

#     def delete(self, request, pk):
#         category = get_object_or_404(Category.objects.prefetch_related('products'), pk=pk)
#         if category.products.count() > 0:
#             return Response({'error': 'There is some products related to this category. Please first remove the products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


##################### Functional View #########################
# @api_view(['GET', 'POST'])
# def product_lis(request):
#     if request.method == 'GET':
#         products_queryset = Product.objects.select_related('category').all()
#         serializer = ProductSerializer(products_queryset, many=True, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, pk):
#     product = get_object_or_404(Product.objects.select_related('category'), pk=pk)
#     if request.method == 'GET':
#         serializer= ProductSerializer(product, context={'request': request})
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.order_items.count() > 0:
#             return Response({'error': 'There is some order items including this product. Please remove them first.'},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    

        # if serializer.is_valid():
        #     serializer.validated_data
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['GET', 'PUT', 'DELETE'])
# def category_detail(request, pk):
#     category = get_object_or_404(Category, pk=pk)
#     if request.method == 'GET':
#         serializer = CategorySerializer(category)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CategorySerializer(category, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if category.products.count() > 0:
#             return Response({'error': 'There is some products related to this category. Please first remove the products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST'])
# def category_list(request):
#     if request.method == 'GET':
#         categories_queryset = Category.objects.prefetch_related('products').all()
#         serializer = CategorySerializer(categories_queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
   
   