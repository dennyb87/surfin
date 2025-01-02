# Generated by Django 4.2 on 2025-01-02 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cftoscana", "0002_cftbuoydata"),
        ("spots", "0003_spot_cft_buoy_station_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="spotsnapshot",
            name="cft_buoy_data",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.PROTECT,
                to="cftoscana.cftbuoydata",
            ),
            preserve_default=False,
        ),
    ]
