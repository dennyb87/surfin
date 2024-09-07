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


class MeteoNetworkStation(AbstractDataSource):
    id: str

    d = {
        "observation_time_local": "2024-09-07 23:47:00",
        "observation_time_utc": "2024-09-07 21:47:00",
        "station_code": "tsc069",
        "place": "Viareggio",
        "area": "quartiere Marco Polo",
        "latitude": "43.8913485567997",
        "longitude": "10.2376549254404",
        "altitude": 10,
        "country": "IT",
        "region_name": "Toscana",
        "temperature": "24.9",
        "smlp": "1013.4",
        "rh": "82",
        "wind_speed": "0.00",
        "wind_direction": "ENE",
        "wind_direction_degree": "70",
        "wind_gust": "27.40",
        "rain_rate": "0.0",
        "daily_rain": "0.0",
        "dew_point": "21.7",
        "rad": None,
        "uv": None,
        "current_tmin": "18.9",
        "current_tmed": "25.1",
        "current_tmax": "31.1",
        "current_rhmin": "55",
        "current_rhmed": "73",
        "current_rhmax": "84",
        "current_wgustmax": "27.4",
        "current_wspeedmax": "17.7",
        "current_wspeedmed": "2.6",
        "current_uvmed": None,
        "current_uvmax": None,
        "current_radmed": None,
        "current_radmax": None,
        "name": "Viareggio - quartiere Marco Polo",
    }


class Webcam(AbstractDataSource):
    pass


@dataclass
class Spot:
    id: str
    name: str
    data_sources: List["AbstractDataSource"]


class Spots(Enum):
    FORTE_DEI_MARMI_PONTILE = Spot(
        id="111", name="Pontile Forte dei Marmi", data_sources=[BuoyStation()]
    )

    @classmethod
    def get_data_sources(cls) -> List["AbstractDataSource"]:
        # Should grab all unique data sources
        # but for now there's only one spot so...
        return Spots.FORTE_DEI_MARMI_PONTILE.value.data_sources
