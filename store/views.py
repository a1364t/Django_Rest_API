from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet

from .paginations import DefaultPagination
from .models import Category, Product, Comment
from .serializers import CategorySerializer, CommentSerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from .filters import ProductFilter



#################### Model Viewset############################
class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['name', 'unit_price', 'inventory'] #?ordering=-inventory,-name
    search_fields = ['name', 'category__title']
    # filterset_fields = ['category_id']
    pagination_class = DefaultPagination
    filterset_class = ProductFilter
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
   
   