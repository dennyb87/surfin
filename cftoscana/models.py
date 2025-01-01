from cft_buoy_data_extractor.constants import Station as StationEnum
from django.db import models

# Create your models here.


class Stations(models.TextChoices):
    BOA_GORGONA = StationEnum.BOA_GORGONA.value
    BOA_GIANNUTRI = StationEnum.BOA_GIANNUTRI.value
    GOMBO = StationEnum.GOMBO.value
    CASTIGLIONE_PESCAIA = StationEnum.CASTIGLIONE_PESCAIA.value


class CFTBuoyStation(models.Model):
    station_uid = models.CharField(
        max_length=1000, choices=Stations.choices, unique=True
    )
    spots = models.ManyToManyField("spots.Spot")

    def __str__(self):
        return f"{dict(Stations.choices)[self.station_uid]} - {self.station_uid}"