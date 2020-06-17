#!/usr/bin/env python3
import csv
import json
from logging import getLogger
from typing import List

from common import setup_log
from model import Place


def convert_place_cache_from_json_to_csv(json_cache: str, csv_cache: str):
    setup_log()
    log = getLogger()
    with open(json_cache, "r") as pc:
        cache = json.load(pc)
    places: List[Place] = []
    for _, place in cache.items():
        p = Place.from_json(place)
        if p:
            places.append(p)
        else:
            log.warning(f"Could not parse into place: {place}")
    rows = []
    for p in places:
        csv_row = p.to_csv_row()
        rows.append(csv_row)
    with open(csv_cache, "w") as csv_f:
        place_writer = csv.writer(csv_f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for r in rows:
            place_writer.writerow(r)


if __name__ == '__main__':
    convert_place_cache_from_json_to_csv("../place_cache.json", "../place_cache.csv")
