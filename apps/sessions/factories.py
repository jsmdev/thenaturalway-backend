from __future__ import annotations

import random
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from apps.exercises.factories import ExerciseFactory
from apps.routines.factories import RoutineFactory
from apps.sessions.models import Session, SessionExercise
from apps.users.factories import UserFactory


class SessionFactory(DjangoModelFactory):
    """Factory para crear sesiones de prueba."""

    class Meta:
        model = Session

    user = factory.SubFactory(UserFactory)
    routine = factory.SubFactory(RoutineFactory)
    date = factory.LazyFunction(lambda: timezone.now().date())
    start_time = factory.LazyFunction(lambda: timezone.now())
    end_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=1))
    duration_minutes = 60
    rpe = factory.Iterator([6, 7, 8, 9])
    energy_level = factory.Iterator(["low", "medium", "high"])
    sleep_hours = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(5.0, 10.0), 2))))
    notes = factory.Faker("text", max_nb_chars=200)


class SessionExerciseFactory(DjangoModelFactory):
    """Factory para crear ejercicios de sesión de prueba."""

    class Meta:
        model = SessionExercise

    session = factory.SubFactory(SessionFactory)
    exercise = factory.SubFactory(ExerciseFactory)
    order = factory.Sequence(lambda n: n)
    sets_completed = factory.Iterator([3, 4, 5])
    repetitions = factory.Iterator(["8-10", "10", "12"])
    weight = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10.0, 100.0), 2))))
    rpe = factory.Iterator([7, 8, 9])
    rest_seconds = factory.Iterator([60, 90, 120])
    notes = factory.Faker("text", max_nb_chars=100)
