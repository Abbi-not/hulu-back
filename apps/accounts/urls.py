from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    MeView,
    ChangePasswordView,
    UserPublicProfileView,
    AdminUserListView,
    AdminUserRestrictView,
    AdminDeletePostView,
    AdminDeleteCommentView,
    AdminStatsView,
)

app_name = "accounts"

urlpatterns = [
    # Auth
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Profile
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("users/<str:username>/", UserPublicProfileView.as_view(), name="user-profile"),

    # Admin
    path("admin/stats/", AdminStatsView.as_view(), name="admin-stats"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin/users/<str:username>/restrict/", AdminUserRestrictView.as_view(), name="admin-user-restrict"),
    path("admin/posts/<slug:slug>/", AdminDeletePostView.as_view(), name="admin-delete-post"),
    path("admin/comments/<uuid:pk>/", AdminDeleteCommentView.as_view(), name="admin-delete-comment"),
]
