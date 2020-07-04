#!/usr/bin/env python3

import argparse
from logging import getLogger

from common import setup_log, read_csv, render_geojson_point, save_geojson, color_gradient


def _calc_value(price_per_sqm: int, min_price: int = 30, max_price: int = 180) -> int:
    value = min(max(price_per_sqm - min_price, 0) / (max_price - min_price), 1.)
    return round((1 - value) * 9)


def main(avg_city_prices_csv: str, output_geojson: str, headers: bool = False) -> None:
    setup_log()
    log = getLogger()
    log.info(f"Parsing CSV {avg_city_prices_csv} file into {output_geojson} GeoJSON...")
    csv_lines = list(read_csv(avg_city_prices_csv))
    if headers:
        _ = csv_lines.pop(0)
    colors = color_gradient("red", "green", 10)
    points = [render_geojson_point(lat=float(t[3]), lon=float(t[4]),
                                   marker_size="small", marker_color=colors[_calc_value(int(float(t[1])))],
                                   props={"title": t[0],
                                          "offer_count": int(float(t[2])),
                                          "price_per_sqm": f"{round(int(float(t[1])))} zł/m2"})
              for t in csv_lines if t[0]]
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
