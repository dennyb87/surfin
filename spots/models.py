from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from meteonetwork.models import MeteoNetworkIRTData


class Spot(models.Model):
    name = models.CharField(max_length=1000)
    lat = models.CharField(max_length=1000)
    lon = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    windy_webcam_id = models.IntegerField()

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
    # buoy_data = models.ForeignKey()

    def __str__(self):
        return f"Snapshot {self.spot.name} {self.created} #{self.pk}"


class SnapshotAssessment(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    snapshot = models.OneToOneField(SpotSnapshot, on_delete=models.PROTECT)
    wave_type_score = models.DecimalField(max_digits=5, decimal_places=4)
