from django.db import models
from django.utils import timezone

from surfin import settings


class IPCamLiveWebcam(models.Model):
    created = models.DateTimeField(default=timezone.now)
    alias = models.CharField(max_length=1000, unique=True)
    name = models.CharField(max_length=1000, unique=True)
    spot = models.ForeignKey("spots.Spot", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.__class__.__name__} {self.name} {self.alias} #{self.pk}"


class IPCamLiveData(models.Model):
    created = models.DateTimeField(default=timezone.now)
    webcam = models.ForeignKey(IPCamLiveWebcam, on_delete=models.PROTECT)
    preview = models.ImageField(upload_to=settings.IPCAMLIVE_ROOT)
