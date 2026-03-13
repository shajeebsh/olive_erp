from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('customers/', views.customers, name='customers'),
    path('leads/', views.leads, name='leads'),
    path('opportunities/', views.opportunities, name='opportunities'),
    path('activities/', views.activities, name='activities'),
]
