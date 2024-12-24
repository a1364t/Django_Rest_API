from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .  import models

class InventoryFilter(admin.SimpleListFilter):
    LESS_THAN_3 = '<3'
    BETWEEN_3_and_10 = '3<=10'
    GREATER_THAN_10 = '>10'
    title = 'Critical Inventory Status'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            (InventoryFilter.LESS_THAN_3, 'High'),
            (InventoryFilter.BETWEEN_3_and_10, 'Medium'),
            (InventoryFilter.GREATER_THAN_10, 'OK'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == InventoryFilter.LESS_THAN_3:
            return queryset.filter(inventory__lt=3)
        if self.value() == InventoryFilter.BETWEEN_3_and_10:
            return queryset.filter(inventory__range=(3,10))
        if self.value() == InventoryFilter.GREATER_THAN_10:
            return queryset.filter(inventory__gt=10)
        


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory', 'unit_price', 'inventory_status', 'product_categgory', 'num_of_comments']
    list_per_page = 50
    list_editable = ['unit_price' ]
    list_select_related = ['category']
    list_filter = ['datetime_created', InventoryFilter, 'category', ]
    actions = ['clear_inventory']
    search_fields = ['name']
    autocomplete_fields = ['category']
    prepopulated_fields = {
        'slug': ['name']
    }

    def get_queryset(self, request):
        return super()\
        .get_queryset(request) \
        .prefetch_related('comments') \
        .annotate(comments_count=Count('comments'))

    def inventory_status(self, product: models.Product): #help vs code to know the type of product
        if product.inventory < 10:
            return 'Low'
        if product.inventory > 50:
            return 'High'
        return 'Medium'
    
    @admin.display(ordering='category__title')
    def product_categgory(self, product: models.Product):
        return product.category.title
    
    @admin.display(description='# comments', ordering='comments_count')
    def num_of_comments(self, product:models.Product):
        url = (
            reverse('admin:store_comment_changelist') 
            + '?'
            + urlencode({
                'product__id': product.id,
            })
        )
        return format_html('<a href="{}">{}</a>', url, product.comments_count)

    @admin.action(description='Clear Inventory')    
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{update_count} of product(s) inventories cleared to zero.',
            messages.ERROR,
        )

class OrderItemInline(admin.TabularInline): #or StackedInline
    model = models.OrderItem
    fields = ['product', 'quantity', 'unit_price']
    extra = 1
    min_num = 1 # min num 1 product must be in order
    # max_num = 10 #max number of product

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','customer', 'status', 'datetime_created', 'num_of_items']
    list_editable = ['status']
    list_per_page = 10
    ordering = ['-datetime_created']
    list_filter = ['datetime_created']
    inlines = [OrderItemInline]

   
    def get_queryset(self, request):
        return super() \
            .get_queryset(request) \
            .prefetch_related('items') \
            .annotate(items_count=Count('items'))
    
    @admin.display(ordering='items_count', description='# items')
    def num_of_items(self, order:models.Order):
        return order.items_count

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product','status']
    list_editable = ['status']
    list_per_page = 10
    list_display_links = ['id', 'product']
    autocomplete_fields = ['product']


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['tile']

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', ]
    list_per_page = 10
    ordering = ['user__last_name', 'user__first_name']
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith']

    def first_name(self):
        return self.user.first_name
    
    def last_name(self):
        return self.user.last_name
    
    def email(self):
        return self.user.email


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'unit_price']
    autocomplete_fields = ['product']


class CartItemInline(admin.TabularInline): #or StackedInline
    model = models.CartItem
    fields = ['id','product', 'quantity']
    extra = 0
    min_num = 1


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at']
    inlines = [CartItemInline]
