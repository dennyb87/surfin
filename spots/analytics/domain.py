import pickle
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

import numpy as np
import pandas as pd
from django.db.models import F, OuterRef
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from cftoscana.domain import CFTBuoyDataDomain
from spots.models import SnapshotAssessment, Spot, SpotSnapshot

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
class TrainOutput:
    spot: str
    rmse: float
    stored: bool
    filename: Optional[str]


@dataclass
class WSS1hPredictor:
    model: "RandomForestRegressor"

    @classmethod
    def initialize(cls, spot_uid: str):
        filename = cls.get_filename(spot_uid=spot_uid)
        with open(filename, "rb") as file:
            model = pickle.load(file)
        return cls(model=model)

    @classmethod
    def get_filename(cls, spot_uid: str):
        return f"{cls.__name__}_{spot_uid}.pkl"

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

    @classmethod
    def train(cls, spot_uid: str, store: bool = False):
        spot = Spot.objects.get(uid=spot_uid)
        timeserie = SpotSnapshotTimeserieV1.build_for_spot(spot, from_date=datetime.min)
        df = pd.DataFrame(snapshot.to_dict() for snapshot in timeserie)
        df.set_index(["created"], inplace=True)
        df.sort_values(by=["created"], inplace=True, ascending=False)
        df.drop(columns=["id"], inplace=True)

        # Separate features and target variable
        X = df.drop(columns=["wave_size_score", "buoy_data"])
        y = df["wave_size_score"]

        # Split into training and testing datasets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train a Random Forest Regressor
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)

        # Predict on the test set
        y_pred = model.predict(X_test)

        # Evaluate the model
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        filename = cls.get_filename(spot_uid)

        if store:
            with open("spot_model.pkl", "wb") as file:
                pickle.dump(model, file)

        return TrainOutput(
            spot=spot_uid,
            rmse=rmse,
            stored=store,
            filename=filename,
        )
