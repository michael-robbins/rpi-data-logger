#!/usr/bin/env python3

from sense_hat import SenseHat
from datetime import datetime

import logging
import logging.handlers

import time
import argparse


def obtain_movement():
    # Get device orientation
    o = sense.get_orientation()
    pitch = o["pitch"]
    roll = o["roll"]
    yaw = o["yaw"]

    pitch = round(pitch, 1)
    roll = round(roll, 1)
    yaw = round(yaw, 1)


def start_logging(logger, getters, delimiter):
    still_logging = True

    while still_logging:
        line = []
        for getter in getters:
            line.append(getter())

        logger.debug(delimiter.join(line))
        time.sleep(1)

if __name__ == "__main__":
    sense = SenseHat()

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-filename", required=True)
    parser.add_argument("--log-delimiter", default='\t')
    parser.add_argument("--log-format", default=["t,T,H,P"])

    args = parser.parse_args()

    # Configure logging
    logger = logging.getLogger("DataLogger")
    logger.setLevel(logging.DEBUG)

    log_max_size = 1024 * 1024 * 20
    log_file_count = 5
    fh = logging.handlers.RotatingFileHandler(args.log_filename,
                                                   maxBytes=log_max_size,
                                                   backupCount=log_file_count)
    logger.addHandler(fh)

    log_format = "%(asctime)s{delimiter}%(message)s".format(delimiter=args.log_delimiter)
    date_format = "%Y-%m-%dT%H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    logger.addFormatter(formatter)

    value_getters = {
        "t": datetime.now,
        "T": sense.get_temperature_from_humidity,
        "H": sense.get_humidity,
        "P": sense.get_pressure,
        "M": obtain_movement,
    }

    getters = []

    for key in args.log_format:
        if key not in value_getters:
            args.error("Log Format contain invalid character")
        log_getters.append(value_getters[key])

    start_logging(logger, getters, args.delimiter)

