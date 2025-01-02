from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, List

from cft_buoy_data_extractor.client import CFTBuoyDataExtractor
from cft_buoy_data_extractor.constants import Graph, SignificantWaveHeight, Station
from django.utils import timezone

from cftoscana.models import CFTBuoyData, CFTBuoyStation

if TYPE_CHECKING:
    from spots.domain import SpotSetDomain, SpotDomain


@dataclass
class CFTBuoyRawData:
    x: list[float]
    y: list[float]


@dataclass
class CFTBuoyStationDomain:
    pk: "int | None"
    station_uid: str

    @property
    def station(self):
        return [s for s in Station if s.value == self.station_uid][0]

    @classmethod
    def from_orm_obj(cls, orm_obj: "CFTBuoyStation"):
        return cls(
            pk=orm_obj.pk,
            station_uid=orm_obj.station_uid,
        )

    def fetch_data(self, graphs: list["Graph"]) -> "dict[Graph.type, CFTBuoyRawData]":
        data = {}
        for graph in graphs:
            client = CFTBuoyDataExtractor(
                station=self.station,
                graph=graph,
            )
            graph_data = client.get_station_data()
            data[graph.type] = graph_data
        return data

    def take_snapshot(self, as_of: datetime) -> "CFTBuoyDataDomain":
        start_of_day = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
        hours = int((as_of - start_of_day).seconds / 3600)
        graphs = [
            SignificantWaveHeight(date=as_of.date().strftime("%d/%m/%Y"), hours=hours)
        ]
        data = self.fetch_data(graphs=graphs)
        return CFTBuoyDataDomain(
            pk=None,
            created=None,
            as_of=as_of,
            station=self,
            data=data,
        )


@dataclass
class CFTBuoyDataDomain:
    station: "CFTBuoyStation"
    created: datetime
    as_of: datetime
    data: "dict[Graph.type, CFTBuoyRawData]"
    pk: "int | None" = None

    @classmethod
    def from_orm_obj(cls, orm_obj: "CFTBuoyData"):
        return cls(
            pk=orm_obj.pk,
            station=orm_obj.station,
            created=orm_obj.created,
            as_of=orm_obj.as_of,
            data=orm_obj.data,
        )

    def to_orm_obj(self):
        return CFTBuoyData(
            pk=self.pk,
            station_id=self.station.pk,
            as_of=self.as_of,
            data=self.data,
        )


class CFTBuoyDataSetDomain(List["CFTBuoyDataDomain"]):
    class BuoyDataNotFoundForSpot(Exception):
        pass

    def for_spot(self, spot: "SpotDomain") -> "CFTBuoyDataDomain":
        for data in self:
            spot_ids = [s.pk for s in data.station.spots.all()]
            if spot.pk in spot_ids:
                return data
        return self.BuoyDataNotFoundForSpot(f"{spot}")


class CFTBuoyService:
    @classmethod
    def get_buoy_stations(cls, spots: "SpotSetDomain") -> tuple["CFTBuoyStationDomain"]:
        qs = CFTBuoyStation.objects.filter(spots__in=[spot.pk for spot in spots])
        buoy_stations = tuple(
            CFTBuoyStationDomain.from_orm_obj(orm_obj) for orm_obj in qs
        )
        return buoy_stations

    @classmethod
    def get_current_data(cls, spots: "SpotSetDomain") -> "CFTBuoyDataSetDomain":
        now = timezone.now()
        buoy_stations = cls.get_buoy_stations(spots)
        data_set = []
        for buoy_station in buoy_stations:
            data = buoy_station.take_snapshot(as_of=now)
            data_set.append(data)

        orm_objs = CFTBuoyData.objects.bulk_create(
            data.to_orm_obj() for data in data_set
        )
        domain_objs = [CFTBuoyDataDomain.from_orm_obj(orm_obj) for orm_obj in orm_objs]
        return CFTBuoyDataSetDomain(domain_objs)
