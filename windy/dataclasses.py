from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, List, Optional

from django.core.files import File
from django.utils import timezone
import requests
from windy_webcams_api.v3.client import WindyWebcamsClient
from windy_webcams_api.v3.constants import WebcamFeature

from spots.models import Spot
from surfin import settings
from windy.models import WindyWebcamData

if TYPE_CHECKING:
    from datetime import datetime

    from spots.dataclasses import SpotDomain, SpotSetDomain


@dataclass
class WindyWebcamDataDomain:
    pk: Optional[int]
    created: "datetime"
    spot: "SpotDomain"
    windy_webcam_id: int
    title: str
    view_count: int
    status: str
    last_updated_on: str
    preview: str

    def to_orm_obj(self) -> WindyWebcamData:
        return WindyWebcamData(
            created=self.created,
            spot=Spot.objects.get(id=self.spot.pk),
            windy_webcam_id=self.windy_webcam_id,
            title=self.title,
            view_count=self.view_count,
            status=self.status,
            last_updated_on=self.last_updated_on,
            preview=self.preview,
        )

    @classmethod
    def from_orm_obj(cls, orm_obj: WindyWebcamData):
        return cls(
            pk=orm_obj.pk,
            created=orm_obj.created,
            spot=Spot.objects.get(id=orm_obj.spot_id),
            windy_webcam_id=orm_obj.windy_webcam_id,
            title=orm_obj.title,
            view_count=orm_obj.view_count,
            status=orm_obj.status,
            last_updated_on=orm_obj.last_updated_on,
            preview=orm_obj.preview,
        )

    @classmethod
    def from_raw_data(
        cls, raw_data: dict, created: "datetime", spot: "SpotDomain"
    ) -> "WindyWebcamDataDomain":
        preview_url = raw_data["images"]["current"]["preview"]
        raw_preview = requests.get(preview_url).content
        with NamedTemporaryFile() as tmp_file:
            tmp_file.write(raw_preview)
            preview = File(tmp_file)
        return cls(
            pk=None,
            created=created,
            spot=spot,
            windy_webcam_id=raw_data["webcamId"],
            title=raw_data["title"],
            view_count=raw_data["viewCount"],
            status=raw_data["status"],
            last_updated_on=raw_data["lastUpdatedOn"],
            preview=preview,
        )


class WindyWebcamSetDomain(List["WindyWebcamDataDomain"]):
    pass


class WindyWebcamService:
    @classmethod
    def fetch_webcam_data(cls, spots: "SpotSetDomain"):
        client = WindyWebcamsClient(api_key=settings.WINDY_WEBCAMS_API_KEY)
        webcam_ids = [str(spot.windy_webcam_id) for spot in spots]
        assert len(webcam_ids) > 0
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
                spot=spots.get_spot_by_windy_webcam(webcam_id),
            )
            webcams.append(webcam)
        return webcams

    @classmethod
    def get_current_webcam(cls, spots: "SpotSetDomain") -> "WindyWebcamSetDomain":
        webcam_data_set = cls.fetch_webcam_data(spots)
        orm_objs = WindyWebcamData.objects.bulk_create(
            data.to_orm_obj() for data in webcam_data_set
        )
        domain_objs = [
            WindyWebcamDataDomain.from_orm_obj(orm_obj) for orm_obj in orm_objs
        ]
        return WindyWebcamDataSetDomain(domain_objs)


class WindyWebcamDataSetDomain(List["WindyWebcamDataDomain"]):
    def for_spot(self, spot: "SpotDomain") -> "WindyWebcamDataDomain":
        data = [data for data in self if data.spot.pk == spot.pk]
        assert len(data) == 1
        return data[0]
