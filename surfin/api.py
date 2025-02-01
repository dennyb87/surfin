from datetime import datetime
from typing import List

import pandas as pd
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ninja import NinjaAPI, Schema
from pydantic import UUID4

from spots.analytics.domain import SpotSnapshotTimeserieV1, WSS1hPredictor
from spots.models import Spot as SpotModel

api = NinjaAPI()


class Spot(Schema):
    uid: UUID4
    name: str
    lat: str
    lon: str


class SpotSnapshot(Schema):
    created: datetime
    wss1h: float
    lag: float
    wave_height: float
    period: float
    direction: float


@api.get("/spots/", response=List[Spot])
def spots(request):
    return SpotModel.objects.all()


@api.get("/spots/{spot_uid}/timeseries/", response=List[SpotSnapshot])
def timeseries(request, spot_uid: UUID4):
    spot = SpotModel.objects.get(uid=spot_uid)
    yesterday = timezone.now() - relativedelta(days=1)
    start_of_day = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    timeserie = SpotSnapshotTimeserieV1.build_for_spot(spot, from_date=start_of_day)

    predictor = WSS1hPredictor.initialize()
    predictions = predictor.predict(timeserie)

    df = pd.DataFrame(prediction.to_dict() for prediction in predictions)
    df.sort_values(by=["created"], inplace=True, ascending=False)

    return df.to_dict(orient="records")
