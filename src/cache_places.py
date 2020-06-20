#!/usr/bin/env python3

import argparse
from logging import getLogger
from os import path

from common import setup_log, list_csv_files, read_csv
from model import ParcelOffer
from place_resolver import MapQuestClient, PlaceResolver


def main(map_quest_api_key: str, csv_cache: str, offers_directory: str):
    setup_log()
    log = getLogger()
    client = MapQuestClient(map_quest_api_key, log)
    resolver = PlaceResolver(client, log)

    if path.isfile(csv_cache):
        resolver.load(csv_cache)
        log.info(f"Loaded {csv_cache} with {len(resolver.cache.keys())} addresses")

    for csv_file in list_csv_files(offers_directory):
        log.info(f"Parsing CSV {csv_file}")
        for row in read_csv(csv_file):
            offer = ParcelOffer.from_csv_row(row)
            if offer:
                _ = resolver.get(offer)
            else:
                log.warning(f"Could not parse into offer: {row}")
        log.info(f"Storing cache with {len(resolver.cache.keys())} into {csv_cache}")
        resolver.save(csv_cache)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Populate places cache with locations resolved using MapQuest API')
    parser.add_argument('cache', type=str, help='Path CSV file containing places cache to work on')
    parser.add_argument('key', type=str, help='MapQuest API key')
    parser.add_argument('offers', type=str, help='Path to directory containing CSV files with offers')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.key, args.cache, args.offers)


if __name__ == '__main__':
    cli_main()
