#!/usr/bin/env python3

import argparse
import json


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Creates update')
    parser.add_argument('output', type=str, help='Output JSON containing update gist requests')
    return parser.parse_args()


def main(output: str):
    with open("offer-map.json", "r") as in_:
        offer_map = json.load(in_)

    with open("data/latest_offers.csv", "r") as f_:
        latest_offers_str = f_.read()

    offer_map_as_json_str = json.dumps(offer_map, ensure_ascii=False)
    with open(output, "w") as out_f:
        json.dump({
            "description": "Map of property offers created in last 10 days",
            "files": {
                "recent_offers.geojson": {
                    "content": offer_map_as_json_str,
                    "filename": "recent_offers.geojson"
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
