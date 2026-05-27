from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.permissions import IsOwnerOrReadOnly
from .models import Category, Post, Comment, Like
from .serializers import (
    CategorySerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostWriteSerializer,
    CommentSerializer,
)


# ── Categories ────────────────────────────────────────────────────────────────

class CategoryListView(generics.ListAPIView):
    """GET /forum/categories/"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# ── Posts ─────────────────────────────────────────────────────────────────────

class PostListCreateView(generics.ListCreateAPIView):
    """
    GET  /forum/posts/         — list published posts
    POST /forum/posts/         — create post (auth required); accepts JSON or multipart/form-data (for image upload)
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "author__username", "status"]
    search_fields = ["title", "body", "author__username"]
    ordering_fields = ["created_at", "views_count", "likes_count"]
    ordering = ["-is_pinned", "-created_at"]

    def get_queryset(self):
        qs = Post.objects.select_related("author", "category").prefetch_related("likes")
        user = self.request.user
        if user.is_authenticated:
            # show own drafts too
            return qs.filter(
                status=Post.STATUS_PUBLISHED
            ) | qs.filter(author=user, status=Post.STATUS_DRAFT)
        return qs.filter(status=Post.STATUS_PUBLISHED)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PostWriteSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save()


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /forum/posts/<slug>/
    PATCH  /forum/posts/<slug>/   — accepts JSON or multipart/form-data (for image upload)
    DELETE /forum/posts/<slug>/
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    lookup_field = "slug"
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Post.objects.select_related("author", "category").prefetch_related(
            "likes", "comments__author", "comments__replies__author", "comments__likes"
        )

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return PostWriteSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        Post.objects.filter(pk=instance.pk).update(views_count=instance.views_count + 1)
        instance.refresh_from_db(fields=["views_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PostLikeToggleView(APIView):
    """POST /forum/posts/<slug>/like/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        post = generics.get_object_or_404(Post, slug=slug)
        like, created = Like.objects.get_or_create(user=request.user, post=post, comment=None)
        if not created:
            like.delete()
            return Response({"liked": False, "likes_count": post.likes.count()})
        return Response({"liked": True, "likes_count": post.likes.count()}, status=status.HTTP_201_CREATED)


# ── Comments ──────────────────────────────────────────────────────────────────

class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET  /forum/posts/<slug>/comments/
    POST /forum/posts/<slug>/comments/
    """
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Comment.objects.filter(
            post__slug=self.kwargs["slug"], parent__isnull=True
        ).select_related("author").prefetch_related("replies__author", "likes")

    def perform_create(self, serializer):
        post = generics.get_object_or_404(Post, slug=self.kwargs["slug"])
        serializer.save(author=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /forum/comments/<pk>/
    PATCH  /forum/comments/<pk>/
    DELETE /forum/comments/<pk>/
    """
    queryset = Comment.objects.select_related("author").prefetch_related("replies", "likes")
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]


class CommentLikeToggleView(APIView):
    """POST /forum/comments/<pk>/like/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        comment = generics.get_object_or_404(Comment, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, comment=comment, post=None)
        if not created:
            like.delete()
            return Response({"liked": False, "likes_count": comment.likes.count()})
        return Response({"liked": True, "likes_count": comment.likes.count()}, status=status.HTTP_201_CREATED)


# ── My posts ──────────────────────────────────────────────────────────────────

class MyPostsView(generics.ListAPIView):
    """GET /forum/my-posts/"""
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).select_related("category").prefetch_related("likes")