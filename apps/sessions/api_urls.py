from django.urls import path

from apps.sessions.views import (
    SessionDetailAPIView,
    SessionExerciseDetailAPIView,
    SessionExerciseListAPIView,
    SessionListAPIView,
)

app_name = "sessions_api"

urlpatterns = [
    path("", SessionListAPIView.as_view(), name="session-list"),
    path("<int:pk>/", SessionDetailAPIView.as_view(), name="session-detail"),
    path(
        "<int:sessionId>/exercises/",
        SessionExerciseListAPIView.as_view(),
        name="session-exercise-list",
    ),
    path(
        "<int:sessionId>/exercises/<int:pk>/",
        SessionExerciseDetailAPIView.as_view(),
        name="session-exercise-detail",
    ),
]
