import string

import factory
from django.utils import timezone
from factory import fuzzy
from factory.django import DjangoModelFactory

from spots.models import Spot


class SpotFactory(DjangoModelFactory):
    class Meta:
        model = Spot

    name = factory.fuzzy.FuzzyText(
        length=12, prefix="spot", chars=string.ascii_lowercase
    )
    lat = "43.956894"
    lon = "10.165571"
