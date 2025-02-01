import pickle
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

import pandas as pd
from django.db.models import F, OuterRef

from cftoscana.domain import CFTBuoyDataDomain
from spots.models import SnapshotAssessment, SpotSnapshot

if TYPE_CHECKING:
    from sklearn.ensemble import RandomForestRegressor

    from spots.domain import SpotDomain


@dataclass
class SpotSnapshotV1:
    id: int
    created: datetime
    buoy_data: "CFTBuoyDataDomain"

    wave_size_score: Decimal

    wind_direction: Decimal
    wind_speed: Decimal

    wave_height_lag_0: float
    wave_height_lag_1: float
    wave_height_lag_2: float

    period_lag_0: float
    period_lag_1: float
    period_lag_2: float

    direction_lag_0: float
    direction_lag_1: float
    direction_lag_2: float

    @classmethod
    def from_orm(cls, snapshot: "SpotSnapshot"):
        buoy = CFTBuoyDataDomain.load_for_snapshot(snapshot)
        return cls(
            id=snapshot.pk,
            created=snapshot.created,
            buoy_data=buoy,
            wave_size_score=snapshot.wave_size_score,
            wind_direction=snapshot.wind_direction,
            wind_speed=snapshot.wind_speed,
            wave_height_lag_0=buoy.get_wave_height(hours_lag=0),
            wave_height_lag_1=buoy.get_wave_height(hours_lag=1),
            wave_height_lag_2=buoy.get_wave_height(hours_lag=2),
            period_lag_0=buoy.get_period(hours_lag=0),
            period_lag_1=buoy.get_period(hours_lag=1),
            period_lag_2=buoy.get_period(hours_lag=2),
            direction_lag_0=buoy.get_direction(hours_lag=0),
            direction_lag_1=buoy.get_direction(hours_lag=1),
            direction_lag_2=buoy.get_direction(hours_lag=2),
        )

    def to_dict(self):
        return asdict(self)


class SpotSnapshotTimeserieV1(list["SpotSnapshotV1"]):
    @classmethod
    def build_for_spot(
        cls, spot: "SpotDomain", from_date: datetime
    ) -> "SpotSnapshotTimeserieV1":
        snapshots = SpotSnapshot.objects.filter(
            spot_id=spot.pk, created__gte=from_date
        ).annotate(
            wind_direction=F("meteonetworkirtdata__wind_direction"),
            wind_speed=F("meteonetworkirtdata__wind_speed"),
            wave_size_score=SnapshotAssessment.objects.filter(
                snapshot=OuterRef("id")
            ).values("wave_size_score"),
        )

        spot_assessments = []

        for snapshot in snapshots:
            spot_assessment = SpotSnapshotV1.from_orm(snapshot)
            spot_assessments.append(spot_assessment)

        return cls(spot_assessments)


@dataclass
class SpotWSS1hPrediction:
    snapshot: "SpotSnapshotV1"
    wss1h: float

    @classmethod
    def from_data(
        cls, snapshot: "SpotSnapshotV1", wss1h: float
    ) -> "SpotWSS1hPrediction":
        return cls(
            snapshot=snapshot,
            wss1h=wss1h,
        )

    def to_dict(self):
        return {
            "created": self.snapshot.created,
            "wss1h": self.wss1h,
            "wave_height": self.snapshot.wave_height_lag_0,
            "period": self.snapshot.period_lag_0,
            "direction": self.snapshot.direction_lag_0,
            "lag": self.snapshot.buoy_data.data_delay.seconds / 3600,
        }


@dataclass
class WSS1hPredictor:
    model: "RandomForestRegressor"

    @classmethod
    def initialize(cls):
        with open("spot_model.pkl", "rb") as file:
            model = pickle.load(file)
        return cls(model=model)

    def predict(self, snapshots: "list[SpotSnapshotV1]") -> "list[SpotWSS1hPrediction]":
        wss1h_snapshots = []
        for snapshot in snapshots:
            data = snapshot.to_dict()
            df = pd.DataFrame([data])
            df.drop(
                columns=["id", "created", "wave_size_score", "buoy_data"], inplace=True
            )
            prediction = self.model.predict(df)
            wss1h = prediction[0]
            spot_wss1h = SpotWSS1hPrediction.from_data(snapshot, wss1h=wss1h)
            wss1h_snapshots.append(spot_wss1h)
        return wss1h_snapshots
