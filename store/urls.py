from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='product') # product-list | product-detail
router.register('categories', views.CategoryViewSet, basename='category') # category-list | category-detail
router.register('carts', views.CartViewSet)

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('comments', views.CommentViewSet, basename='product-comments')

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_items_router.register('items', views.CartItemsViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + cart_items_router.urls


# urlpatterns = [
#      path('', include(router.urls))
# ]


# urlpatterns = [
#    path('products/', views.ProductList.as_view()),
#    path('products/<int:pk>/', views.ProductDetail.as_view()),
#    path('categories/', views.CategoryList.as_view()),
#    path('categories/<int:pk>', views.CategoryDetail.as_view(), name='category-detail'),
# ]
