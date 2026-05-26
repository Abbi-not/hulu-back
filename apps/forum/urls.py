from django.urls import path
from .views import (
    CategoryListView,
    PostListCreateView,
    PostDetailView,
    PostLikeToggleView,
    CommentListCreateView,
    CommentDetailView,
    CommentLikeToggleView,
    MyPostsView,
)

app_name = "forum"

urlpatterns = [
    # Categories
    path("categories/", CategoryListView.as_view(), name="category-list"),

    # Posts
    path("posts/", PostListCreateView.as_view(), name="post-list"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<slug:slug>/like/", PostLikeToggleView.as_view(), name="post-like"),
    path("posts/<slug:slug>/comments/", CommentListCreateView.as_view(), name="post-comments"),

    # Comments
    path("comments/<uuid:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/<uuid:pk>/like/", CommentLikeToggleView.as_view(), name="comment-like"),

    # My content
    path("my-posts/", MyPostsView.as_view(), name="my-posts"),
]
