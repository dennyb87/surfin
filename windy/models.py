from django.db import models
from django.utils import timezone

from surfin import settings


class WindyWebcam(models.Model):
    created = models.DateTimeField(default=timezone.now)
    windy_uid = models.IntegerField(unique=True)
    name = models.CharField(max_length=1000, unique=True)
    spot = models.ForeignKey("spots.Spot", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.__class__.__name__} {self.name} {self.windy_uid} #{self.pk}"


class WindyWebcamData(models.Model):
    created = models.DateTimeField(default=timezone.now())
    webcam = models.ForeignKey(WindyWebcam, on_delete=models.PROTECT)
    title = models.CharField(max_length=1000)
    view_count = models.IntegerField()
    status = models.CharField(max_length=1000)
    last_updated_on = models.CharField(max_length=1000)
    preview = models.ImageField(upload_to=settings.WINDY_WEBCAMS_ROOT)
