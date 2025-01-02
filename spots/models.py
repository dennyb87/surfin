from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from spots.constants import WaveSizeScore


if TYPE_CHECKING:
    from meteonetwork.models import MeteoNetworkIRTData


class Spot(models.Model):
    name = models.CharField(max_length=1000)
    lat = models.CharField(max_length=1000)
    lon = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} #{self.pk}"


class SpotSnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    spot = models.ForeignKey("spots.Spot", on_delete=models.PROTECT)
    meteonetwork_irt_data: "MeteoNetworkIRTData" = models.ForeignKey(
        "meteonetwork.MeteoNetworkIRTData", on_delete=models.PROTECT
    )
    windy_webcam_data = models.ForeignKey(
        "windy.WindyWebcamData", on_delete=models.PROTECT
    )
    cft_buoy_data = models.ForeignKey("cftoscana.CFTBuoyData", on_delete=models.PROTECT)

    def __str__(self):
        return f"Snapshot {self.spot.name} {self.created} #{self.pk}"


class SnapshotAssessment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    snapshot = models.OneToOneField(SpotSnapshot, on_delete=models.PROTECT)
    wave_size_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[
            MinValueValidator(WaveSizeScore.MIN_SCORE),
            MaxValueValidator(WaveSizeScore.MAX_SCORE),
        ],
        help_text=WaveSizeScore.help_text,
    )
