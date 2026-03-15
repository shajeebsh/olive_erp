from django.urls import include, path

from . import api, views

app_name = "compliance"

api_patterns = [
    path("deadlines/", api.ComplianceDeadlinesView.as_view(), name="deadlines"),
    path("upcoming/", api.UpcomingDeadlinesView.as_view(), name="upcoming"),
    path("pending/", api.PendingFilingsView.as_view(), name="pending"),
]

urlpatterns = [
    path("api/", include((api_patterns, "api"))),
    path("cro-b1/", views.cro_b1, name="cro_b1"),
    path("ct1/", views.ct1, name="ct1"),
    path("vat/", views.vat, name="vat"),
    path("rbo/", views.rbo, name="rbo"),
    path("paye/", views.paye, name="paye"),
    path("calendar/", views.calendar, name="calendar"),
    path("history/", views.history, name="history"),
    path("dashboard/", views.ComplianceDashboardView.as_view(), name="dashboard"),
    path("return_preview/", views.return_preview, name="return_preview"),
    path(
        "return_preview/<int:return_id>/",
        views.return_preview,
        name="return_preview_id",
    ),
    path("approval/", views.approval_workflow, name="approval_workflow"),
]
