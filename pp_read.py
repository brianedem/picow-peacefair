#!/usr/bin/env python3
""" Read Peacefair power meter via pico w web server

The pico w provides a json response with all readings from the Peacefair device

This application provides a library for accessing this data
"""
import sys
import logging
import requests
import argparse

log = logging.getLogger(__name__)

def read_dev(dev) :
    try:
        r = requests.get(f'http://{dev}/data.json')
    except requests.exceptions.ConnectionError:
        log.exception(f'Unable to connect to {dev}')
        return None
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        log.exception(f'Unable to decode JSON data from {dev}')
        return None

items = ['voltage','current','power','energy','frequency','powerFactor','powerAlarm','hostname','temperature']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('net_address', help='network name or address of device')
    parser.add_argument('item', help='register to be read',
        nargs='*', choices=items)
    args = parser.parse_args()

    logging.basicConfig(filename='pp-read.log', encoding='utf-8', level=logging.WARN)

    values = read_dev(args.net_address)
    if values is None:
        sys.exit(f'unable to access device {args.net_address}')

    log.debug(args.item)
    if len(args.item)==1:
        print(f'{values[args.item[0]]}')
        sys.exit(0)
    if len(args.item)==0:
        args.item = items
    for i in args.item:
        print(f'{i:12} = {values[i]}')
