from django.urls import path
from .views import ReportCreateView, ReportAdminListView, ReportAdminDetailView, ReportStatsView

app_name = 'reports'

urlpatterns = [
    # User endpoint — submit a report
    path('', ReportCreateView.as_view(), name='create'),

    # Admin endpoints
    path('admin/', ReportAdminListView.as_view(), name='admin-list'),
    path('admin/stats/', ReportStatsView.as_view(), name='admin-stats'),
    path('admin/<uuid:pk>/', ReportAdminDetailView.as_view(), name='admin-detail'),
]