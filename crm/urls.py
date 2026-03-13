from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('customers/', views.customers, name='customers'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('sales-orders/', views.sales_orders, name='sales_orders'),
    path('sales-orders/create/', views.sales_order_create, name='sales_order_create'),
    path('leads/', views.leads, name='leads'),
    path('opportunities/', views.opportunities, name='opportunities'),
    path('activities/', views.activities, name='activities'),
]
