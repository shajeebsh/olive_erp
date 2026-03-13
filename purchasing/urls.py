from django.urls import path
from . import views

app_name = 'purchasing'

urlpatterns = [
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('orders/', views.purchase_orders, name='purchase_orders'),
    path('orders/create/', views.purchase_order_create, name='purchase_order_create'),
]
