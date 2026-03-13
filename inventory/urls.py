from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('products/', views.products, name='products'),
    path('stock/', views.stock, name='stock'),
    path('warehouses/', views.warehouses, name='warehouses'),
    path('movements/', views.movements, name='movements'),
]
