from datetime import datetime
from typing import List, Optional

import numpy as np
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
    hour: float
    wss1h: Optional[float]
    wave_height: Optional[float]


@api.get("/spots/", response=List[Spot])
def spots(request):
    return SpotModel.objects.all()


@api.get("/spots/{spot_uid}/timeseries/", response=List[SpotSnapshot])
def timeseries(request, spot_uid: UUID4):
    spot = SpotModel.objects.get(uid=spot_uid)
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    timeserie = SpotSnapshotTimeserieV1.build_for_spot(spot, from_date=start_of_day)

    predictor = WSS1hPredictor.initialize(spot_uid=spot_uid)
    predictions = predictor.predict(timeserie)

    # For simplicity always build wave height from latest available data
    try:
        latest_prediction = predictions[-1].snapshot.buoy_data.wave_height
    except IndexError:
        df = pd.DataFrame({"x": [], "y": [], "unit": []})
    else:
        df = pd.DataFrame(latest_prediction)

    df["hour"] = df.x
    df.drop(columns=["x", "unit"], inplace=True)
    df.rename(columns={"y": "wave_height"}, inplace=True)

    daydf = pd.DataFrame({"hour": np.arange(0.0, 24.5, 0.5)})
    daydf = pd.merge_asof(daydf, df, on=["hour"])

    wssdf = pd.DataFrame(p.to_dict() for p in predictions)
    if not wssdf.empty:
        wssdf["hour"] = wssdf.created.apply(
            lambda dt: round(dt.hour + (dt.minute / 60), 1)
        )
        wssdf["wss1h"] = wssdf.wss1h.shift(periods=2)
    else:
        wssdf = pd.DataFrame({"wss1h": [], "hour": []})

    daydf = daydf.merge(wssdf[["hour", "wss1h"]], on=["hour"], how="outer")
    daydf.replace({np.nan: None}, inplace=True)
    return daydf.to_dict(orient="records")
