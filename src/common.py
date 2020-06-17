import csv
import logging
import os
import time
from os import path
from typing import Generator, List


def setup_log(level: int = logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s.%(msecs)03d|%(levelname)-7s| %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S")
    logging.Formatter.converter = time.gmtime


def abs_path(rel_proj_path: str) -> str:
    dir_path = path.dirname(path.realpath(__file__)).partition("estate-analysis")
    return path.join(dir_path[0], dir_path[1], rel_proj_path)


def list_csv_files(dir_path: str) -> List[str]:
    return sorted([path.join(dir_path, f) for f in os.listdir(dir_path)
                   if path.isfile(path.join(dir_path, f))
                   and path.splitext(f)[-1].lower() == ".csv"])


def read_simple_csv(csv_file: str) -> Generator[str, None, None]:
    with open(csv_file, "r") as csv_f:
        return (line.strip() for line in csv_f.read().splitlines() if line.strip())


def read_csv(csv_file: str) -> Generator[List[str], None, None]:
    with open(csv_file, "r") as csv_f:
        for line in csv.reader(csv_f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL):
            if line:
                yield line
