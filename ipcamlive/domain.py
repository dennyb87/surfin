from dataclasses import dataclass
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import requests
from django.core.files import File
from django.utils import timezone

from ipcamlive.models import IPCamLiveData, IPCamLiveWebcam

if TYPE_CHECKING:
    from spots.domain import SpotDomain, SpotSetDomain
    from spots.models import Spot, SpotSnapshot


@dataclass
class IPCamLiveWebcamDomain:
    pk: int
    created: datetime
    alias: str
    name: str
    spot: "Spot"

    @classmethod
    def from_orm_obj(cls, orm_obj: "IPCamLiveWebcam"):
        return cls(
            pk=orm_obj.pk,
            created=orm_obj.created,
            alias=orm_obj.alias,
            name=orm_obj.name,
            spot=orm_obj.spot,
        )

    def get_preview(self):
        url = f"https://ipcamlive.com/player/snapshot.php?alias={self.alias}"
        return requests.get(url, allow_redirects=True).content

    def fetch_data(self):
        raw_preview = self.get_preview()
        tmp_file = NamedTemporaryFile()
        tmp_file.write(raw_preview)
        preview = File(tmp_file)
        return IPCamLiveDataDomain(
            pk=None,
            snapshot=None,
            created=timezone.now(),
            webcam=self,
            preview=preview,
        )


class IPCamLiveDataSetDomain(list[IPCamLiveWebcamDomain]):
    class IPCamLiveDataNotFoundForSpot(Exception):
        pass

    def for_spot(self, spot: "SpotDomain") -> "IPCamLiveDataDomain":
        for data in self:
            if spot.pk == data.webcam.spot.pk:
                return data
        raise self.IPCamLiveDataNotFoundForSpot(f"{spot}")


@dataclass
class IPCamLiveDataDomain:
    pk: int
    snapshot: "SpotSnapshot"
    created: datetime
    webcam: "IPCamLiveWebcam"
    preview: File

    def to_assessment_view(self):
        return {
            "created": self.created,
            "webcam": self.webcam,
            "preview": self.preview.url,
        }

    @classmethod
    def from_orm_obj(cls, orm_obj: "IPCamLiveData"):
        return cls(
            pk=orm_obj.pk,
            snapshot=orm_obj.snapshot,
            created=orm_obj.created,
            webcam=orm_obj.webcam,
            preview=orm_obj.preview,
        )

    def persist(self, snapshot: "SpotSnapshot") -> IPCamLiveData:
        obj = IPCamLiveData(
            created=self.created,
            snapshot=snapshot,
            webcam_id=self.webcam.pk,
        )
        obj.preview.save(name="ipcamlive.jpg", content=self.preview)
        return self.from_orm_obj(obj)

    @classmethod
    def load_for_snapshot(cls, snapshot_id: int):
        orm_obj = IPCamLiveData.objects.get(snapshot_id=snapshot_id)
        return cls.from_orm_obj(orm_obj)


class IPCamLiveService:
    @classmethod
    def get_current_data(cls, spots: "SpotSetDomain") -> "IPCamLiveDataSetDomain":
        webcams = IPCamLiveWebcam.objects.filter(spot__in=[s.pk for s in spots])
        data_set = []
        for webcam in webcams:
            iplivecam = IPCamLiveWebcamDomain.from_orm_obj(webcam)
            data = iplivecam.fetch_data()
            data_set.append(data)
        return IPCamLiveDataSetDomain(data_set)
