from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from django.utils import timezone
from meteonetwork_api.client import MeteoNetworkClient

from meteonetwork.models import MeteoNetworkIRTData
from surfin import settings

if TYPE_CHECKING:
    from spots.domain import SpotDomain, SpotSetDomain
    from spots.models import SpotSnapshot


@dataclass
class MeteoNetworkIRTDataDomain:
    pk: Optional[int]
    snapshot: "Optional[SpotSnapshot]"
    created: "datetime"
    lat: str
    lon: str
    temperature: str
    rh: str
    dew_point: str
    daily_rain: Optional[str]  # sometimes null for some reason
    smlp: str
    wind_direction: str
    wind_direction_cardinal: str
    wind_speed: str
    distance: str
    place: Optional[str]
    name: Optional[str]
    current_tmin: Optional[str]
    current_tmed: Optional[str]
    current_tmax: Optional[str]
    current_rhmin: Optional[str]
    current_rhmed: Optional[str]
    current_rhmax: Optional[str]
    current_wgustmax: Optional[str]
    current_wspeedmax: Optional[str]
    current_wspeedmed: Optional[str]
    current_uvmed: Optional[str]
    current_uvmax: Optional[str]
    current_radmed: Optional[str]
    current_radmax: Optional[str]

    def to_assessment_view(self):
        return {
            "created": self.created,
            "temperature": self.temperature,
            "wind_direction": self.wind_direction,
            "wind_speed": self.wind_speed,
        }

    @classmethod
    def from_orm_obj(cls, orm_obj: "MeteoNetworkIRTData"):
        return cls(
            pk=orm_obj.pk,
            snapshot=orm_obj.snapshot,
            created=orm_obj.created,
            lat=orm_obj.lat,
            lon=orm_obj.lon,
            temperature=orm_obj.temperature,
            rh=orm_obj.rh,
            dew_point=orm_obj.dew_point,
            daily_rain=orm_obj.daily_rain,
            smlp=orm_obj.smlp,
            wind_direction=orm_obj.wind_direction,
            wind_direction_cardinal=orm_obj.wind_direction_cardinal,
            wind_speed=orm_obj.wind_speed,
            distance=orm_obj.distance,
            place=None,
            name=None,
            current_tmin=None,
            current_tmed=None,
            current_tmax=None,
            current_rhmin=None,
            current_rhmed=None,
            current_rhmax=None,
            current_wgustmax=None,
            current_wspeedmax=None,
            current_wspeedmed=None,
            current_uvmed=None,
            current_uvmax=None,
            current_radmed=None,
            current_radmax=None,
        )

    def persist(self, snapshot: "SpotSnapshot") -> MeteoNetworkIRTData:
        return MeteoNetworkIRTData.objects.create(
            lat=self.lat,
            lon=self.lon,
            temperature=Decimal(self.temperature),
            rh=Decimal(self.rh),
            dew_point=Decimal(self.dew_point),
            daily_rain=Decimal(self.daily_rain) if self.daily_rain else None,
            smlp=Decimal(self.smlp),
            wind_direction=Decimal(self.wind_direction),
            wind_direction_cardinal=self.wind_direction_cardinal,
            wind_speed=Decimal(self.wind_speed),
            distance=Decimal(self.distance),
            snapshot=snapshot,
        )

    @classmethod
    def load_for_snapshot(cls, snapshot_id: int):
        orm_obj = MeteoNetworkIRTData.objects.get(snapshot_id=snapshot_id)
        return cls.from_orm_obj(orm_obj)


@dataclass
class MeteoNetworkService:
    """Interpolated Real Time at location"""

    @classmethod
    def fetch_irt_data(cls, spot: "SpotDomain") -> "MeteoNetworkIRTDataDomain":
        client = MeteoNetworkClient(access_token=settings.METEONETWORK_API_TOKEN)
        data = client.interpolated_real_time_data(lat=spot.lat, lon=spot.lon)
        # no need lat/lon from api but saving lat/lon input instead!
        data.pop("lat")
        data.pop("lon")
        return MeteoNetworkIRTDataDomain(
            pk=None,
            snapshot=None,
            created=timezone.now(),
            lat=spot.lat,
            lon=spot.lon,
            **data
        )

    @classmethod
    def get_current_data(cls, spots: "SpotSetDomain") -> "MeteoNetworkIRTDataSetDomain":
        data_set: List["MeteoNetworkIRTDataDomain"] = []
        for spot in spots:
            data = cls.fetch_irt_data(spot)
            data_set.append(data)
        return MeteoNetworkIRTDataSetDomain(data_set)


class MeteoNetworkIRTDataSetDomain(List["MeteoNetworkIRTDataDomain"]):
    def for_spot(self, spot: "SpotDomain") -> "MeteoNetworkIRTDataDomain":
        data = [data for data in self if data.lat == spot.lat and data.lon == spot.lon]
        assert len(data) == 1
        return data[0]
