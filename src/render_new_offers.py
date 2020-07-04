#!/usr/bin/env python3

import argparse
from logging import getLogger, Logger
from random import uniform
from typing import List, Any, Dict, Tuple, Optional

from common import setup_log, read_csv, render_geojson_point, save_geojson, color_gradient


def _calc_value(price_per_sqm: int, min_price: int = 30, max_price: int = 180) -> int:
    value = min(max(price_per_sqm - min_price, 0) / (max_price - min_price), 1.)
    return round((1 - value) * 9)


def randomize_coordinates(lat: float, lon: float, delta: float = 0.006) -> Tuple[float, float]:
    lat_positive_delta = uniform(delta / 3, delta)
    lat_negative_delta = uniform(-1 * delta / 3, -1 * delta)
    lon_positive_delta = uniform(delta / 3, delta)
    lon_negative_delta = uniform(-1 * delta / 3, -1 * delta)
    selector = uniform(0, 1)
    if selector <= 0.25:
        return lat + lat_negative_delta, lon + lon_negative_delta
    elif selector <= 0.5:
        return lat + lat_negative_delta, lon + lon_positive_delta
    elif selector <= 0.75:
        return lat + lat_positive_delta, lon + lon_negative_delta
    else:
        return lat + lat_positive_delta, lon + lon_positive_delta


def row_to_point(row: List[str], colors: List[str], log: Logger) -> Optional[Dict[str, Any]]:
    try:
        offer_age_days = int(row[0])
        price_per_sqm = round(float(row[3]))
        marker_color = colors[_calc_value(price_per_sqm, max_price=150)]
        lat, lon = randomize_coordinates(float(row[9]), float(row[10]))
        return render_geojson_point(lat=lat, lon=lon,
                                    marker_size="large" if offer_age_days <= 2 else "small",
                                    marker_color=marker_color,
                                    props={"title": row[2], "url": row[8], "age": offer_age_days,
                                           "area": round(float(row[4])), "city": row[1],
                                           "price_per_sqm": f"{price_per_sqm} zł/m2"})
    except (LookupError, ValueError, TypeError) as e:
        log.warning(f"Could not render CSV row {row} as GeoJSON: {e}")
        return None


def main(avg_city_prices_csv: str, output_geojson: str, headers: bool = False) -> None:
    setup_log()
    log = getLogger()
    log.info(f"Parsing CSV {avg_city_prices_csv} file into {output_geojson} GeoJSON...")
    csv_lines = list(read_csv(avg_city_prices_csv))
    if headers:
        _ = csv_lines.pop(0)
    colors = color_gradient("red", "green", 10)
    points = list(filter(None, [row_to_point(t, colors, log) for t in csv_lines if t[0]]))
    log.info(f"Rendering GeoJSON out of {len(points)} points...")
    save_geojson(points, output_geojson)
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
