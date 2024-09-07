from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List


class AbstractDataSource(ABC):
    @abstractmethod
    def take_snapshot(self):
        pass

class BuoyStation(AbstractDataSource):
    def take_snapshot(self):
        pass

class WeatherStation(AbstractDataSource):
    pass

class Webcam(AbstractDataSource):
    pass


@dataclass
class Spot:
    id: str
    name: str
    data_sources: List["AbstractDataSource"]


class Spots(Enum):
    FORTE_DEI_MARMI_PONTILE = Spot(id="111", name="Pontile Forte dei Marmi", data_sources=[BuoyStation()])

    @classmethod
    def get_data_sources(cls) -> List["AbstractDataSource"]:
        # Should grab all unique data sources
        # but for now there's only one spot so...
        return Spots.FORTE_DEI_MARMI_PONTILE.value.data_sources
