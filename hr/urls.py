from django.urls import path

from . import views

app_name = "hr"

urlpatterns = [
    path('employees/', views.employees, name='employees'),
    path('leave/', views.leave, name='leave'),
    path('attendance/', views.attendance, name='attendance'),
    path('payroll/', views.payroll, name='payroll'),
]
