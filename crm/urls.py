from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Customers
    path('customers/', views.customers, name='customers'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Sales Orders
    path('sales-orders/', views.sales_orders, name='sales_orders'),
    path('sales-orders/create/', views.sales_order_create, name='sales_order_create'),
    path('sales-orders/<int:pk>/', views.sales_order_detail, name='sales_order_detail'),
    path('sales-orders/<int:pk>/edit/', views.sales_order_edit, name='sales_order_edit'),
    path('sales-orders/<int:pk>/delete/', views.sales_order_delete, name='sales_order_delete'),
    
    # Leads
    path('leads/', views.leads, name='leads'),
    path('leads/create/', views.lead_create, name='lead_create'),
    path('leads/<int:pk>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:pk>/edit/', views.lead_edit, name='lead_edit'),
    path('leads/<int:pk>/delete/', views.lead_delete, name='lead_delete'),
    
    # Other
    path('opportunities/', views.opportunities, name='opportunities'),
    path('activities/', views.activities, name='activities'),
]
