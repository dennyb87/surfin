from typing import List, Optional

import numpy as np
import pandas as pd
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
    direction: Optional[float]
    period: Optional[float]


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
        latest_buoy_data = predictions[-1].snapshot.buoy_data
    except IndexError:
        df = pd.DataFrame({"x": [], "y": [], "unit": []})
        dir_df = pd.DataFrame({"x": [], "y": [], "unit": []})
        period_df = pd.DataFrame({"x": [], "y": [], "unit": []})
    else:
        df = pd.DataFrame(latest_buoy_data.wave_height.to_dict())
        dir_df = pd.DataFrame(latest_buoy_data.direction.to_dict())
        period_df = pd.DataFrame(latest_buoy_data.period.to_dict())

    df["hour"] = df.x
    df.drop(columns=["x", "unit"], inplace=True)

    dir_df["hour"] = dir_df.x
    dir_df.drop(columns=["x", "unit"], inplace=True)
    dir_df.rename(columns={"y": "direction"}, inplace=True)

    period_df["hour"] = period_df.x
    period_df.drop(columns=["x", "unit"], inplace=True)
    period_df.rename(columns={"y": "period"}, inplace=True)

    df = pd.merge_asof(df, dir_df, on="hour", tolerance=0.5, direction="nearest")
    df = pd.merge_asof(df, period_df, on="hour", tolerance=0.5, direction="nearest")

    df.rename(columns={"y": "wave_height"}, inplace=True)

    daydf = pd.DataFrame({"hour": np.arange(0.0, 24.5, 0.5)})
    daydf = pd.merge_asof(daydf, df, on=["hour"], tolerance=0.5, direction="nearest")
    wssdf = pd.DataFrame(p.to_dict() for p in predictions)
    if not wssdf.empty:
        wssdf["hour"] = wssdf.created.apply(
            lambda dt: round(dt.hour + (dt.minute / 60), 1)
        )
        wssdf = wssdf[["hour", "wss1h"]]
    else:
        wssdf = pd.DataFrame({"wss1h": [], "hour": []})
    daydf = daydf.merge(wssdf[["hour", "wss1h"]], on=["hour"], how="outer")
    daydf["wss1h"] = daydf.wss1h.shift(periods=2)
    daydf.replace({np.nan: None}, inplace=True)
    return daydf.to_dict(orient="records")
