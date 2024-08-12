# Generated by Django 5.0.1 on 2024-08-12 17:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("apiProjects", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("startDate", models.DateField()),
                ("endDate", models.DateField()),
                ("priority", models.IntegerField()),
                ("durationMinutes", models.IntegerField()),
                ("dateCreated", models.DateField(auto_now_add=True)),
                ("dateLastEdit", models.DateField()),
                (
                    "contributorIDs",
                    models.ManyToManyField(
                        related_name="tasks", to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "lastEditor",
                    models.ForeignKey(
                        on_delete=models.SET("DELETED_PROFILE"),
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "parentTaskID",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.task",
                    ),
                ),
                (
                    "projectID",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="apiProjects.project",
                    ),
                ),
                (
                    "status",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="apiProjects.status",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("dateCreated", models.DateField(auto_now_add=True)),
                ("mood", models.IntegerField()),
                ("explanation", models.TextField()),
                (
                    "profileID",
                    models.ForeignKey(
                        on_delete=models.SET("DELETED_PROFILE"),
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "projectID",
                    models.ForeignKey(
                        on_delete=models.SET("DELETED_PROFILE"),
                        to="apiProjects.project",
                    ),
                ),
                (
                    "taskID",
                    models.ForeignKey(
                        on_delete=models.SET("DELETED_PROFILE"), to="api.task"
                    ),
                ),
            ],
        ),
    ]
