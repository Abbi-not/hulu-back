from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Report
from .serializers import ReportCreateSerializer, ReportAdminSerializer


class IsAdminUser(permissions.BasePermission):
    """Allow access only to staff/superuser accounts."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class ReportCreateView(generics.CreateAPIView):
    """
    POST /api/v1/reports/
    Any authenticated user can submit a report.
    """
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReportAdminListView(generics.ListAPIView):
    """
    GET /api/v1/reports/admin/
    Staff only — list all reports with filtering.
    """
    serializer_class = ReportAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'reason', 'target_type']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Report.objects.select_related('reporter', 'reviewed_by').all()


class ReportAdminDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/reports/admin/<pk>/
    PATCH /api/v1/reports/admin/<pk>/   — update status and admin_note
    Staff only.
    """
    serializer_class = ReportAdminSerializer
    permission_classes = [IsAdminUser]
    queryset = Report.objects.select_related('reporter', 'reviewed_by').all()


class ReportStatsView(APIView):
    """
    GET /api/v1/reports/admin/stats/
    Returns counts by status for the dashboard summary.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Report.objects.all()
        return Response({
            'total': qs.count(),
            'pending': qs.filter(status=Report.STATUS_PENDING).count(),
            'reviewed': qs.filter(status=Report.STATUS_REVIEWED).count(),
            'resolved': qs.filter(status=Report.STATUS_RESOLVED).count(),
            'dismissed': qs.filter(status=Report.STATUS_DISMISSED).count(),
        })