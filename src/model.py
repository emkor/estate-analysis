from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, Optional, List
from urllib.parse import urlparse


class Model:
    @classmethod
    def from_csv_row(cls, row: List[str]) -> Optional['Model']:
        raise NotImplementedError

    def to_csv_row(self) -> List[str]:
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> Optional['Model']:
        raise NotImplementedError

    def to_json(self) -> Dict[str, Any]:
        raise NotImplementedError


class ParcelOffer(Model):
    def __init__(self, timestamp: datetime, ident: str, url: str, location: str, area_m2: float, price_pln: float,
                 title: str) -> None:
        self.timestamp = timestamp.replace(microsecond=0)
        self.ident = ident
        self.url = url
        self.location = location
        self.area_m2 = area_m2
        self.price_pln = price_pln
        self.title = title

    def __repr__(self):
        return f"{self.__class__.__name__}({self.ident}, {self.timestamp}, {self.url}, {self.location}, {self.area_m2}, {self.price_pln}, {self.title})"

    def __str__(self):
        return f"{self.__class__.__name__}({self.domain}, {self.ident}, {self.location}, {self.timestamp})"

    @property
    def domain(self) -> str:
        return urlparse(self.url).hostname

    def __hash__(self):
        return hash((self.ident, self.domain))

    def __eq__(self, other: 'ParcelOffer'):
        return self.ident == other.ident and self.domain == other.domain

    def to_csv_row(self) -> List[str]:
        return [self.timestamp.date().isoformat(), self.timestamp.time().isoformat(),
                self.domain, self.ident, self.area_m2, self.price_pln, self.location, self.url, self.title]

    @classmethod
    def from_csv_row(cls, cells: List[str]) -> Optional['ParcelOffer']:
        try:
            if len(cells) == 9:
                timestamp = datetime.fromisoformat(f"{cells[0]}T{cells[1]}")
                return cls(timestamp, ident=cells[3], url=cells[7], location=cells[6],
                           area_m2=int(cells[4]), price_pln=int(cells[5]), title=cells[8])
            else:
                return None
        except (TypeError, ValueError, LookupError):
            return None

    def to_json(self) -> Dict[str, Any]:
        json_dict = deepcopy(self.__dict__)
        json_dict["timestamp"] = json_dict["timestamp"].isoformat()
        return json_dict

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> Optional['ParcelOffer']:
        try:
            json_dict["timestamp"] = datetime.fromisoformat(json_dict["timestamp"])
            return cls(**json_dict)
        except (TypeError, ValueError, LookupError):
            return None


class Place(Model):
    def __init__(self, location: str, city: Optional[str], postcode: Optional[str], lat: Optional[float],
                 lon: Optional[float]):
        self.location = location
        self.city = city
        self.postcode = postcode
        self.lat = lat
        self.lon = lon

    def __hash__(self):
        return hash(self.location)

    def __eq__(self, other: 'Place'):
        return self.location == other.location

    def __repr__(self):
        return f"{self.__class__.__name__}({self.location}, {self.city}, {self.lat}, {self.lon})"

    def __str__(self):
        return f"{self.__class__.__name__}({self.location}, {self.city}, {self.postcode}, {round(self.lat, 3)}, {round(self.lon, 3)})"

    def to_json(self) -> Dict[str, Any]:
        return deepcopy(self.__dict__)

    @classmethod
    def from_json(cls, json_dict: Dict[str, Any]) -> Optional['Place']:
        try:
            return cls(**json_dict)
        except (TypeError, ValueError):
            return None

    def to_csv_row(self) -> List[str]:
        return [self.location, self.city, self.postcode, self.lat, self.lon]

    @classmethod
    def from_csv_row(cls, row: List[str]) -> Optional['Place']:
        try:
            return Place(*row) if len(row) == 5 else None
        except (TypeError, ValueError):
            return None
