from itertools import count
from django.shortcuts import render
from django.db.models import Count

from .models import Category

def show_data(request):
    Category.objects.filter(pk__in=[10, 20, 30, 40,50]).update(top_product_id=1)
    
    # q1 = Customer.objects.filter(birth_date__isnull=False)
    # print(len(q1))
    return render(request, 'hello.html')