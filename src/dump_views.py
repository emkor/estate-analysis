#!/usr/bin/env python3

import argparse
import sqlite3
from logging import getLogger
from os import path

from common import write_csv, setup_log


def main(sqlite_db: str, output_path: str):
    setup_log()
    _export_query(sqlite_db, "SELECT * FROM latest_offers", path.join(output_path, "latest_offers.csv"))
    _export_query(sqlite_db, "SELECT * FROM avg_city_price", path.join(output_path, "avg_city_price.csv"))
    _export_query(sqlite_db, "SELECT * FROM daily_price_avg", path.join(output_path, "daily_price_avg.csv"))


def _export_query(sqlite_db: str, query: str, output_csv: str):
    log = getLogger()
    db_conn: sqlite3.Connection = sqlite3.connect(sqlite_db)
    cursor = db_conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        write_csv(csv_file=output_csv, rows=rows)
    except (OSError, sqlite3.DatabaseError) as e:
        log.error(f"Could not dump query {query} from DB {sqlite_db}: {e}")
        cursor.close()
        db_conn.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Merges base isochrone map with given additional GeoJSON features')
    parser.add_argument('db', type=str, help='Path to populated sqlite3 DB')
    parser.add_argument('output', type=str, help='Path to directory where CSV files should be written to')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.db, args.output)


if __name__ == '__main__':
    cli_main()
