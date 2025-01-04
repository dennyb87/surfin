from dataclasses import dataclass
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

import requests
from django.core.files import File

from ipcamlive.models import IPCamLiveData, IPCamLiveWebcam

if TYPE_CHECKING:
    from spots.domain import SpotSetDomain


@dataclass
class IPCamLiveWebcamDomain:
    pk: int
    created: datetime
    alias: str
    name: str

    @classmethod
    def from_orm_obj(cls, orm_obj: "IPCamLiveWebcam"):
        return cls(
            pk=orm_obj.pk,
            created=orm_obj.created,
            alias=orm_obj.alias,
            name=orm_obj.name,
        )

    def get_preview(self):
        url = f"https://ipcamlive.com/player/snapshot.php?alias={self.alias}"
        return requests.get(url, allow_redirects=True).content

    def fetch_data(self):
        raw_preview = self.get_preview()
        tmp_file = NamedTemporaryFile()
        tmp_file.write(raw_preview)
        preview = File(tmp_file)
        obj = IPCamLiveData(
            created=self.created,
            webcam_id=self.pk,
        )
        obj.preview.save(name="ipcamlive.jpg", content=preview)
        return IPCamLiveDataDomain.from_orm_obj(obj)


@dataclass
class IPCamLiveDataSetDomain(list[IPCamLiveWebcamDomain]):
    pass


@dataclass
class IPCamLiveDataDomain:
    created: datetime
    webcam: "IPCamLiveWebcam"
    preview: str

    @classmethod
    def from_orm_obj(cls, orm_obj: "IPCamLiveData"):
        return cls(
            created=orm_obj.created,
            webcam=orm_obj.webcam,
            preview=orm_obj.preview,
        )


class IPCamLiveService:
    @classmethod
    def get_current_data(cls, spots: "SpotSetDomain") -> "IPCamLiveDataSetDomain":
        webcams = IPCamLiveWebcam.objects.filter(spot__in=[s.pk for s in spots])
        data_set = []
        for webcam in webcams:
            iplivecam = IPCamLiveWebcamDomain.from_orm_obj(webcam)
            data = iplivecam.fetch_data()
            data_set.append(data)
        return data_set
