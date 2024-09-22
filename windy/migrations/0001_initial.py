# Generated by Django 4.2 on 2024-09-21 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("spots", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WindyWebcamData",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("windy_webcam_id", models.IntegerField()),
                ("title", models.CharField(max_length=1000)),
                ("view_count", models.IntegerField()),
                ("status", models.CharField(max_length=1000)),
                ("last_updated_on", models.CharField(max_length=1000)),
                ("preview", models.ImageField(upload_to="windy_webcam_previews")),
                (
                    "spot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="spots.spot"
                    ),
                ),
            ],
        ),
    ]