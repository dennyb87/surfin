# Generated by Django 4.2 on 2025-01-02 20:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("windy", "0004_remove_windywebcamdata_windy_webcam_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="windywebcam",
            name="created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 1, 2, 20, 15, 56, 26254, tzinfo=datetime.timezone.utc
                )
            ),
        ),
        migrations.AlterField(
            model_name="windywebcamdata",
            name="created",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2025, 1, 2, 20, 15, 56, 26667, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]
