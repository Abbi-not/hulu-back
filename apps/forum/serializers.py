from rest_framework import serializers
from django.utils.text import slugify
import uuid

from apps.accounts.serializers import UserPublicSerializer
from .models import Category, Post, Comment, Like


class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "icon", "post_count")

    def get_post_count(self, obj):
        return obj.posts.filter(status=Post.STATUS_PUBLISHED).count()


class CommentSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id", "post", "author", "parent", "body",
            "replies", "likes_count", "is_liked", "created_at", "updated_at",
        )
        read_only_fields = ("id", "author", "created_at", "updated_at")

    def get_replies(self, obj):
        if obj.parent is None:
            return CommentSerializer(
                obj.replies.all(), many=True, context=self.context
            ).data
        return []

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostListSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id", "author", "category", "title", "slug",
            "body", "image", "status", "is_pinned",
            "views_count", "likes_count", "comments_count",
            "is_liked", "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "author", "views_count", "created_at", "updated_at")

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class PostDetailSerializer(PostListSerializer):
    comments = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ("comments",)

    def get_comments(self, obj):
        top_level = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(top_level, many=True, context=self.context).data


class PostWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = ("title", "body", "image", "status", "category_id")

    def create(self, validated_data):
        title = validated_data.get("title", "")
        base_slug = slugify(title)
        slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        validated_data["slug"] = slug
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
