#!/usr/bin/env python3

import argparse
import json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Creates update')
    parser.add_argument('output', type=str, help='Output JSON containing update gist requests')
    return parser.parse_args()


def main(output: str):
    with open("parcel-map.json", "r") as in_:
        city_map = json.load(in_)

    with open("offer-map.json", "r") as in_:
        offer_map = json.load(in_)

    with open("data/latest_offers.csv", "r") as f_:
        latest_offers_str = f_.read()

    with open("data/daily_price_avg.csv", "r") as f_:
        daily_price_avg = f_.read()

    city_map_as_json_str = json.dumps(city_map, ensure_ascii=False)
    offer_map_as_json_str = json.dumps(offer_map, ensure_ascii=False)
    with open(output, "w") as out_f:
        json.dump({
            "description": "Map of Wroclaw-centric isochrones together with average price per square meter markers per village",
            "files": {
                "parcel-map.geojson": {
                    "content": city_map_as_json_str,
                    "filename": "parcel-map.geojson"
                },
                "offer-map.geojson": {
                    "content": offer_map_as_json_str,
                    "filename": "offer-map.geojson"
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
    main(args.output)


if __name__ == '__main__':
    cli_main()
