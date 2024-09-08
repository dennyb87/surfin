from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List

from meteonetwork_api.client import MeteoNetworkClient

from surfin import settings


class AbstractDataSource(ABC):
    @property
    def requires_spot(self):
        pass

    @abstractmethod
    def collect(self):
        pass

    @abstractmethod
    def store(self):
        pass


@dataclass
class BuoyStation(AbstractDataSource):
    uid: str

    def collect(self):
        pass

    def store(self):
        pass


@dataclass
class MeteoNetworkIRTDomain(AbstractDataSource):
    """Interpolated Real Time"""

    location: "Location"

    def fetch(self):
        client = MeteoNetworkClient(access_token=settings.METEONETWORK_API_TOKEN)
        return client.interpolated_real_time_data(
            lat=self.location.lat, lon=self.location.lon
        )

    def collect(self):
        data = self.fetch()
        return self.store(data)

    def store(self, data):
        # MeteoNetworkIRT.objects.create()
        return data


class Webcam(AbstractDataSource):
    pass


@dataclass
class Location:
    name: str
    lat: str
    lon: str


class Locations(Enum):
    FORTE_DEI_MARMI_PONTILE = Location(
        name="Pontile Forte dei Marmi",
        lat="43.956894",
        lon="10.165571",
    )


@dataclass
class Spot:
    location: "Location"
    data_sources: List["AbstractDataSource"]

    def load_dataframe(self):
        for source in self.data_sources:
            data = source.load_dataframe()


class Spots(Enum):
    FORTE_DEI_MARMI_PONTILE = Spot(
        location=Locations.FORTE_DEI_MARMI_PONTILE.value,
        data_sources=[
            MeteoNetworkIRTDomain(location=Locations.FORTE_DEI_MARMI_PONTILE.value),
            BuoyStation(uid="T01"),
        ],
    )

    @classmethod
    def get_data_sources(cls) -> List["AbstractDataSource"]:
        sources = []
        for spot in cls:
            for source in spot.value.data_sources:
                if source not in sources:
                    sources.append(source)
        return sources
