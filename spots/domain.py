from dataclasses import asdict, dataclass
from datetime import datetime
from typing import TYPE_CHECKING, List

from django.db import transaction

from cftoscana.domain import CFTBuoyDataDomain, CFTBuoyService
from ipcamlive.domain import IPCamLiveDataDomain, IPCamLiveService
from meteonetwork.domain import MeteoNetworkIRTDataDomain, MeteoNetworkService
from spots.models import Spot, SpotSnapshot
from windy.domain import WindyWebcamDataDomain, WindyWebcamService

if TYPE_CHECKING:
    from spots.domain import SpotDomain


class SpotSetDomain(List["SpotDomain"]):
    @transaction.atomic
    def take_snapshots(self) -> List["SpotSnapshotDomain"]:
        ipcamlive_data = IPCamLiveService.get_current_data(spots=self)
        windy_webcam_data = WindyWebcamService.get_current_data(spots=self)
        meteonetwork_irt_data = MeteoNetworkService.get_current_data(spots=self)
        cft_buoy_data = CFTBuoyService.get_current_data(spots=self)

        snapshots = []
        for spot in self:
            snapshot = SpotSnapshotDomain.create_from_data(
                spot=spot,
                ipcamlive_data=ipcamlive_data.for_spot(spot),
                meteonetwork_irt_data=meteonetwork_irt_data.for_spot(spot),
                windy_webcam_data=windy_webcam_data.for_spot(spot),
                cft_buoy_data=cft_buoy_data.for_spot(spot),
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

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_orm_obj(cls, orm_obj: "Spot"):
        return cls(
            pk=orm_obj.id,
            name=orm_obj.name,
            lat=orm_obj.lat,
            lon=orm_obj.lon,
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

    @classmethod
    def from_orm_obj(cls, orm_obj: "SpotSnapshot"):
        return cls(
            pk=orm_obj.pk,
            spot=SpotDomain.from_orm_obj(orm_obj.spot),
            created=orm_obj.created,
        )

    @classmethod
    @transaction.atomic
    def create_from_data(
        cls,
        spot: "SpotDomain",
        ipcamlive_data: "IPCamLiveDataDomain",
        meteonetwork_irt_data: "MeteoNetworkIRTDataDomain",
        windy_webcam_data: "WindyWebcamDataDomain",
        cft_buoy_data: "CFTBuoyDataDomain",
    ) -> "SpotSnapshotDomain":
        snapshot_orm = SpotSnapshot.objects.create(spot_id=spot.pk)

        ipcamlive_data.persist(snapshot_orm)
        meteonetwork_irt_data.persist(snapshot_orm)
        windy_webcam_data.persist(snapshot_orm)
        cft_buoy_data.persist(snapshot_orm)

        return cls.from_orm_obj(snapshot_orm)

    def to_assessment_view(self):
        meteonetwork_data = MeteoNetworkIRTDataDomain.load_for_snapshot(
            snapshot_id=self.pk
        )
        cft_buoy_data = CFTBuoyDataDomain.load_for_snapshot(snapshot_id=self.pk)
        windy_webcam_data = WindyWebcamDataDomain.load_for_snapshot(snapshot_id=self.pk)
        iplivecam_data = IPCamLiveDataDomain.load_for_snapshot(snapshot_id=self.pk)
        return {
            "spot": self.spot.to_dict(),
            "meteonetwork": meteonetwork_data.to_assessment_view(),
            "cft_buoy": cft_buoy_data.to_assessment_view(),
            "windy_webcam": windy_webcam_data.to_assessment_view(),
            "iplivecam": iplivecam_data.to_assessment_view(),
        }
