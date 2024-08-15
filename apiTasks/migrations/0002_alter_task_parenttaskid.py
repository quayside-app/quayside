# Generated by Django 5.0.1 on 2024-08-15 22:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apiTasks", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="parentTaskID",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="childTasks",
                to="apiTasks.task",
            ),
        ),
    ]
