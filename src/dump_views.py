#!/usr/bin/env python3

import argparse
import sqlite3
from logging import getLogger
from os import path
from typing import List, Optional

from common import write_csv, setup_log


def main(sqlite_db: str, output_path: str, headers: bool = False):
    setup_log()
    _export_query(sqlite_db, "SELECT * FROM latest_offers", path.join(output_path, "latest_offers.csv"),
                  header_table="latest_offers" if headers else None)
    _export_query(sqlite_db, "SELECT * FROM avg_city_price", path.join(output_path, "avg_city_price.csv"),
                  header_table="avg_city_price" if headers else None)
    _export_query(sqlite_db, "SELECT * FROM daily_price_avg", path.join(output_path, "daily_price_avg.csv"),
                  header_table="daily_price_avg" if headers else None)
    _export_query(sqlite_db, "SELECT * FROM last_10days_offers", path.join(output_path, "last_10days_offers.csv"),
                  header_table="last_10days_offers" if headers else None)


def _export_query(sqlite_db: str, query: str, output_csv: str, header_table: Optional[str] = None):
    log = getLogger()
    db_conn: sqlite3.Connection = sqlite3.connect(sqlite_db)

    col_names = []
    try:
        if header_table:
            col_names = [_get_col_names(db_conn, header_table)]
    except (OSError, sqlite3.DatabaseError) as e:
        log.error(f"Could not dump table column names from DB {sqlite_db}/{header_table}: {e}")

    cursor = db_conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        col_names.extend(rows)
        write_csv(csv_file=output_csv, rows=col_names)
    except (OSError, sqlite3.DatabaseError) as e:
        log.error(f"Could not dump query {query} from DB {sqlite_db}: {e}")
        cursor.close()
        db_conn.close()


def _get_col_names(db_conn: sqlite3.Connection, table: str) -> List[str]:
    return [col[1] for col in db_conn.execute(f"pragma table_info('{table}')")]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Merges base isochrone map with given additional GeoJSON features')
    parser.add_argument('db', type=str, help='Path to populated sqlite3 DB')
    parser.add_argument('output', type=str, help='Path to directory where CSV files should be written to')
    parser.add_argument('--headers', action='store_true', help='Add header row with column names')
    return parser.parse_args()


def cli_main():
    args = _parse_args()
    main(args.db, args.output, args.headers)


if __name__ == '__main__':
    cli_main()
