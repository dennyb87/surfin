from dataclasses import dataclass
from datetime import datetime, timedelta, date
import math
from typing import TYPE_CHECKING, List, Optional, TypedDict

import pandas as pd

from cft_buoy_data_extractor.client import CFTBuoyDataExtractor
from cft_buoy_data_extractor.constants import (
    Graph,
    PeakDirection,
    PeakPeriod,
    SignificantWaveHeight,
    Station,
)
from django.utils import timezone

from cftoscana.models import CFTBuoyData, CFTBuoyStation

if TYPE_CHECKING:
    from spots.domain import SpotDomain, SpotSetDomain
    from spots.models import Spot, SpotSnapshot


class CFTBuoyRawData(TypedDict):
    x: list[float]
    y: list[float]
    unit: str


@dataclass
class CFTBuoyStationDomain:
    pk: Optional[int]
    station_uid: str
    spots_orm: "list[Spot]"

    @property
    def station(self):
        return [s for s in Station if s.value == self.station_uid][0]

    @classmethod
    def from_orm_obj(cls, orm_obj: "CFTBuoyStation"):
        return cls(
            pk=orm_obj.pk,
            station_uid=orm_obj.station_uid,
            spots_orm=orm_obj.spots.all(),
        )

    def fetch_data(self, graph: "Graph") -> CFTBuoyRawData:
        client = CFTBuoyDataExtractor(
            station=self.station,
            graph=graph,
        )
        data = client.get_station_data()
        return CFTBuoyRawData(x=data["x"], y=data["y"], unit=graph.unit)

    def take_snapshot(self, as_of: datetime) -> "CFTBuoyDataDomain":
        start_of_day = as_of.replace(hour=0, minute=0, second=0, microsecond=0)
        hours = int((as_of - start_of_day).seconds / 3600)

        graph_dirp = PeakDirection(date=as_of.date().strftime("%d/%m/%Y"), hours=hours)
        graph_tp = PeakPeriod(date=as_of.date().strftime("%d/%m/%Y"), hours=hours)
        graph_hm0 = SignificantWaveHeight(
            date=as_of.date().strftime("%d/%m/%Y"), hours=hours
        )

        wave_height = self.fetch_data(graph=graph_hm0)
        period = self.fetch_data(graph=graph_tp)
        direction = self.fetch_data(graph=graph_dirp)

        return CFTBuoyDataDomain(
            pk=None,
            snapshot=None,
            created=None,
            as_of=as_of,
            station=self,
            wave_height=wave_height,
            period=period,
            direction=direction,
        )


@dataclass
class CFTBuoyDataDomain:
    pk: Optional[int]
    snapshot: "Optional[SpotSnapshot]"
    station: "CFTBuoyStationDomain"
    created: Optional[datetime]
    as_of: datetime
    wave_height: "CFTBuoyRawData"
    period: "CFTBuoyRawData"
    direction: "CFTBuoyRawData"

    @property
    def data_delay(self) -> timedelta:
        raw_hour = self.wave_height["x"][-1]
        hour = math.floor(raw_hour)
        minute = math.floor(raw_hour - hour)
        last_datapoint_dt = self.as_of.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        delay = self.as_of - last_datapoint_dt
        return delay - timedelta(microseconds=delay.microseconds)

    def get_feature_at(self, feature: CFTBuoyRawData, as_of_hour: float) -> float:
        df = pd.DataFrame({"y": feature["y"]}, index=feature["x"])
        return df.iloc[df.index <= as_of_hour].iloc[-1].y

    def get_wave_height(self, hours_lag: float):
        as_of_hour = self.wave_height["x"][-1] - hours_lag
        return self.get_feature_at(self.wave_height, as_of_hour=as_of_hour)

    def get_direction(self, hours_lag: float):
        as_of_hour = self.direction["x"][-1] - hours_lag
        return self.get_feature_at(self.direction, as_of_hour=as_of_hour)

    def get_period(self, hours_lag: float):
        as_of_hour = self.period["x"][-1] - hours_lag
        return self.get_feature_at(self.period, as_of_hour=as_of_hour)

    def to_assessment_view(self):
        wave_height = f"{self.wave_height['y'][-1]} {self.wave_height['unit']}"
        direction = f"{self.direction['y'][-1]} {self.direction['unit']}"
        period = f"{self.period['y'][-1]} {self.period['unit']}"
        data_hours_delay = round(self.data_delay.total_seconds() / 3600, 2)
        return {
            "station": self.station,
            "as_of": self.as_of,
            "data_delay": f"{data_hours_delay} h",
            "wave_height": wave_height,
            "direction": direction,
            "period": period,
        }

    @classmethod
    def from_orm_obj(cls, orm_obj: "CFTBuoyData"):
        return cls(
            pk=orm_obj.pk,
            snapshot=orm_obj.snapshot,
            station=orm_obj.station,
            created=orm_obj.created,
            as_of=orm_obj.as_of,
            wave_height=orm_obj.wave_height,
            period=orm_obj.period,
            direction=orm_obj.direction,
        )

    def persist(self, snapshot: "SpotSnapshot") -> "CFTBuoyData":
        return CFTBuoyData.objects.create(
            pk=self.pk,
            station_id=self.station.pk,
            as_of=self.as_of,
            wave_height=self.wave_height,
            period=self.period,
            direction=self.direction,
            snapshot=snapshot,
        )

    @classmethod
    def load_for_snapshot(cls, snapshot_id: int):
        orm_obj = CFTBuoyData.objects.get(snapshot_id=snapshot_id)
        return cls.from_orm_obj(orm_obj)


class CFTBuoyDataSetDomain(List["CFTBuoyDataDomain"]):
    class BuoyDataNotFoundForSpot(Exception):
        pass

    def for_spot(self, spot: "SpotDomain") -> "CFTBuoyDataDomain":
        for data in self:
            spot_ids = [s.pk for s in data.station.spots_orm]
            if spot.pk in spot_ids:
                return data
        raise self.BuoyDataNotFoundForSpot(f"{spot}")

    def for_date(self, date: date) -> "CFTBuoyDataSetDomain":
        return self.__class__([data for data in self if data.as_of.date() == date])


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
        return CFTBuoyDataSetDomain(data_set)
