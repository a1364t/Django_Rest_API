from django.urls import path
from .views import instructions_view

urlpatterns = [
    path('instructions/', instructions_view, name='instructions'),
]
