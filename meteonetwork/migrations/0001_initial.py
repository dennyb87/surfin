# Generated by Django 4.2 on 2025-01-06 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("spots", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeteoNetworkIRTData",
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
                ("lat", models.CharField(max_length=1000)),
                ("lon", models.CharField(max_length=1000)),
                ("temperature", models.DecimalField(decimal_places=4, max_digits=10)),
                ("rh", models.DecimalField(decimal_places=4, max_digits=10)),
                ("dew_point", models.DecimalField(decimal_places=4, max_digits=10)),
                (
                    "daily_rain",
                    models.DecimalField(decimal_places=4, max_digits=10, null=True),
                ),
                ("smlp", models.DecimalField(decimal_places=4, max_digits=10)),
                (
                    "wind_direction",
                    models.DecimalField(decimal_places=4, max_digits=10),
                ),
                ("wind_direction_cardinal", models.CharField(max_length=1000)),
                ("wind_speed", models.DecimalField(decimal_places=4, max_digits=10)),
                ("distance", models.DecimalField(decimal_places=4, max_digits=10)),
                (
                    "snapshot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="spots.spotsnapshot",
                    ),
                ),
            ],
        ),
    ]
