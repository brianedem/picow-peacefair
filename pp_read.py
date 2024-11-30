#!/usr/bin/env python3
""" Read Peacefair power meter via pico w web server

The pico w provides a json response with all readings from the Peacefair device

This application provides a library for accessing this data
"""
import sys
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import http
import json
import string
import argparse
import socket

log = logging.getLogger(__name__)

def read_device(dev) :
    """ Reads power information from picow + peacefair power meter
    """
    req = Request(f'http://{dev}/data.json')
    values = None
    try:
        with urlopen(req, timeout=1) as response :
            content_type = response.getheader('Content-type')
            if 'json' in content_type :
                body = response.read()
                log.debug(body)
                try:
                    values = json.loads(body)
                except json.JSONDecodeError:
                    log.exception(f'Unable to import json from {dev}')
            else :
                print('{dev}: json content not found')
                print(response.read())

    except HTTPError as e:
        log.exception(f'Request to {dev} {e.code}')
    except URLError as e:
        log.exception(f'Request to {dev} {e.reason}')
    except TimeoutError :
        log.exception(f'Request to {dev} timed out')
    except http.client.RemoteDisconnected :
        log.exception(f'{dev} disconnected before returning response')
    except socket.error as e:
        log.exception(f'socket error {e}')

    return values

import requests
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
        nargs='?')
    parser.add_argument('-d', '--dump', help='dump all values',
        action='store_true')
    args = parser.parse_args()

    if args.item and args.item not in items:
        exit(f'{args.item} is not valid - select from:\n {items}')

    logging.basicConfig(filename='pp-read.log', encoding='utf-8', level=logging.WARN)

    values = read_device(args.net_address)
    if values is None:
        sys.exit(f'unable to access device {args.net_address}')

    if args.dump:
        for i in values:
            print(f'{i:12} = {values[i]}')
    else:
        print(f'{values[args.item]}')
