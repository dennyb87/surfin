from dataclasses import dataclass
from typing import TYPE_CHECKING, List
from cft_buoy_data_extractor.client import CFTBuoyDataExtractor
from cft_buoy_data_extractor.constants import SignificantWaveHeight, Station
from django.utils import timezone

if TYPE_CHECKING:
    from spots.domain import SpotSetDomain


@dataclass
class CFTBuoyDataDomain:
    pass


class CFTBuoyDataSetDomain(List["CFTBuoyDataDomain"]):
    pass


class CFTBuoyService:

    def __init__(self):
        self.now = timezone.now()
        self.start_of_day = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
        self.hours = int((self.now - self.start_of_day).seconds / 3600)
        self.graphs = [
            SignificantWaveHeight(
                date=self.now.date().strftime("%d/%m/%Y"), hours=self.hours
            )
        ]

    @classmethod
    def station_by_id(cls, station_id: str):
        return [station for station in Station if station.value == station_id][0]

    def get_data(self, station: Station):
        for graph in self.graphs:
            client = CFTBuoyDataExtractor(
                station=station,
                graph=graph,
            )

    def get_current_data(self, spots: "SpotSetDomain") -> "CFTBuoyDataSetDomain":
        station_ids = set([spot.cft_buoy_station_id for spot in spots])
        for station_id in station_ids:
            station = self.station_by_id(station_id)
            data = self.get_data(station)
