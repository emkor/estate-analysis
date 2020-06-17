#!/usr/bin/env python3

import sqlite3
from logging import getLogger
from typing import Optional, Type

from more_itertools import chunked

from common import setup_log, read_csv
from model import Model, Place


def _init_tables(db_conn, ddl_script):
    with open(ddl_script, "r") as ddl_f:
        ddl_query = " ".join(ddl_f.read().splitlines())
    c = db_conn.cursor()
    c.executescript(ddl_query)
    c.close()


def _parse_into_model(row: str, model: Type[Model], sep: str = ";") -> Optional[Model]:
    return model.from_csv_row(row.split(sep))


def main(db_file: str, ddl_script: str, place_cache: str):
    setup_log()
    log = getLogger()
    db_conn: sqlite3.Connection = sqlite3.connect(db_file)
    _init_tables(db_conn, ddl_script)

    places = filter(None, map(Place.from_csv_row, read_csv(place_cache)))
    for places_chunk in chunked(map(lambda p: p.to_csv_row(), places), 50):
        try:
            c = db_conn.cursor()
            c.executemany("INSERT INTO place VALUES (?,?,?,?,?)", places_chunk)
            c.close()
            db_conn.commit()
        except sqlite3.IntegrityError as e:
            log.warning(f"Could not insert {len(places_chunk)} rows: {e}")

    db_conn.close()


if __name__ == '__main__':
    main("../offers.db", "ddl.sql", "../place_cache.csv")
