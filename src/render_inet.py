import argparse
from logging import getLogger

from common import read_csv, render_geojson_point, setup_log, save_geojson, color_gradient, randomize_coordinates


def calc_class(avg_bandwidth: float, avg_bw_lower_bound: float = 4., avg_bw_upper_bound: int = 64.,
               classes: int = 4) -> int:
    # value = min(max(avg_bandwidth - avg_bw_lower_bound, 0) / (avg_bw_upper_bound - avg_bw_lower_bound), 1.)
    # return round(value * classes)
    if avg_bandwidth < 8.:
        return 0
    elif avg_bandwidth < 25.:
        return 1
    else:
        return 2


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Render UKE POPC data into GeoJSON map layer')
    parser.add_argument('input', type=str, help='Path to UKE POPC CSV file')
    parser.add_argument('output', type=str, help='Path where to store rendered map')
    return parser.parse_args()


def main(broadband_city_csv: str, geojson: str):
    setup_log()
    log = getLogger()
    colors = color_gradient("#737373", "#F2F2F2", 3)
    points = []
    for i, cells in enumerate(read_csv(broadband_city_csv)):
        if i == 0 or not cells:
            continue
        try:
            city, ap_count = cells[0], int(cells[1])
            min_bw, avg_bw, max_bw = int(cells[2]), float(cells[3]), int(cells[4])
            lat, lon = randomize_coordinates(float(cells[5]), float(cells[6]), delta=0.004)
            color_class = calc_class(avg_bandwidth=avg_bw) if max_bw < 100 else 2
            point = render_geojson_point(lat=lat, lon=lon, marker_color=colors[color_class], marker_symbol='star',
                                         props={'title': city,
                                                'min-bandwidth': min_bw,
                                                'avg-bandwidth': avg_bw,
                                                'max-bandwidth': max_bw,
                                                'bandwidth-class': color_class})
            points.append(point)
        except (TypeError, ValueError, LookupError) as e:
            log.warning(f"Could not parse: {e}, cells: {cells}")
    if points:
        save_geojson(points, geojson)


if __name__ == '__main__':
    args = _parse_args()
    main(broadband_city_csv=args.input, geojson=args.output)
