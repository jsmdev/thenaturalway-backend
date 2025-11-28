from django.urls import path

from apps.routines.web_views import (
    RoutineListView,
    RoutineDetailView,
    RoutineCreateView,
    RoutineUpdateView,
    RoutineDeleteView,
    WeekCreateView,
    DayCreateView,
    BlockCreateView,
    RoutineExerciseCreateView,
)

app_name = "routines"

urlpatterns = [
    path("", RoutineListView.as_view(), name="list"),
    path("create/", RoutineCreateView.as_view(), name="create"),
    path("<int:pk>/", RoutineDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", RoutineUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", RoutineDeleteView.as_view(), name="delete"),
    path("<int:pk>/weeks/create/", WeekCreateView.as_view(), name="week-create"),
    path(
        "<int:pk>/weeks/<int:weekId>/days/create/",
        DayCreateView.as_view(),
        name="day-create",
    ),
    path(
        "<int:pk>/days/<int:dayId>/blocks/create/",
        BlockCreateView.as_view(),
        name="block-create",
    ),
    path(
        "<int:pk>/blocks/<int:blockId>/exercises/create/",
        RoutineExerciseCreateView.as_view(),
        name="exercise-create",
    ),
]
