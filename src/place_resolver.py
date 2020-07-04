from collections import OrderedDict
from copy import copy
from functools import partial
from logging import Logger
from threading import RLock
from typing import Dict, Any, Optional, List
from urllib import parse
import requests

from common import read_csv, write_csv
from model import Place, ParcelOffer


class MapQuestClient:
    BASE_API_URL_FMT = "http://open.mapquestapi.com/nominatim/v1/search.php?format=json&addressdetails=1&limit=1&countrycodes=PL&key={}&q={}"

    def __init__(self, api_key: str, log: Logger):
        self.api_key = api_key
        self.log = log

    def resolve(self, query_address: str, location: str) -> Place:
        resolve_url = self.BASE_API_URL_FMT.format(self.api_key, parse.quote(copy(query_address)))
        r = requests.get(url=resolve_url)
        if r.ok:
            json_resp = r.json()
            if len(json_resp):
                return self._parse(location, json_resp)
            else:
                self.log.warning(f"No response for {query_address}: {r.status_code} {r.content}")
                return Place(location, None, None, None, None)
        else:
            self.log.warning(f"MapQuest returned error for query {query_address}: {r.status_code} {r.content}")
            return Place(location, None, None, None, None)

    def _parse(self, location: str, json_resp: Dict[str, Any]) -> Place:
        return Place(location=location, city=json_resp[0].get("address", {}).get("city", None),
                     postcode=json_resp[0].get("address", {}).get("postcode", None), lat=float(json_resp[0]["lat"]),
                     lon=float(json_resp[0]["lon"]))


class PlaceResolver:
    def __init__(self, map_quest_client: MapQuestClient, log: Logger):
        self.client = map_quest_client
        self.log = log
        self._cache_lock = RLock()
        self.cache: Dict[str, Optional[Place]] = {}

    def load(self, csv_cache):
        with self._cache_lock:
            for line in read_csv(csv_cache):
                self.cache[line[0]] = Place.from_csv_row(line)

    def save(self, csv_cache):
        with self._cache_lock:
            row_gen = [r.to_csv_row() for r in self.cache.values() if r]
            row_gen.sort(key=lambda r: r[0])
            write_csv(csv_cache, row_gen)

    def get(self, offer: ParcelOffer) -> Optional[Place]:
        with self._cache_lock:
            if offer.location in self.cache:
                return self.cache.get(offer.location)
            else:
                address = build_resolve_name(offer.domain, offer.location)
                if address != offer.location:
                    self.log.info(f"Resolving {offer.location} -> {address}")
                resolved = self.client.resolve(address, offer.location)
                self.cache[offer.location] = resolved
                return resolved


def build_resolve_name(domain: str, location: str) -> str:
    name_parts: List[str] = [p.strip() for p in location.split(",") if p.strip()]
    condition = partial(lambda p: not p.lower().startswith("ul.")
                                  and not p.lower().startswith("ul ")
                                  and not p.lower().startswith("ulica ")
                                  and not p.lower().startswith("al.")
                                  and not p.lower().startswith("al ")
                                  and not p.lower().startswith("aleja ")
                                  and not p.lower().startswith("ok.")
                                  and not p.lower().startswith("ok ")
                                  and not p.lower().startswith("okolice")
                                  and not p.lower().startswith("miasto ")
                                  and not p.lower().startswith("gmina ")
                                  and not p.lower().startswith("gm.")
                        )
    name_parts_wout_street = list(filter(condition, name_parts))
    name_parts_wout_dupl = list(OrderedDict.fromkeys(name_parts_wout_street))

    if name_parts_wout_dupl[0].lower().startswith("dolnośląski") \
            or name_parts_wout_dupl[0].lower().startswith("wielkopolski"):
        name_parts_wout_dupl = name_parts_wout_dupl[::-1]
    if name_parts_wout_dupl[-1].lower().startswith("dolnośląski") \
            or name_parts_wout_dupl[-1].lower().startswith("wielkopolski"):
        name_parts_wout_dupl = name_parts_wout_dupl[:-1]

    if domain == "www.morizon.pl":
        if len(name_parts_wout_dupl) > 2 and name_parts_wout_dupl[2] in name_parts_wout_dupl[1]:
            name_parts_wout_dupl[1] = name_parts_wout_dupl[1].replace(name_parts_wout_dupl[2], "").strip()

    if len(name_parts_wout_dupl) > 2:
        name_parts_wout_dupl = name_parts_wout_dupl[1:]

    return ", ".join(name_parts_wout_dupl)
