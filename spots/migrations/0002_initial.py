# Generated by Django 4.2 on 2024-09-21 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("windy", "0001_initial"),
        ("spots", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="spotsnapshot",
            name="windy_webcam_data",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="windy.windywebcamdata"
            ),
        ),
        migrations.AddField(
            model_name="snapshotassessment",
            name="snapshot",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to="spots.spotsnapshot"
            ),
        ),
    ]