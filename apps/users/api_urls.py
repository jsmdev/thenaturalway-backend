from django.urls import path

from apps.users.views import (
    UserLoginAPIView,
    UserLogoutAPIView,
    UserProfileAPIView,
    UserRegisterAPIView,
    UserTokenRefreshAPIView,
)

app_name = "users_api"

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("me/", UserProfileAPIView.as_view(), name="profile"),
    path("refresh/", UserTokenRefreshAPIView.as_view(), name="refresh"),
]
