from django.urls import path

from apps.exercises.views import ExerciseListAPIView, ExerciseDetailAPIView

app_name = "exercises"

urlpatterns = [
    path("", ExerciseListAPIView.as_view(), name="exercise-list"),
    path("<int:pk>/", ExerciseDetailAPIView.as_view(), name="exercise-detail"),
]

