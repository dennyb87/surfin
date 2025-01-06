import factory
from cft_buoy_data_extractor.constants import Station
from factory.django import DjangoModelFactory

from cftoscana.models import CFTBuoyStation


class CFTBuoyStationFactory(DjangoModelFactory):
    class Meta:
        model = CFTBuoyStation

    station_uid = factory.fuzzy.FuzzyChoice(Station)
