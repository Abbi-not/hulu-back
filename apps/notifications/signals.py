from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.forum.models import Comment, Like
from .models import Notification


@receiver(post_save, sender=Comment)
def notify_on_comment(sender, instance, created, **kwargs):
    """Notify post author when someone comments; notify comment author when someone replies."""
    if not created:
        return

    actor = instance.author

    if instance.parent is None:
        # Top-level comment → notify post author
        post = instance.post
        recipient = post.author
        if recipient == actor:
            return  # Don't notify yourself
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=Notification.TYPE_COMMENT,
            title=f"{actor.display_name} commented on your post",
            message=f'"{instance.body[:120]}"',
            post_slug=post.slug,
            comment_id=str(instance.id),
        )
    else:
        # Reply → notify the parent comment author
        parent_author = instance.parent.author
        if parent_author != actor:
            Notification.objects.create(
                recipient=parent_author,
                actor=actor,
                notification_type=Notification.TYPE_REPLY,
                title=f"{actor.display_name} replied to your comment",
                message=f'"{instance.body[:120]}"',
                post_slug=instance.post.slug,
                comment_id=str(instance.id),
            )


@receiver(post_save, sender=Like)
def notify_on_like(sender, instance, created, **kwargs):
    """Notify the target (post/comment) author when someone likes their content."""
    if not created:
        return

    actor = instance.user

    if instance.post:
        recipient = instance.post.author
        if recipient == actor:
            return
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=Notification.TYPE_LIKE_POST,
            title=f"{actor.display_name} liked your post",
            message=f'"{instance.post.title[:120]}"',
            post_slug=instance.post.slug,
        )

    elif instance.comment:
        recipient = instance.comment.author
        if recipient == actor:
            return
        Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=Notification.TYPE_LIKE_COMMENT,
            title=f"{actor.display_name} liked your comment",
            message=f'"{instance.comment.body[:120]}"',
            post_slug=instance.comment.post.slug,
            comment_id=str(instance.comment.id),
        )