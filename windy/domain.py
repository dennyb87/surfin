from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, List, Optional

import requests
from django.core.files import File
from django.utils import timezone
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
    preview: str

    def to_dict(self):
        return {
            "pk": self.pk,
            "created": self.created.strftime("%m/%d/%Y, %H:%M:%S"),
            "webcam": self.webcam,
            "status": self.status,
            "last_updated_on": self.last_updated_on,
            "preview": self.preview.url,
        }

    def persist(self) -> WindyWebcamData:
        raw_preview = requests.get(self.preview).content
        tmp_file = NamedTemporaryFile()
        tmp_file.write(raw_preview)
        preview = File(tmp_file)
        obj = WindyWebcamData(
            created=self.created,
            webcam=self.webcam,
            title=self.title,
            view_count=self.view_count,
            status=self.status,
            last_updated_on=self.last_updated_on,
        )
        obj.preview.save(name="windy.jpg", content=preview)
        return obj

    @classmethod
    def from_orm_obj(cls, orm_obj: WindyWebcamData):
        return cls(
            pk=orm_obj.pk,
            created=orm_obj.created,
            webcam=orm_obj.webcam,
            title=orm_obj.title,
            view_count=orm_obj.view_count,
            status=orm_obj.status,
            last_updated_on=orm_obj.last_updated_on,
            preview=orm_obj.preview,
        )

    @classmethod
    def from_raw_data(
        cls, raw_data: dict, created: "datetime", webcam: "WindyWebcam"
    ) -> "WindyWebcamDataDomain":
        preview_url = raw_data["images"]["current"]["preview"]
        return cls(
            pk=None,
            created=created,
            webcam=webcam,
            title=raw_data["title"],
            view_count=raw_data["viewCount"],
            status=raw_data["status"],
            last_updated_on=raw_data["lastUpdatedOn"],
            preview=preview_url,
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
            webcam = WindyWebcamDataDomain.from_raw_data(
                raw_data=webcam_data,
                created=timezone.now(),
                webcam=webcam_uid_to_orm_obj[webcam_id],
            )
            webcams.append(webcam)
        return webcams

    @classmethod
    def get_current_webcam(cls, spots: "SpotSetDomain") -> "WindyWebcamSetDomain":
        webcam_data_set = cls.fetch_webcam_data(spots)
        orm_objs = [data.persist() for data in webcam_data_set]
        domain_objs = [
            WindyWebcamDataDomain.from_orm_obj(orm_obj) for orm_obj in orm_objs
        ]
        return WindyWebcamDataSetDomain(domain_objs)


class WindyWebcamDataSetDomain(List["WindyWebcamDataDomain"]):
    class WindyWebcamDataNotFoundForSpot(Exception):
        pass

    def for_spot(self, spot: "SpotDomain") -> "WindyWebcamDataDomain":
        for data in self:
            if spot.pk == data.webcam.spot.pk:
                return data
        return self.WindyWebcamDataNotFoundForSpot(f"{spot}")
