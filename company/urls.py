from django.urls import path

from . import views

app_name = "company"

urlpatterns = [
    path('setup/', views.SetupStep1View.as_view(), name='setup'),
    path('setup/features/', views.SetupStep2View.as_view(), name='setup_features'),
    path('setup/step3/', views.SetupStep3View.as_view(), name='setup_step3'),
    path('setup/complete/', views.SetupCompleteView.as_view(), name='setup_complete'),
    path('profile/', views.profile, name='profile'),
]
