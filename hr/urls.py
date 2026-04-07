from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('employees/', views.employees, name='employees'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('leave/', views.leave, name='leave'),
    path('leave/create/', views.leave_create, name='leave_create'),
    path('attendance/', views.attendance, name='attendance'),
    path('payroll/', views.payroll, name='payroll'),
    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/<int:pk>/', views.payroll_detail, name='payroll_detail'),
]
