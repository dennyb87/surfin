from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from django.utils import timezone
from meteonetwork_api.client import MeteoNetworkClient

from meteonetwork.models import MeteoNetworkIRTData
from spots.models import Spot
from surfin import settings

if TYPE_CHECKING:
    from spots.dataclasses import SpotDomain, SpotSetDomain


@dataclass
class MeteoNetworkIRTDataDomain:
    pk: Optional[int]
    created: "datetime"
    spot: "SpotDomain"
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

    def to_orm_obj(self):
        return MeteoNetworkIRTData(
            spot=Spot.objects.get(id=self.spot.pk),
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
        )

    @classmethod
    def from_orm_obj(cls, orm_obj: "MeteoNetworkIRTData"):
        return cls(
            pk=orm_obj.pk,
            spot=orm_obj.spot,
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

    @classmethod
    def latest_for_spot(cls, spot: "SpotDomain"):
        orm_obj = MeteoNetworkIRTData.objects.filter(spot_id=spot.pk).latest("created")
        return cls.from_orm_obj(orm_obj)


@dataclass
class MeteoNetworkService:
    """Interpolated Real Time at location"""

    @classmethod
    def fetch_irt_data(cls, spot: "SpotDomain") -> "MeteoNetworkIRTDataDomain":
        client = MeteoNetworkClient(access_token=settings.METEONETWORK_API_TOKEN)
        data = client.interpolated_real_time_data(lat=spot.lat, lon=spot.lon)
        return MeteoNetworkIRTDataDomain(
            pk=None, created=timezone.now(), spot=spot, **data
        )

    @classmethod
    def get_current_irt_data(
        cls, spots: "SpotSetDomain"
    ) -> "MeteoNetworkIRTDataSetDomain":
        data_set: List["MeteoNetworkIRTDataDomain"] = []
        for spot in spots:
            data = cls.fetch_irt_data(spot)
            data_set.append(data)

        orm_objs = MeteoNetworkIRTData.objects.bulk_create(
            data.to_orm_obj() for data in data_set
        )
        domain_objs = [
            MeteoNetworkIRTDataDomain.from_orm_obj(orm_obj) for orm_obj in orm_objs
        ]
        return MeteoNetworkIRTDataSetDomain(domain_objs)


class MeteoNetworkIRTDataSetDomain(List["MeteoNetworkIRTDataDomain"]):
    def for_spot(self, spot: "SpotDomain") -> "MeteoNetworkIRTDataDomain":
        data = [data for data in self if data.spot.pk == spot.pk]
        assert len(data) == 1
        return data[0]
