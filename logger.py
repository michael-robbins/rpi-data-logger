#!/usr/bin/env python3

from sense_hat import SenseHat
from datetime import datetime

import logging
import logging.handlers

import time
import argparse


last_movement = None

def obtain_movement():
    global last_movement
    tolerance = 5

    # Get device orientation
    o = sense.get_orientation()
    pitch = o["pitch"]
    roll = o["roll"]
    yaw = o["yaw"]

    pitch = round(pitch, 1)
    roll = round(roll, 1)
    yaw = round(yaw, 1)

    this_movement = (pitch, roll, yaw)

    if last_movement is not None:
        for name, old, new in zip(["pitch", "roll", "yaw"], last_movement, this_movement):
            #print("{0},{1},{2}".format(name, old, new))
            lower_bound = round((old - tolerance) % 360, 1)
            upper_bound = round((old + tolerance) % 360, 1)

            if upper_bound < lower_bound:
                upper_bound += 360

                if new < upper_bound and new < lower_bound:
                    new += 360

            if not lower_bound < new < upper_bound:
                print("{0}: {1} < {2} < {3}".format(name, lower_bound, new, upper_bound))

    last_movement = (pitch, roll, yaw)
    return (pitch, roll, yaw)

def start_logging(logger, getters, delimiter, headers=None):
    still_logging = True

    if headers:
        headers = ["time"] + headers
        logger.debug(delimiter.join(headers))

    while still_logging:
        line = []
        for getter in getters:
            line.append(getter())

        print([datetime.now()] + line)
        logger.debug(delimiter.join(line))
        time.sleep(1)

if __name__ == "__main__":
    sense = SenseHat()

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-filename", required=True)
    parser.add_argument("--log-delimiter", default='\t')
    parser.add_argument("--log-format", default=["T", "H", "P", "M"])
    args = parser.parse_args()

    # Configure logging
    logger = logging.getLogger("DataLogger")
    logger.setLevel(logging.DEBUG)

    log_max_size = 1024 * 1024 * 20
    log_file_count = 5
    fh = logging.handlers.RotatingFileHandler(args.log_filename,
                                                   maxBytes=log_max_size,
                                                   backupCount=log_file_count)

    log_format = "%(asctime)s{delimiter}%(message)s".format(delimiter=args.log_delimiter)
    date_format = "%Y-%m-%dT%H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    value_getters = {
        "T": lambda: str(round(sense.get_temperature_from_humidity(), 1)) + "C",
        "H": lambda: str(round(sense.get_humidity(), 1)) + "%",
        "P": lambda: str(round(sense.get_pressure(), 1)),
        "M": lambda: str(obtain_movement()),
    }

    getters = []

    for key in args.log_format:
        if key not in value_getters.keys():
            parser.error("Log Format contains invalid character")
        getters.append(value_getters[key])

    start_logging(logger, getters, args.log_delimiter, headers=args.log_format)

