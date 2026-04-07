from django.urls import path
from . import views

app_name = 'purchasing'

urlpatterns = [
    path('suppliers/', views.suppliers, name='suppliers'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    path('orders/', views.purchase_orders, name='purchase_orders'),
    path('orders/create/', views.purchase_order_create, name='purchase_order_create'),
    path('orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('orders/<int:pk>/edit/', views.purchase_order_edit, name='purchase_order_edit'),
    path('orders/<int:pk>/delete/', views.purchase_order_delete, name='purchase_order_delete'),
]
