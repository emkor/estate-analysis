#!/usr/bin/env python3

import argparse
import json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Creates update')
    parser.add_argument('input', type=str, help='JSON file to be wrapped into update gist request')
    parser.add_argument('output', type=str, help='Output JSON containing update gist requests')
    return parser.parse_args()


def main(input: str, output: str):
    with open(input, "r") as in_:
        input_map = json.load(in_)

    with open("data/latest_offers.csv", "r") as f_:
        latest_offers_str = f_.read()

    with open("data/daily_price_avg.csv", "r") as f_:
        daily_price_avg = f_.read()

    map_as_json_str = json.dumps(input_map, ensure_ascii=False)
    with open(output, "w") as out_f:
        json.dump({
            "description": "Map of Wroclaw-centric isochrones together with average price per square meter markers per village",
            "files": {
                "parcel-map.geojson": {
                    "content": map_as_json_str,
                    "filename": "parcel-map.geojson"
                },
                "daily_price_avg.csv": {
                    "content": daily_price_avg,
                    "filename": "daily_price_avg.csv"
                },
                "latest_offers.csv": {
                    "content": latest_offers_str,
                    "filename": "latest_offers.csv"
                }
            }
        }, out_f, ensure_ascii=False)


def cli_main():
    args = _parse_args()
    main(args.input, args.output)


if __name__ == '__main__':
    cli_main()
