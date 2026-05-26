from django.contrib import admin
from .models import Category, Post, Comment, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "is_pinned", "views_count", "created_at")
    list_filter = ("status", "is_pinned", "category")
    search_fields = ("title", "body", "author__username")
    readonly_fields = ("id", "slug", "views_count", "created_at", "updated_at")
    raw_id_fields = ("author",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "parent", "created_at")
    search_fields = ("body", "author__username")
    raw_id_fields = ("author", "post", "parent")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "post", "comment", "created_at")
    raw_id_fields = ("user", "post", "comment")
