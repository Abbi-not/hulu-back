import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ("notification_type", models.CharField(
                    choices=[
                        ("comment", "Comment on your post"),
                        ("like_post", "Like on your post"),
                        ("like_comment", "Like on your comment"),
                        ("reply", "Reply to your comment"),
                        ("new_post", "New post in category"),
                        ("system", "System notification"),
                    ],
                    max_length=20,
                )),
                ("title", models.CharField(max_length=255)),
                ("message", models.TextField(blank=True)),
                ("post_slug", models.CharField(blank=True, max_length=320)),
                ("comment_id", models.CharField(blank=True, max_length=50)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notifications_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "notifications",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["recipient", "-created_at"], name="notif_recipient_created_idx"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["recipient", "is_read"], name="notif_recipient_read_idx"),
        ),
    ]