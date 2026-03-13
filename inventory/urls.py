from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('products/', views.products, name='products'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('stock/', views.stock, name='stock'),
    path('warehouses/', views.warehouses, name='warehouses'),
    path('warehouses/create/', views.warehouse_create, name='warehouse_create'),
    path('movements/', views.movements, name='movements'),
    path('movements/create/', views.movement_create, name='movement_create'),
]
