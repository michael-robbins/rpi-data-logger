#!/usr/bin/env python3

from sense_hat import SenseHat
from datetime import datetime

import logging
import logging.handlers

import sys
import time
import argparse


def start_logging(logger, getters, delimiter, delay=1):
    still_logging = True

    while still_logging:
        line = []
        for getter in getters:
            line.append(getter())

        logger.debug(delimiter.join(line))
        time.sleep(delay)

if __name__ == "__main__":
    sense = SenseHat()

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-filename")
    parser.add_argument("--log-delimiter", default='\t')
    parser.add_argument("--log-format", default=["T", "H", "P"])
    parser.add_argument("--log-delay", type=int, default=1, help="Seconds")
    args = parser.parse_args()

    # Configure logging
    logger = logging.getLogger("DataLogger")
    logger.setLevel(logging.DEBUG)

    if args.log_filename:
        log_max_size = 1024 * 1024 * 20
        log_file_count = 5
        fh = logging.handlers.RotatingFileHandler(args.log_filename,
                                                  maxBytes=log_max_size,
                                                  backupCount=log_file_count)
    else:
        fh = logging.StreamHandler(sys.stdout)

    log_format = "%(asctime)s{delimiter}%(message)s".format(delimiter=args.log_delimiter)
    date_format = "%Y-%m-%dT%H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    value_getters = {
        "T": lambda: str(round(sense.get_temperature_from_humidity(), 1)) + "C",
        "H": lambda: str(round(sense.get_humidity(), 1)) + "%",
        "P": lambda: str(round(sense.get_pressure(), 1)),
    }

    getters = []

    for key in args.log_format:
        if key not in value_getters.keys():
            parser.error("Log Format contains invalid character")
        getters.append(value_getters[key])

    start_logging(logger, getters, args.log_delimiter, delay=args.log_delay)

