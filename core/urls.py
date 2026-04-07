from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('goto-search/', views.GoToSearchView.as_view(), name='goto_search'),
    path('audit/', views.audit_log, name='audit_log'),
    path('system-config/', views.system_config, name='system_config'),
    path('approvals/', views.ApprovalWorkflowListView.as_view(), name='approval_list'),
    path('approvals/<int:pk>/', views.ApprovalWorkflowDetailView.as_view(), name='approval_detail'),
    path('approvals/create/<str:workflow_type>/<str:model_name>/<int:object_id>/', views.create_approval_request, name='create_approval'),
    path('upload-attachment/', views.upload_attachment, name='upload_attachment'),
]
