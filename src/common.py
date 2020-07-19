import csv
import json
import logging
import os
import time
from copy import deepcopy
from os import path
from typing import Generator, List, Iterable, Dict, Any

from colour import Color
from more_itertools import chunked

GEOJSON_POINT_TEMPLATE = {
    "type": "Feature",
    "geometry": {
        "type": "Point",
        "coordinates": [0., 0.]
    },
    "properties": {
        "marker-symbol": "bank",
        "marker-color": "PLACEHOLDER",
        "title": "PLACEHOLDER",
        "price_per_sqm": "PLACEHOLDER"
    }
}


def render_geojson_point(lat: float, lon: float, marker_size: str = "small", marker_color: str = "",
                         marker_symbol: str = "bank", props: Dict[str, Any] = None) -> Dict[str, Any]:
    point = deepcopy(GEOJSON_POINT_TEMPLATE)
    point["geometry"]["coordinates"] = [lon, lat]
    point["properties"]["marker-color"] = marker_color
    point["properties"]["marker-size"] = marker_size
    point["properties"]["marker-symbol"] = marker_symbol
    point["properties"].update(props)
    return point


def save_geojson(features: List[Dict[str, Any]], output_file: str) -> None:
    with open(output_file, "w") as f_:
        json.dump({"type": "FeatureCollection", "features": features}, f_, ensure_ascii=False, indent=2)


def color_gradient(start_color: str, end_color: str, count: int) -> List[str]:
    return [c.hex for c in Color(start_color).range_to(Color(end_color), count)]


def setup_log(level: int = logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s.%(msecs)03d|%(levelname)-7s| %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S")
    logging.Formatter.converter = time.gmtime


def abs_path(rel_proj_path: str) -> str:
    dir_path = path.dirname(path.realpath(__file__)).partition("estate-analysis")
    return path.join(dir_path[0], dir_path[1], rel_proj_path)


def list_csv_files(dir_path: str) -> List[str]:
    return sorted([path.join(dir_path, f) for f in os.listdir(dir_path)
                   if path.isfile(path.join(dir_path, f))
                   and path.splitext(f)[-1].lower() == ".csv"])


def read_csv(csv_file: str, delimiter: str = ',') -> Generator[List[str], None, None]:
    with open(csv_file, "r") as csv_f:
        for line in csv.reader(csv_f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL):
            if line:
                yield line


def write_csv(csv_file: str, rows: Iterable[List[str]], delimiter: str = ','):
    with open(csv_file, "w") as csv_f:
        writer = csv.writer(csv_f, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for line in chunked(rows, 20):
            writer.writerows(line)
