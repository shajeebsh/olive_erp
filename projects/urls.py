from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path('active/', views.active, name='active'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('timeline/', views.timeline, name='timeline'),
    path('resources/', views.resources, name='resources'),
]
