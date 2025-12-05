from django.urls import path

from apps.exercises.views import ExerciseDetailAPIView, ExerciseListAPIView

app_name = "exercises_api"

urlpatterns = [
    path("", ExerciseListAPIView.as_view(), name="exercise-list"),
    path("<int:pk>/", ExerciseDetailAPIView.as_view(), name="exercise-detail"),
]
