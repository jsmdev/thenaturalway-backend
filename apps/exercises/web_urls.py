from django.urls import path

from apps.exercises.web_views import (
    ExerciseListView,
    ExerciseDetailView,
    ExerciseCreateView,
    ExerciseUpdateView,
    ExerciseDeleteView,
)

app_name = "exercises"

urlpatterns = [
    path("", ExerciseListView.as_view(), name="list"),
    path("<int:pk>/", ExerciseDetailView.as_view(), name="detail"),
    path("create/", ExerciseCreateView.as_view(), name="create"),
    path("<int:pk>/update/", ExerciseUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", ExerciseDeleteView.as_view(), name="delete"),
]

