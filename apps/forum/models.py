from django.db import models
from django.conf import settings
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "forum_categories"
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True)
    body = models.TextField()
    image = models.ImageField(upload_to="posts/", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    is_pinned = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "forum_posts"
        ordering = ["-is_pinned", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["author", "-created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.filter(parent__isnull=True).count()


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "forum_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

    @property
    def likes_count(self):
        return self.likes.count()


class Like(models.Model):
    """Polymorphic-style like — either on a Post or a Comment."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="likes",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "forum_likes"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                condition=models.Q(post__isnull=False),
                name="unique_post_like",
            ),
            models.UniqueConstraint(
                fields=["user", "comment"],
                condition=models.Q(comment__isnull=False),
                name="unique_comment_like",
            ),
        ]

    def __str__(self):
        target = self.post or self.comment
        return f"{self.user} likes {target}"
