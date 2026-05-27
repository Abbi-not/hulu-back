from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.pagination import StandardPagination
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/v1/notifications/
    Returns the authenticated user's notifications, newest first.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Notification.objects
            .filter(recipient=self.request.user)
            .select_related("actor")
        )


class NotificationMarkReadView(APIView):
    """
    POST /api/v1/notifications/<pk>/read/
    Toggle or set is_read on a single notification.
    Body (optional): { "read": true|false }  — defaults to true.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notif = Notification.objects.get(pk=pk, recipient=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        notif.is_read = request.data.get("read", True)
        notif.save(update_fields=["is_read"])
        return Response({"id": str(notif.id), "is_read": notif.is_read})


class NotificationMarkAllReadView(APIView):
    """
    POST /api/v1/notifications/mark-all-read/
    Marks every unread notification for the user as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({"marked": count})


class NotificationClearView(APIView):
    """
    DELETE /api/v1/notifications/clear/
    Deletes all notifications for the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        count, _ = Notification.objects.filter(recipient=request.user).delete()
        return Response({"deleted": count})


class UnreadCountView(APIView):
    """
    GET /api/v1/notifications/unread-count/
    Returns { "count": <int> } for badge display.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"count": count})