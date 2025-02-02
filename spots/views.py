import pandas as pd
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.utils import timezone

from spots.analytics.domain import SpotSnapshotTimeserieV1, WSS1hPredictor
from spots.models import Spot as SpotModel


def spot(request, spot_id):
    return render(request=request, template_name="spots/spot.html")
