from django.urls import path

from . import views

app_name = "reporting"

urlpatterns = [
    path("", views.index, name="index"),
    path("builder/", views.builder, name="builder"),
    path("saved/", views.saved, name="saved"),
    path("scheduled/", views.scheduled, name="scheduled"),
    path("datasources/", views.datasources, name="datasources"),
]
