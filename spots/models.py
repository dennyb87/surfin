from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from spots.constants import SurfQualityScore, WaveSizeScore


class Spot(models.Model):
    name = models.CharField(max_length=1000, unique=True)
    lat = models.CharField(max_length=1000)
    lon = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} #{self.pk}"


class SpotSnapshot(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    spot = models.ForeignKey("spots.Spot", on_delete=models.PROTECT)

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
    surf_quality_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[
            MinValueValidator(SurfQualityScore.MIN_SCORE),
            MaxValueValidator(SurfQualityScore.MAX_SCORE),
        ],
    )
