from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, List, Optional

import requests
from django.core.files import File
from django.utils import timezone
from spots.models import SpotSnapshot
from windy_webcams_api.v3.client import WindyWebcamsClient
from windy_webcams_api.v3.constants import WebcamFeature

from surfin import settings
from windy.models import WindyWebcam, WindyWebcamData

if TYPE_CHECKING:
    from datetime import datetime

    from spots.domain import SpotDomain, SpotSetDomain


@dataclass
class WindyWebcamDataDomain:
    pk: Optional[int]
    created: "datetime"
    webcam: "WindyWebcam"
    title: str
    view_count: int
    status: str
    last_updated_on: str
    preview: File
    snapshot: Optional[SpotSnapshot]

    def to_assessment_view(self):
        return {
            "pk": self.pk,
            "created": self.created.strftime("%m/%d/%Y, %H:%M:%S"),
            "webcam": self.webcam,
            "status": self.status,
            "last_updated_on": self.last_updated_on,
            "preview": self.preview.url,
        }

    def persist(self, snapshot) -> WindyWebcamData:
        obj = WindyWebcamData(
            created=self.created,
            webcam=self.webcam,
            title=self.title,
            view_count=self.view_count,
            status=self.status,
            last_updated_on=self.last_updated_on,
            snapshot=snapshot,
        )
        obj.preview.save(name="windy.jpg", content=self.preview)
        return obj

    @classmethod
    def load_for_snapshot(cls, snapshot_id: int):
        orm_obj = WindyWebcamData.objects.get(snapshot_id=snapshot_id)
        return cls.from_orm_obj(orm_obj)

    @classmethod
    def from_orm_obj(cls, orm_obj: WindyWebcamData):
        return cls(
            pk=orm_obj.pk,
            snapshot=orm_obj.snapshot,
            created=orm_obj.created,
            webcam=orm_obj.webcam,
            title=orm_obj.title,
            view_count=orm_obj.view_count,
            status=orm_obj.status,
            last_updated_on=orm_obj.last_updated_on,
            preview=orm_obj.preview,
        )

    @classmethod
    def from_data(
        cls, data: dict, created: "datetime", webcam: "WindyWebcam"
    ) -> "WindyWebcamDataDomain":
        preview_url = data["images"]["current"]["preview"]
        raw_preview = requests.get(preview_url).content
        tmp_file = NamedTemporaryFile()
        tmp_file.write(raw_preview)
        preview = File(tmp_file)
        return cls(
            pk=None,
            created=created,
            webcam=webcam,
            title=data["title"],
            view_count=data["viewCount"],
            status=data["status"],
            last_updated_on=data["lastUpdatedOn"],
            preview=preview,
            snapshot=None,
        )


class WindyWebcamSetDomain(List["WindyWebcamDataDomain"]):
    pass


class WindyWebcamService:
    @classmethod
    def fetch_webcam_data(cls, spots: "SpotSetDomain") -> "list[WindyWebcamDataDomain]":
        webcams = WindyWebcam.objects.filter(spot__in=[s.pk for s in spots])
        webcam_uid_to_orm_obj = {cam.windy_uid: cam for cam in webcams}
        webcam_ids = [str(uid) for uid in webcam_uid_to_orm_obj.keys()]
        assert len(webcam_ids) > 0

        client = WindyWebcamsClient(api_key=settings.WINDY_WEBCAMS_API_KEY)
        data = client.webcams(
            webcam_ids=webcam_ids,
            features=[WebcamFeature.images],
        )
        webcams = []
        for webcam_data in data["webcams"]:
            webcam_id = webcam_data["webcamId"]
            webcam = WindyWebcamDataDomain.from_data(
                data=webcam_data,
                created=timezone.now(),
                webcam=webcam_uid_to_orm_obj[webcam_id],
            )
            webcams.append(webcam)
        return webcams

    @classmethod
    def get_current_data(cls, spots: "SpotSetDomain") -> "WindyWebcamDataSetDomain":
        data_set = cls.fetch_webcam_data(spots)
        return WindyWebcamDataSetDomain(data_set)


class WindyWebcamDataSetDomain(List["WindyWebcamDataDomain"]):
    class WindyWebcamDataNotFoundForSpot(Exception):
        pass

    def for_spot(self, spot: "SpotDomain") -> "WindyWebcamDataDomain":
        for data in self:
            if spot.pk == data.webcam.spot.pk:
                return data
        raise self.WindyWebcamDataNotFoundForSpot(f"{spot}")
