import argparse
import codecs
import json
from logging import getLogger
from typing import List, Any, Dict, Optional

from shapely.geometry import shape, Point, Polygon

from common import setup_log, read_csv, write_csv
from model import Place


def _build_polygons(isochrone_map: Dict[str, Any]) -> List[Polygon]:
    return [shape(feature['geometry']) for feature in isochrone_map["features"]]


def _index_of_polygon_point_is_in(lat: float, lon: float, polygons: List[shape]) -> int:
    for i, polygon in enumerate(polygons):
        if polygon.contains(Point(lon, lat)):
            return i
    return -1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Merges base isochrone map with given additional GeoJSON features')
    parser.add_argument('isochrone', type=str, help='Path to isochrone map')
    parser.add_argument('place_cache', type=str, help='Path to places cache CSV file')
    parser.add_argument('output', type=str, help='Path output CSV file')
    return parser.parse_args()


def main(isochrone: str, place_cache: str, output: str, polygon_step_time_min: int = 7):
    setup_log()
    log = getLogger()

    log.info(f"Reading isochrone map from {isochrone} ...")
    with codecs.open(isochrone, 'r', 'utf-8-sig') as map_:
        isochrone_map = json.load(map_)
    polygons = _build_polygons(isochrone_map)

    log.info(f"Reading places cache from {place_cache} ...")
    places = filter(None, map(Place.from_csv_row, read_csv(place_cache)))
    city_to_time_to_wroclaw: Dict[str, Optional[int]] = {}

    log.info(f"Finding time to reach destination for places...")
    for p in places:
        if p not in city_to_time_to_wroclaw.keys():
            index = _index_of_polygon_point_is_in(p.lat, p.lon, polygons)
            if index != -1:
                time_to_wroclaw_min = index * polygon_step_time_min
                city_to_time_to_wroclaw[p.city] = time_to_wroclaw_min
            else:
                city_to_time_to_wroclaw[p.city] = None

    log.info(f"Writing {len(city_to_time_to_wroclaw)} results to {output} ...")
    write_csv(output, sorted([[k, v] for k, v in city_to_time_to_wroclaw.items()]))
    log.info("Done")


def cli_main():
    args = _parse_args()
    main(args.isochrone, args.place_cache, args.output)


if __name__ == '__main__':
    cli_main()
