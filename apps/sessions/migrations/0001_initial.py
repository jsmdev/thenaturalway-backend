# Generated manually for sessions app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('routines', '0001_initial'),
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('duration_minutes', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('rpe', models.IntegerField(blank=True, help_text='Rate of Perceived Exertion (1-10)', null=True)),
                ('energy_level', models.CharField(blank=True, choices=[('very_low', 'Very Low'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('very_high', 'Very High')], db_index=True, max_length=20, null=True)),
                ('sleep_hours', models.DecimalField(blank=True, decimal_places=2, help_text='Horas de sueño la noche anterior', max_digits=4, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('routine', models.ForeignKey(blank=True, db_index=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sessions', to='routines.routine')),
                ('user', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'db_table': 'training_sessions',
                'indexes': [
                    models.Index(fields=['user'], name='sessions_user_idx'),
                    models.Index(fields=['routine'], name='sessions_routine_idx'),
                    models.Index(fields=['date'], name='sessions_date_idx'),
                    models.Index(fields=['energy_level'], name='sessions_energy_level_idx'),
                ],
                'ordering': ['-date', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SessionExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('sets_completed', models.IntegerField(blank=True, null=True)),
                ('repetitions', models.CharField(blank=True, max_length=50, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, help_text='Peso en kilogramos', max_digits=8, null=True)),
                ('rpe', models.IntegerField(blank=True, help_text='Rate of Perceived Exertion (1-10)', null=True)),
                ('rest_seconds', models.IntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exercise', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_exercises', to='exercises.exercise')),
                ('session', models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name='session_exercises', to='training_sessions.session')),
            ],
            options={
                'verbose_name': 'Session Exercise',
                'verbose_name_plural': 'Session Exercises',
                'db_table': 'session_exercises',
                'indexes': [
                    models.Index(fields=['session'], name='session_exercises_session_idx'),
                    models.Index(fields=['exercise'], name='session_exercises_exercise_idx'),
                    models.Index(fields=['order'], name='session_exercises_order_idx'),
                ],
                'ordering': ['order', 'id'],
            },
        ),
    ]

