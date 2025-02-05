import string
from uuid import uuid4

import factory
from factory.django import DjangoModelFactory

from spots.models import Spot


class SpotFactory(DjangoModelFactory):
    class Meta:
        model = Spot

    uid = factory.LazyAttribute(lambda x: uuid4())
    name = factory.fuzzy.FuzzyText(
        length=12, prefix="spot", chars=string.ascii_lowercase
    )
    lat = "43.956894"
    lon = "10.165571"
