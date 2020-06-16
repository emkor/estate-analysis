import logging
import time
from os import path


def setup_log(level: int = logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s.%(msecs)03d|%(levelname)-7s| %(message)s",
                        datefmt="%Y-%m-%dT%H:%M:%S")
    logging.Formatter.converter = time.gmtime


def abs_path(rel_proj_path: str) -> str:
    dir_path = path.dirname(path.realpath(__file__)).partition("estate-analysis")
    return path.join(dir_path[0], dir_path[1], rel_proj_path)
