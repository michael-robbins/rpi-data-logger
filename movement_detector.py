#!/usr/bin/env python3

from sense_hat import SenseHat
from datetime import datetime

import logging
import logging.handlers

import sys
import time
import boto3
import argparse


last_movement = None

def movement_detected():
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
            lower_bound = round((old - tolerance) % 360, 1)
            upper_bound = round((old + tolerance) % 360, 1)

            if upper_bound < lower_bound:
                upper_bound += 360

                if new < upper_bound and new < lower_bound:
                    new += 360

            if not lower_bound < new < upper_bound:
                last_movement = this_movement
                return "{0}: {1} < {2} < {3}".format(name, lower_bound, new, upper_bound)

    last_movement = this_movement
    return None

def raise_sns_alarm(topic, location):
    client = boto3.client("sns")

    message = "Movement detected in {0}".format(location)

    client.publish(TopicArn=topic, Message=message)

if __name__ == "__main__":
    sense = SenseHat()

    parser = argparse.ArgumentParser()
    parser.add_argument("--log-filename")
    parser.add_argument("--sns-topic")
    parser.add_argument("--location", default="Raspberry Pi")
    args = parser.parse_args()

    # Configure logging
    logger = logging.getLogger("MovementDetector")
    logger.setLevel(logging.DEBUG)

    if args.log_filename:
        log_max_size = 1024 * 1024 * 20
        log_file_count = 5
        fh = logging.handlers.RotatingFileHandler(args.log_filename,
                                                  maxBytes=log_max_size,
                                                  backupCount=log_file_count)
    else:
        fh = logging.StreamHandler(sys.stdout)

    log_format = "time='%(asctime)s' message='%(message)s' result='%(result)s'"
    date_format = "%Y-%m-%dT%H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    monitoring = True
    alarm_active = False

    logger.info("Beginning movement detection", extra={"result": None})
    while monitoring:
        result = movement_detected()

        if result and not alarm_active:
            logger.error("Movement detected!", extra={"result": result})
            alarm_active = True

            if args.sns_topic:
                raise_sns_alarm(args.sns_topic, args.location)

        elif not result:
            alarm_active = False

        time.sleep(1)
