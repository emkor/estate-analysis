#!/usr/bin/env python3

import argparse
import codecs
import json
import logging
from os import path
from typing import Any, Dict

from colour import Color

from common import setup_log


def _read_isochrone_map(map_path: str, narrowest_color: str = "green", broadest_color: str = "red") -> Dict[str, Any]:
    with codecs.open(map_path, 'r', 'utf-8-sig') as map_:
        map_path = json.load(map_)
    polygon_count = len(map_path["features"])
    colors = [c.hex for c in Color(narrowest_color).range_to(Color(broadest_color), polygon_count)]
    for f, c in zip(map_path["features"], colors):
        f["properties"]["fill"] = colors[0]
        f["properties"]["fill-opacity"] = 0.04
        f["properties"]["stroke"] = c
        f["properties"]["stroke-opacity"] = 0.8
    return map_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Merges base isochrone map with given additional GeoJSON features')
    parser.add_argument('base', type=str, help='Path to base isochrone map from maps.openrouteservice.org')
    parser.add_argument('tgt', type=str, help='Path where to store rendered map')
    parser.add_argument('layers', nargs='+', help='Paths to more GeoJSON files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable more verbose logging')
    return parser.parse_args()


def main(tgt_map: str, isochrone_map: str, debug: bool, *layers_files) -> None:
    setup_log(logging.DEBUG if debug else logging.INFO)
    log = logging.getLogger("estate")

    base_map = _read_isochrone_map(isochrone_map)

    log.info(f"Applying {len(layers_files)} layers on top of {isochrone_map}")
    for lf in layers_files:
        lf = path.abspath(lf)
        if path.isfile(lf):
            with open(lf, "r") as lf_:
                layer_map = json.load(lf_)
            base_map["features"].extend(layer_map["features"])
        else:
            log.warning(f"GeoJSON file {lf} does not exist, omitting the layer")

    log.info(f"Writing final map at {tgt_map}")
    with open(tgt_map, "w") as tgt:
        json.dump(base_map, tgt, ensure_ascii=False, indent=2)

    log.info(f"Done writing final map at {tgt_map}")


def cli_main():
    args = _parse_args()
    print(args)
    main(args.tgt, args.base, args.verbose, *tuple(args.layers))


if __name__ == '__main__':
    cli_main()
