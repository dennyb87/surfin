# Generated by Django 4.2 on 2024-09-21 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("spots", "0001_initial"),
        ("meteonetwork", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="meteonetworkirtdata",
            name="spot",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="spots.spot"
            ),
        ),
    ]