import string

import factory
from django.utils import timezone
from factory import fuzzy
from factory.django import DjangoModelFactory

from ipcamlive.models import IPCamLiveWebcam
from spots.tests.factories import SpotFactory


class IPCamLiveWebcamFactory(DjangoModelFactory):
    class Meta:
        model = IPCamLiveWebcam

    alias = factory.fuzzy.FuzzyText(
        length=16, prefix="alias", chars=string.ascii_lowercase
    )
    name = factory.fuzzy.FuzzyText(
        length=16, prefix="webcam", chars=string.ascii_lowercase
    )
    spot = factory.SubFactory(SpotFactory)
