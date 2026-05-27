from rest_framework import generics, status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserPublicSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class RegisterView(generics.CreateAPIView):
    """POST /auth/register/"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /auth/login/"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """POST /auth/logout/ — blacklist the refresh token."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    """GET / PATCH /auth/me/ — accepts JSON or multipart/form-data (for avatar upload)"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UpdateProfileSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """POST /auth/change-password/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"detail": "Password changed successfully."})


class UserPublicProfileView(generics.RetrieveAPIView):
    """GET /auth/users/<username>/"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "username"


class AdminUserListView(generics.ListAPIView):
    """
    GET /auth/admin/users/
    Staff only — list all users for admin management.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = User.objects.all().order_by('-date_joined')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(email__icontains=search) | qs.filter(username__icontains=search) | qs.filter(full_name__icontains=search)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        return qs


class AdminUserRestrictView(APIView):
    """
    POST /auth/admin/users/<username>/restrict/
    Staff only — toggle is_active on a user (restrict = deactivate, unrestrict = reactivate).
    Cannot restrict other staff or superusers.
    """
    permission_classes = [IsAdminUser]

    def post(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent admins from restricting other staff/superusers
        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Cannot restrict another staff or superuser account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevent self-restriction
        if user == request.user:
            return Response(
                {"detail": "You cannot restrict your own account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.is_active = not user.is_active
        user.save()

        action = "restricted" if not user.is_active else "unrestricted"
        return Response({
            "detail": f"User {user.username} has been {action}.",
            "is_active": user.is_active,
            "username": user.username,
        })


class AdminDeletePostView(APIView):
    """
    DELETE /auth/admin/posts/<slug>/
    Staff only — delete any post regardless of ownership.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, slug):
        from apps.forum.models import Post
        try:
            post = Post.objects.get(slug=slug)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found."}, status=status.HTTP_404_NOT_FOUND)
        title = post.title
        post.delete()
        return Response({"detail": f"Post '{title}' deleted successfully."})


class AdminDeleteCommentView(APIView):
    """
    DELETE /auth/admin/comments/<pk>/
    Staff only — delete any comment regardless of ownership.
    """
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        from apps.forum.models import Comment
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response({"detail": "Comment deleted successfully."})


class AdminStatsView(APIView):
    """
    GET /auth/admin/stats/
    Staff only — platform-wide stats for admin dashboard.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        from apps.forum.models import Post, Comment
        return Response({
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "restricted_users": User.objects.filter(is_active=False).count(),
            "total_posts": Post.objects.count(),
            "total_comments": Comment.objects.count(),
        })
