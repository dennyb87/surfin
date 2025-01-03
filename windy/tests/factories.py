import string

import factory
from django.utils import timezone
from factory import fuzzy
from factory.django import DjangoModelFactory

from spots.tests.factories import SpotFactory
from windy.models import WindyWebcam


class WindyWebcamFactory(DjangoModelFactory):
    class Meta:
        model = WindyWebcam

    windy_uid = factory.fuzzy.FuzzyInteger(10000, 99999)
    name = factory.fuzzy.FuzzyText(
        length=24, prefix="windy_webcam", chars=string.ascii_lowercase
    )
    spot = factory.SubFactory(SpotFactory)
