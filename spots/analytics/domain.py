from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import F

from cftoscana.domain import CFTBuoyDataDomain, CFTBuoyDataSetDomain
from cftoscana.models import CFTBuoyData
from spots.models import SnapshotAssessment

if TYPE_CHECKING:
    from spots.domain import SpotDomain


@dataclass
class SpotSnapshotV1:
    id: int
    created: datetime
    wave_size_score: Decimal
    wind_direction: Decimal
    wind_speed: Decimal
    wave_height: float
    period: float
    direction: float

    @classmethod
    def from_data(
        cls, annotated_orm_obj: "SnapshotAssessment", buoy_data: "CFTBuoyDataDomain"
    ):
        return cls(
            id=annotated_orm_obj.pk,
            created=annotated_orm_obj.created,
            wave_size_score=annotated_orm_obj.wave_size_score,
            wind_direction=annotated_orm_obj.wind_direction,
            wind_speed=annotated_orm_obj.wind_speed,
            wave_height=buoy_data.get_wave_height_at(
                annotated_orm_obj.snapshot.created
            ),
            period=buoy_data.get_period(annotated_orm_obj.snapshot.created),
            direction=buoy_data.get_direction(annotated_orm_obj.snapshot.created),
        )

    def to_dict(self):
        return asdict(self)


class SpotSnapshotTimeserieV1(list["SpotSnapshotV1"]):
    @classmethod
    def build_for_spot(cls, spot: "SpotDomain"):
        buoy_qs = (
            CFTBuoyData.objects.filter(snapshot__spot_id=spot.pk)
            .order_by("-as_of__date", "-as_of")
            .distinct("as_of__date")
        )
        buoy_data_set = CFTBuoyDataSetDomain(
            CFTBuoyDataDomain.from_orm_obj(orm_obj) for orm_obj in buoy_qs
        )

        assessments = SnapshotAssessment.objects.filter(
            snapshot__spot_id=spot.pk
        ).annotate(
            wind_direction=F("snapshot__meteonetworkirtdata__wind_direction"),
            wind_speed=F("snapshot__meteonetworkirtdata__wind_speed"),
        )

        spot_assessments = []

        for assessment_orm in assessments:
            buoy_data = buoy_data_set.for_date(assessment_orm.snapshot.created.date())[
                0
            ]
            spot_assessment = SpotSnapshotV1.from_data(assessment_orm, buoy_data)
            spot_assessments.append(spot_assessment)

        return cls(spot_assessments)
