"""Script to fetch beer data from https://catalog.beer/api-docs"""

import logging
import requests
import json
import argparse
import urllib
from datetime import datetime

parser = argparse.ArgumentParser(description='Args to fetch data')
parser.add_argument('--api-key', type=str, help='')
parser.add_argument('--type', type=str, help='')
args = parser.parse_args()

URL = 'https://api.catalog.beer/'


def fetch(api):
    now = datetime.now()
    timestamp = str(datetime.timestamp(now))
    timestamp = timestamp.split('.')[0]
    basicAuthCredentials = (args.api_key, args.api_key)
    next_cursor = ''
    batch_count = 0
    while True:
        log.info(f'Fetching batch {batch_count} - {next_cursor}')
        if next_cursor:
            next_cursor = urllib.parse.quote(next_cursor)
            beer_url = f'{URL}{api}?count=5000&cursor={next_cursor}'
        else:
            beer_url = f'{URL}{api}?count=5000'
        try:
            res = requests.get(
                beer_url,
                auth=basicAuthCredentials
            )
        except Exception as e:
            log.error(f'Error fetching data {e}')
            log.warn(f'Batch failed on {batch_count}')
            return

        if res.status_code != 200:
            log.error(res.text)
            log.warn(f'Batch failed on {batch_count}')
            return
        data = res.json()
        next_cursor = data.get('next_cursor')
        has_more = data.get('has_more')
        file_name = f'{api}_batch_{batch_count}_{timestamp}.json'
        with open(file_name, 'w') as f:
            json.dump(data.get('data'), f)

        batch_count += 1
        if not has_more:
            return


def fetch_beers(folder, save_file):
    basicAuthCredentials = (args.api_key, args.api_key)
    with open(folder, 'r') as f:
        data = json.load(f)

    beers = []
    count = 0
    for beer in data:
        log.info(f'Fetching beer {count} - {beer.get("id")}')
        beer_url = f'{URL}beer/{beer.get("id")}'
        try:
            res = requests.get(
                beer_url,
                auth=basicAuthCredentials
            )
        except Exception as e:
            log.error(f'Error fetching data {e}')
            log.warn(f'Batch failed on {count}')
            return

        if res.status_code != 200:
            log.error(res.text)
            log.warn(f'Beers failed on {count}')
            return

        beers.append(res.json())
        count += 1
    if beers:
        with open(save_file, 'w') as f:
            json.dump(beers, f)


def setup_logging(name, level="INFO"):
    """Method to setup logger.

    Args:
        name (str): Name of the logger
        level (str): log level
    Returns:
        obj logger
    """
    log = logging.getLogger(name)
    log.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    ch = logging.StreamHandler()
    ch.setLevel(level=level)
    ch.setFormatter(formatter)

    log.addHandler(ch)
    return log


if __name__ == "__main__":
    log = setup_logging('data_fetch')
    if args.type == 'beer':
        fetch('beer')
    elif args.type == 'brewer':
        fetch('brewer')

    elif args.type == 'get_beers':
        fetch_beers(
            'beer_batch_12_1606102731.json',
            'get_beers_batch_12_1606102731.json'
        )
