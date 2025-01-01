from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, List

from cft_buoy_data_extractor.client import CFTBuoyDataExtractor
from cft_buoy_data_extractor.constants import Graph, SignificantWaveHeight, Station
from django.utils import timezone

from cftoscana.models import CFTBuoyStation

if TYPE_CHECKING:
    from spots.domain import SpotSetDomain


@dataclass
class CFTBuoyRawData:
    x: list[float]
    y: list[float]


@dataclass
class CFTBuoyStationDomain:
    pass

    @staticmethod
    def fetch_data(self, graphs: list["Graph"]) -> "dict[Graph.type, CFTBuoyRawData]":
        data = {}
        for graph in graphs:
            client = CFTBuoyDataExtractor(
                station=self.station_uid,
                graph=graph,
            )
            graph_data = client.get_station_data()
            data[graph.type] = graph_data
        return data

    def take_snapshot(self, as_of: datetime):
        start_of_day = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
        hours = int((as_of - start_of_day).seconds / 3600)
        graphs = [
            SignificantWaveHeight(date=as_of.date().strftime("%d/%m/%Y"), hours=hours)
        ]
        return self.fetch_data(graphs=graphs)


@dataclass
class CFTBuoyDataDomain:
    pass


class CFTBuoyDataSetDomain(List["CFTBuoyDataDomain"]):
    pass


class CFTBuoyService:
    @classmethod
    def get_buoy_stations(cls, spots: "SpotSetDomain") -> tuple["CFTBuoyStationDomain"]:
        qs = CFTBuoyStation.objects.filter(spots__in=[spot.pk for spot in spots])
        buoy_stations = tuple(
            CFTBuoyStationDomain.from_orm_obj(orm_obj) for orm_obj in qs
        )
        return buoy_stations

    def get_current_data(self, spots: "SpotSetDomain") -> "CFTBuoyDataSetDomain":
        now = timezone.now()
        buoy_stations = self.get_buoy_stations(spots)
        data_set = []
        for buoy_station in buoy_stations:
            data = buoy_station.take_snapshot(as_of=now)
            data_set.append(data)
