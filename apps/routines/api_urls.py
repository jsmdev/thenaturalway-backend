from django.urls import path

from apps.routines.views import (
    BlockCreateAPIView,
    DayCreateAPIView,
    RoutineDetailAPIView,
    RoutineExerciseCreateAPIView,
    RoutineListAPIView,
    WeekCreateAPIView,
)

app_name = "routines_api"

urlpatterns = [
    path("", RoutineListAPIView.as_view(), name="routine-list"),
    path("<int:pk>/", RoutineDetailAPIView.as_view(), name="routine-detail"),
    path("<int:pk>/weeks/", WeekCreateAPIView.as_view(), name="week-create"),
    path(
        "<int:pk>/weeks/<int:weekId>/days/",
        DayCreateAPIView.as_view(),
        name="day-create",
    ),
    path(
        "<int:pk>/days/<int:dayId>/blocks/",
        BlockCreateAPIView.as_view(),
        name="block-create",
    ),
    path(
        "<int:pk>/blocks/<int:blockId>/exercises/",
        RoutineExerciseCreateAPIView.as_view(),
        name="routine-exercise-create",
    ),
]
