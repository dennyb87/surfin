from cft_buoy_data_extractor.constants import Station
from django.db import transaction

from cftoscana.models import CFTBuoyStation
from ipcamlive.models import IPCamLiveWebcam
from spots.domain import SpotDomain
from spots.models import Spot
from windy.models import WindyWebcam


class PontileTonfano:
    @classmethod
    @transaction.atomic
    def create(cls):
        spot = Spot.objects.create(
            name="Pontile Marina di Pietrasanta",
            lat="43.9257971",
            lon="10.1960908",
        )
        cft_buoy_station = CFTBuoyStation.objects.create(
            station_uid=Station.BOA_GORGONA,
        )
        cft_buoy_station.spots.add(spot)
        WindyWebcam.objects.create(
            windy_uid=1655061161,
            name="Pontile Tonfano - Consorzio Mare Versilia",
            spot=spot,
        )
        IPCamLiveWebcam.objects.create(
            alias="6241bbf538321",
            name="Pontile Tonfano - Consorzio Mare Versilia",
            spot=spot,
        )
        return SpotDomain.from_orm_obj(spot)
