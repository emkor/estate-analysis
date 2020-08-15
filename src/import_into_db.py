#!/usr/bin/env python3

import argparse
import sqlite3
from datetime import datetime
from logging import getLogger, Logger
from typing import List, Optional, Iterable

from more_itertools import chunked

from common import setup_log, read_csv, list_csv_files
from model import Place, ParcelOffer, BroadbandAccess


def _init_tables(db_conn, ddl_script):
    with open(ddl_script, "r") as ddl_f:
        ddl_query = " ".join(ddl_f.read().splitlines())
    c = db_conn.cursor()
    c.executescript(ddl_query)
    c.close()


def _parse_bandwidth(bandwidth: str) -> Optional[int]:
    try:
        return int(bandwidth.strip().lower().replace("do", "").strip())
    except ValueError:
        return None


def _filter_fields_from_curr_inet_csv_row(row: List[str]) -> Optional[List[str]]:
    if len(row) > 12:
        bandwidth = _parse_bandwidth(row[12])
        return [row[0].strip(), None, row[3].strip().title(), row[5].strip().title(), row[7].strip().title() or None,
                row[8].strip().title() or None, row[11].strip().title(), row[13].strip().title(), bandwidth] \
            if bandwidth else None
    else:
        return None


def _filter_fields_from_planned_inet_csv_row(row: List[str]) -> Optional[List[str]]:
    if len(row) > 15:
        bandwidth = _parse_bandwidth(row[5])
        return [row[0].strip(), datetime.strptime(row[4], "%Y%m%d").date().isoformat(),
                row[8].strip().title(), row[12].strip().title() or None, row[14].strip().title() or None,
                row[15].strip().title(), row[1].strip().title(), row[3].strip().title(), bandwidth] \
            if bandwidth else None
    else:
        return None


def main(db_file: str, ddl_script: str, place_cache: str, offers_path: str, inet_curr: str, inet_popc: str):
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

    for inet_curr_csv in list_csv_files(inet_curr):
        log.info(f"Inserting current broadband data from CSVs under {inet_curr_csv} into DB...")
        inet_curr_rows = filter(None,
                                map(_filter_fields_from_curr_inet_csv_row,
                                    read_csv(inet_curr_csv, delimiter=';')))
        broadband_accesses = filter(None, map(BroadbandAccess.from_csv_row, inet_curr_rows))
        _insert_broadband_access_obj(broadband_accesses, db_conn, log)

    for inet_popc_csv in list_csv_files(inet_popc):
        log.info(
            f"Inserting planned broadband expansion data from CSVs under {inet_popc_csv} into DB...")
        inet_curr_rows = filter(None,
                                map(_filter_fields_from_planned_inet_csv_row, read_csv(inet_popc_csv, delimiter=';')))
        broadband_accesses = filter(None, map(BroadbandAccess.from_csv_row, inet_curr_rows))
        _insert_broadband_access_obj(broadband_accesses, db_conn, log)

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


def _insert_broadband_access_obj(broadband_accesses: Iterable[BroadbandAccess], db_conn: sqlite3.Connection,
                                 log: Logger):
    for access_chunk in chunked(map(lambda ba: ba.to_sql_row(), broadband_accesses), 50):
        try:
            c = db_conn.cursor()
            c.executemany("INSERT INTO broadband VALUES (?,?,?,?,?,?,?,?,?)", access_chunk)
            c.close()
            db_conn.commit()
        except sqlite3.IntegrityError as e:
            log.warning(
                f"Could not insert {len(access_chunk)} rows [{access_chunk[0]}, ..., {access_chunk[-1]}]: {e}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Import CSV data into sqlite3 DB')
    parser.add_argument('db', type=str, help='Path to sqlite3 DB file')
    parser.add_argument('ddl', type=str, help='Path to SQL DDL script executed before data insertion')
    parser.add_argument('place', type=str, help='Path to CSV file with Places cache')
    parser.add_argument('offer', type=str, help='Path to directory containing offer CSV files')
    parser.add_argument('inet_curr', type=str, help='Path to directory containing current broadband infrastructure')
    parser.add_argument('inet_popc', type=str, help='Path to directory containing planned '
                                                    'expansion of broadband network (POPC)')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.db, args.ddl, args.place, args.offer, args.inet_curr, args.inet_popc)


if __name__ == '__main__':
    cli_main()
    # main("/home/mat/proj/estate-analysis/data/offers.db",
    #      "/home/mat/proj/estate-analysis/src/ddl.sql",
    #      "/home/mat/proj/estate-analysis/data/place_cache.csv",
    #      "/home/mat/proj/estate-analysis/offers",
    #      "/home/mat/proj/estate-analysis/data/uke/current",
    #      "/home/mat/proj/estate-analysis/data/uke/popc")
