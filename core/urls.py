from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('goto-search/', views.GoToSearchView.as_view(), name='goto_search'),
]
