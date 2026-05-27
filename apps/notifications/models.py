import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_COMMENT = "comment"       # someone commented on your post
    TYPE_LIKE_POST = "like_post"   # someone liked your post
    TYPE_LIKE_COMMENT = "like_comment"  # someone liked your comment
    TYPE_REPLY = "reply"           # someone replied to your comment
    TYPE_NEW_POST = "new_post"     # new post in a category (future: follows)
    TYPE_SYSTEM = "system"         # admin broadcast

    TYPE_CHOICES = [
        (TYPE_COMMENT, "Comment on your post"),
        (TYPE_LIKE_POST, "Like on your post"),
        (TYPE_LIKE_COMMENT, "Like on your comment"),
        (TYPE_REPLY, "Reply to your comment"),
        (TYPE_NEW_POST, "New post in category"),
        (TYPE_SYSTEM, "System notification"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_sent",
    )

    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    # Optional deep-link targets
    post_slug = models.CharField(max_length=320, blank=True)
    comment_id = models.CharField(max_length=50, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] → {self.recipient} : {self.title}"