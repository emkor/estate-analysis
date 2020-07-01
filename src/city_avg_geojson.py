#!/usr/bin/env python3

import argparse
import colorsys
import json
from copy import deepcopy
from logging import getLogger
from typing import List, Any, Dict

from colour import Color

from common import setup_log, read_csv

TEMPLATE_JSON = {
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

COLORS = [(c.hex)[1:] for c in Color("red").range_to(Color("green"), 10)]


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def rgb2hex(r, g, b) -> str:
    return '#%02x%02x%02x' % (r, g, b)


def render_point(city: str, price_per_sqm: int, offer_count: int, lat: float, lon: float) -> Dict[str, Any]:
    point = deepcopy(TEMPLATE_JSON)
    point["geometry"]["coordinates"] = [lon, lat]
    point["properties"]["marker-color"] = COLORS[_calc_value(price_per_sqm)]
    point["properties"]["marker-size"] = "small"
    point["properties"]["title"] = city
    point["properties"]["offer_count"] = offer_count
    point["properties"]["price_per_sqm"] = f"{round(price_per_sqm)} zł/m2"
    return point


def _calc_value(price_per_sqm: int, min_price: int = 30, max_price: int = 180) -> int:
    value = min(max(price_per_sqm - min_price, 0) / (max_price - min_price), 1.)
    return round((1 - value) * 9)


def render_geojson(features: List[Dict[str, Any]], output_file: str) -> None:
    with open(output_file, "w") as f_:
        json.dump({"type": "FeatureCollection", "features": features}, f_, ensure_ascii=False, indent=2)


def main(avg_city_prices_csv: str, output_geojson: str, headers: bool = False) -> None:
    setup_log()
    log = getLogger()
    log.info(f"Parsing CSV {avg_city_prices_csv} file into {output_geojson} GeoJSON...")
    csv_lines = list(read_csv(avg_city_prices_csv))
    if headers:
        _ = csv_lines.pop(0)
    points = [render_point(t[0], int(float(t[1])), int(float(t[2])), float(t[3]), float(t[4]))
              for t in csv_lines if t[0]]
    log.info(f"Rendering GeoJSON out of {len(points)} points...")
    render_geojson(points, output_geojson)
    log.info(f"Done rendering file {output_geojson}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Render average city price CSV file as GeoJON')
    parser.add_argument('input', type=str, help='Path to CSV file with average city prices')
    parser.add_argument('output', type=str, help='Path to output GeoJSON file')
    parser.add_argument('--headers', action='store_true', help='Assume there is a header row in input CSV')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.input, args.output, args.headers)


if __name__ == '__main__':
    cli_main()
