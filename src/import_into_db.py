#!/usr/bin/env python3

import argparse
import sqlite3
from logging import getLogger

from more_itertools import chunked

from common import setup_log, read_csv, list_csv_files
from model import Place, ParcelOffer


def _init_tables(db_conn, ddl_script):
    with open(ddl_script, "r") as ddl_f:
        ddl_query = " ".join(ddl_f.read().splitlines())
    c = db_conn.cursor()
    c.executescript(ddl_query)
    c.close()


def main(db_file: str, ddl_script: str, place_cache: str, offers_path: str):
    setup_log()
    log = getLogger()
    db_conn: sqlite3.Connection = sqlite3.connect(db_file)
    _init_tables(db_conn, ddl_script)

    log.info(f"Inserting Places cache {place_cache} into sqlite3 DB {db_file}...")
    places = filter(None, map(Place.from_csv_row, read_csv(place_cache)))
    for places_chunk in chunked(map(lambda p: p.to_sql_row(), places), 50):
        try:
            c = db_conn.cursor()
            c.executemany("INSERT INTO place VALUES (?,?,?,?,?)", places_chunk)
            c.close()
            db_conn.commit()
        except sqlite3.IntegrityError as e:
            log.warning(f"Could not insert {len(places_chunk)} rows [{places_chunk[0]}, ..., {places_chunk[-1]}]: {e}")

    for offers_csv in list_csv_files(offers_path):
        log.info(f"Inserting Offers from CSV {offers_csv} into sqlite3 DB {db_file}...")
        offers = filter(None, map(ParcelOffer.from_csv_row, read_csv(offers_csv)))
        for offers_chunk in chunked(map(lambda p: p.to_sql_row(), offers), 50):
            try:
                c = db_conn.cursor()
                c.executemany("INSERT INTO parcel_offer VALUES (?,?,?,?,?,?,?)", offers_chunk)
                c.close()
                db_conn.commit()
            except sqlite3.IntegrityError as e:
                log.warning(
                    f"Could not insert {len(offers_chunk)} rows [{offers_chunk[0]}, ..., {offers_chunk[-1]}]: {e}")

    db_conn.close()
    log.info("Done inserting Places cache and Offers into sqlite3 DB")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import CSV data into sqlite3 DB')
    parser.add_argument('db', type=str, help='Path to sqlite3 DB file')
    parser.add_argument('ddl', type=str, help='Path to SQL DDL script executed before data insertion')
    parser.add_argument('place', type=str, help='Path to CSV file with Places cache')
    parser.add_argument('offer', type=str, help='Path to directory containing offer CSV files')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.db, args.ddl, args.place, args.offer)


if __name__ == '__main__':
    cli_main()
