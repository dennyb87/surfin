# Generated by Django 4.2 on 2025-01-02 21:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("windy", "0005_alter_windywebcam_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="windywebcam",
            name="created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 1, 2, 21, 23, 5, 74006, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="windywebcamdata",
            name="created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 1, 2, 21, 23, 5, 74403, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]