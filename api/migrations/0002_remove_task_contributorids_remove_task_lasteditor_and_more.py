# Generated by Django 5.0.1 on 2024-08-15 20:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="task",
            name="contributorIDs",
        ),
        migrations.RemoveField(
            model_name="task",
            name="lastEditor",
        ),
        migrations.RemoveField(
            model_name="task",
            name="parentTaskID",
        ),
        migrations.RemoveField(
            model_name="task",
            name="projectID",
        ),
        migrations.RemoveField(
            model_name="task",
            name="status",
        ),
    ]
