from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List

from django.db import transaction

from meteonetwork.dataclasses import MeteoNetworkIRTDataDomain, MeteoNetworkService
from spots.models import Spot, SpotSnapshot
from windy.dataclasses import WindyWebcamDataDomain, WindyWebcamService

if TYPE_CHECKING:
    from spots.dataclasses import SpotDomain


class SpotSetDomain(List["SpotDomain"]):
    def get_spot_by_windy_webcam(self, webcam_id: str) -> "SpotDomain":
        spots = [spot for spot in self if spot.windy_webcam_id == webcam_id]
        return spots[0]

    def take_snapshots(self) -> List["SnapshotDomain"]:
        # self.refresh_buoy()
        windy_webcam_data = WindyWebcamService.get_current_webcam(self)
        meteonetwork_irt_data = MeteoNetworkService.get_current_irt_data(self)

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
        )

    @classmethod
    def load_all(cls) -> "SpotSetDomain":
        orm_objs = Spot.objects.all()
        return SpotSetDomain([cls.from_orm_obj(orm_obj) for orm_obj in orm_objs])


@dataclass
class SpotSnapshotDomain:
    pk: int
    created: "datetime"
    weather_data: "MeteoNetworkIRTDataDomain"
    windy_webcam_data: "WindyWebcamDataDomain"

    @classmethod
    def from_orm_obj(cls, orm_obj: "SpotSnapshot"):
        return cls(
            pk=orm_obj.pk,
            created=orm_obj.created,
            weather_data=orm_obj.meteonetwork_irt_data,
            windy_webcam_data=orm_obj.windy_webcam_data,
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
