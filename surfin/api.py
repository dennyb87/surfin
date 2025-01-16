from datetime import datetime
from typing import List

import pandas as pd
from ninja import NinjaAPI, Schema
from pydantic import UUID4

from spots.analytics.domain import SpotSnapshotTimeserieV1
from spots.models import Spot as SpotModel

api = NinjaAPI()


class Spot(Schema):
    uid: UUID4
    name: str
    lat: str
    lon: str


class SpotSnapshot(Schema):
    created: datetime
    wave_size_score: float
    wind_direction: float
    wind_speed: float
    wave_height: float
    period: float
    direction: float


@api.get("/spots/", response=List[Spot])
def spots(request):
    return SpotModel.objects.all()


@api.get("/spots/{spot_uid}/timeseries/", response=List[SpotSnapshot])
def timeseries(request, spot_uid: UUID4):
    spot = SpotModel.objects.get(uid=spot_uid)
    timeserie = SpotSnapshotTimeserieV1.build_for_spot(spot)
    df = pd.DataFrame(snapshot.to_dict() for snapshot in timeserie)
    df.drop(["id"], axis=1, inplace=True)
    df.sort_values(by=["created"], inplace=True, ascending=False)
    return df.to_dict(orient="records")
