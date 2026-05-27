from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name = serializers.SerializerMethodField()
    actor_avatar = serializers.SerializerMethodField()
    # Friendly type label for the frontend icon logic
    type = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "type",
            "title",
            "message",
            "post_slug",
            "comment_id",
            "is_read",
            "created_at",
            "actor_name",
            "actor_avatar",
        )
        read_only_fields = fields

    def get_actor_name(self, obj):
        return obj.actor.display_name if obj.actor else "Someone"

    def get_actor_avatar(self, obj):
        if obj.actor and obj.actor.avatar:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.actor.avatar.url)
            return obj.actor.avatar.url
        return None

    def get_type(self, obj):
        """Map internal type to a simple alert/success/info string for frontend."""
        alert_types = {Notification.TYPE_SYSTEM}
        success_types = {Notification.TYPE_LIKE_POST, Notification.TYPE_LIKE_COMMENT}
        if obj.notification_type in alert_types:
            return "alert"
        if obj.notification_type in success_types:
            return "success"
        return "info"