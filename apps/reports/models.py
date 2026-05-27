import uuid
from django.db import models
from django.conf import settings


class Report(models.Model):
    REASON_SPAM = 'spam'
    REASON_HARASSMENT = 'harassment'
    REASON_MISINFORMATION = 'misinformation'
    REASON_INAPPROPRIATE = 'inappropriate'
    REASON_OTHER = 'other'

    REASON_CHOICES = [
        (REASON_SPAM, 'Spam'),
        (REASON_HARASSMENT, 'Harassment'),
        (REASON_MISINFORMATION, 'Misinformation'),
        (REASON_INAPPROPRIATE, 'Inappropriate Content'),
        (REASON_OTHER, 'Other'),
    ]

    TARGET_POST = 'post'
    TARGET_COMMENT = 'comment'
    TARGET_USER = 'user'

    TARGET_CHOICES = [
        (TARGET_POST, 'Post'),
        (TARGET_COMMENT, 'Comment'),
        (TARGET_USER, 'User'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_RESOLVED = 'resolved'
    STATUS_DISMISSED = 'dismissed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reports_made',
    )
    target_type = models.CharField(max_length=10, choices=TARGET_CHOICES)
    target_id = models.CharField(max_length=255)  # UUID or int as string
    target_preview = models.TextField(blank=True)  # snapshot of content at report time
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report({self.reason}) on {self.target_type}:{self.target_id} by {self.reporter}"