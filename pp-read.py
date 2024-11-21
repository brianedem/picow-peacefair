#!/usr/bin/env python3
""" Read Peacefair power meter via pico w web server

The pico w provides a json response with all readings from the Peacefair device

This application provides a library for accessing this data
"""

import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import http
import json
import string
import argparse

log = logging.getLogger(__name__)
logging.basicConfig(filename='wheater.log', encoding='utf-8', level=logging.WARN)

def read_device(dev) :
    """ Reads power information from picow + peacefair power meter
    """
    req = Request(f'http://{dev}/data.json')
    values = {}
    try:
        with urlopen(req) as response :
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

    return values
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
        print(f'{args.item} is not valid - select from:')
        print(f' {items}')
        exit()

    print(args)
    values = read_device(args.net_address)

    if args.dump:
        for i in values:
            print(f'{i:12} = {values[i]}')
    else:
        print(f'{values[args.item]}')
