from django.urls import path

from . import views

app_name = "company"

urlpatterns = [
    path('setup/', views.CompanySetupView.as_view(), name='setup'),
    path('setup/features/', views.FeatureSetupView.as_view(), name='setup_features'),
    path('setup/complete/', views.SetupCompleteView.as_view(), name='setup_complete'),
    path('profile/', views.profile, name='profile'),
]
