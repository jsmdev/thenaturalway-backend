from django.urls import path

from apps.sessions.web_views import (
    SessionListView,
    SessionDetailView,
    SessionCreateView,
    SessionUpdateView,
    SessionDeleteView,
    SessionExerciseCreateView,
    SessionExerciseUpdateView,
    SessionExerciseDeleteView,
)

app_name = "sessions"

urlpatterns = [
    path("", SessionListView.as_view(), name="list"),
    path("create/", SessionCreateView.as_view(), name="create"),
    path("<int:pk>/", SessionDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", SessionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", SessionDeleteView.as_view(), name="delete"),
    path("<int:pk>/exercises/create/", SessionExerciseCreateView.as_view(), name="exercise-create"),
    path(
        "<int:pk>/exercises/<int:exerciseId>/update/",
        SessionExerciseUpdateView.as_view(),
        name="exercise-update",
    ),
    path(
        "<int:pk>/exercises/<int:exerciseId>/delete/",
        SessionExerciseDeleteView.as_view(),
        name="exercise-delete",
    ),
]

