from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path('active/', views.active, name='active'),
    path('tasks/', views.tasks, name='tasks'),
    path('timeline/', views.timeline, name='timeline'),
    path('resources/', views.resources, name='resources'),
]
