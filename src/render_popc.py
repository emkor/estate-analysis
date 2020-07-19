import argparse
from datetime import datetime
from logging import getLogger

from common import read_csv, render_geojson_point, setup_log, save_geojson


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Render UKE POPC data into GeoJSON map layer')
    parser.add_argument('input', type=str, help='Path to UKE POPC CSV file')
    parser.add_argument('output', type=str, help='Path where to store rendered map')
    return parser.parse_args()


def main(popc_csv: str, geojson: str):
    setup_log()
    log = getLogger()
    points = []
    seen_streets = set()

    for i, cells in enumerate(read_csv(popc_csv, delimiter=';')):
        if i == 0:
            continue
        try:
            lat, lon = float(cells[19].replace(',', '.').strip()), float(cells[18].replace(',', '.').strip())
            completion = datetime.strptime(cells[4].strip(), "%Y%m%d").date().strftime("%Y-%m-%d")
            address = ", ".join((cells[12], cells[14]))
            if address not in seen_streets:
                seen_streets.add(address)
                medium, speed, vendor = cells[3].strip(), float(cells[5].replace(',', '.').strip()), cells[1].strip()
                point = render_geojson_point(lat=lat, lon=lon, marker_color='#11ee11', marker_symbol='star',
                                             props={'title': '',
                                                    'address': address,
                                                    'date': completion,
                                                    'vendor': vendor,
                                                    'medium': f"{medium}, {speed} Mbps"})
                points.append(point)
        except (TypeError, ValueError, LookupError) as e:
            log.warning(f"Could not parse: {e} cells: {cells}")
    if points:
        save_geojson(points, geojson)


if __name__ == '__main__':
    # args = _parse_args()
    main("/home/mat/proj/estate-analysis/data/uke_olawski/0215_POPC.csv",
         "/home/mat/proj/estate-analysis/data/uke_olawski/0215_POPC.json")
