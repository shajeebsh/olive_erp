from django.urls import path

from . import views

app_name = "compliance"

urlpatterns = [
    path('cro-b1/', views.cro_b1, name='cro_b1'),
    path('ct1/', views.ct1, name='ct1'),
    path('vat/', views.vat, name='vat'),
    path('rbo/', views.rbo, name='rbo'),
    path('paye/', views.paye, name='paye'),
    path('calendar/', views.calendar, name='calendar'),
    path('history/', views.history, name='history'),
]
