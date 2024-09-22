from dataclasses import asdict, dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List

from django.db import transaction

from cftoscana.domain import CFTBuoyService
from meteonetwork.domain import MeteoNetworkIRTDataDomain, MeteoNetworkService
from spots.models import Spot, SpotSnapshot
from windy.domain import WindyWebcamDataDomain, WindyWebcamService

if TYPE_CHECKING:
    from spots.domain import SpotDomain


class SpotSetDomain(List["SpotDomain"]):
    def get_spot_by_windy_webcam(self, webcam_id: str) -> "SpotDomain":
        spots = [spot for spot in self if spot.windy_webcam_id == webcam_id]
        return spots[0]

    @transaction.atomic
    def take_snapshots(self) -> List["SnapshotDomain"]:
        # self.refresh_buoy()
        windy_webcam_data = WindyWebcamService.get_current_webcam(spots=self)
        meteonetwork_irt_data = MeteoNetworkService.get_current_irt_data(spots=self)
        cft_buoy_data = CFTBuoyService().get_current_data(spots=self)
        snapshots = []
        for spot in self:
            snapshot = SpotSnapshotDomain.take_snapshot(
                spot=spot,
                meteonetwork_irt_data=meteonetwork_irt_data.for_spot(spot),
                windy_webcam_data=windy_webcam_data.for_spot(spot),
            )
            snapshots.append(snapshot)
        return snapshots

    # def take_snapshots(self):
    #     MeteoNetworkIRTDataDomain.latest_for_spots()


@dataclass
class SpotDomain:
    pk: int
    name: str
    lat: str
    lon: str
    windy_webcam_id: str
    cft_buoy_station_id: str

    def to_dict(self):
        return asdict(self)

    def take_snapshot(self):
        return SpotSnapshotDomain.create_from(self)

    @classmethod
    def from_orm_obj(cls, orm_obj: "Spot"):
        return cls(
            pk=orm_obj.id,
            name=orm_obj.name,
            lat=orm_obj.lat,
            lon=orm_obj.lon,
            windy_webcam_id=orm_obj.windy_webcam_id,
            cft_buoy_station_id=orm_obj.cft_buoy_station_id,
        )

    @classmethod
    def load_all(cls) -> "SpotSetDomain":
        orm_objs = Spot.objects.all()
        return SpotSetDomain([cls.from_orm_obj(orm_obj) for orm_obj in orm_objs])


@dataclass
class SpotSnapshotDomain:
    pk: int
    created: "datetime"
    spot: "SpotDomain"
    weather_data: "MeteoNetworkIRTDataDomain"
    windy_webcam_data: "WindyWebcamDataDomain"

    @classmethod
    def from_orm_obj(cls, orm_obj: "SpotSnapshot"):
        return cls(
            pk=orm_obj.pk,
            spot=SpotDomain.from_orm_obj(orm_obj.spot),
            created=orm_obj.created,
            weather_data=MeteoNetworkIRTDataDomain.from_orm_obj(
                orm_obj.meteonetwork_irt_data
            ),
            windy_webcam_data=WindyWebcamDataDomain.from_orm_obj(
                orm_obj.windy_webcam_data
            ),
        )

    @classmethod
    @transaction.atomic
    def take_snapshot(
        cls,
        spot: "SpotDomain",
        meteonetwork_irt_data: "MeteoNetworkIRTDataDomain",
        windy_webcam_data: "WindyWebcamDataDomain",
    ) -> "SpotSnapshotDomain":
        orm_obj = SpotSnapshot.objects.create(
            spot_id=spot.pk,
            meteonetwork_irt_data_id=meteonetwork_irt_data.pk,
            windy_webcam_data_id=windy_webcam_data.pk,
        )
        return cls.from_orm_obj(orm_obj)

    def to_assessment_format(self):
        return {
            "spot": self.spot.to_dict(),
            "weather": self.weather_data.to_dict(),
            "webcam": self.windy_webcam_data.to_dict(),
        }
