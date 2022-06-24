"""This script backups the current index and saves to a json file.
"""

import sys
import os
import json
from datetime import datetime
from redisearch import Client

TIMESTAMP = datetime.now().strftime("%d%m%Y-%H:%M:%S")
BEER_INDEX_NAME = "beer_index"


def redis_client(index_name, port=6379, password=False):
    """Get redis client

    Args:
        index_name (str): Redis index name
        port (int): Port for redis
        password (str): Redis password
    Returns:
        obj: redis client
    """
    client = Client(
        index_name=index_name,
        host='localhost',
        port=port,
        password=password
    )
    return client


def backup():
    """Backup redis index to json
    """
    redis_cli = redis_client(BEER_INDEX_NAME)
    backup_path = f"../../data/archive/backup_{TIMESTAMP}.json"
    os.rename("../../data/production_data/final_data_file.json", backup_path)

    data = []
    for beer_id in redis_cli.redis.scan_iter('beer:*'):
        row = redis_cli.redis.hgetall(beer_id)

        beer = {
            "id": beer_id.replace("beer:", ""),
            "name": row.get("title", ""),
            "style": row.get("style", ""),
            "description": row.get("description", ""),
            "abv": row.get("abv", ""),
            "ibu": row.get("ibu", ""),
            "user_thumbs_down": row.get("user_thumbs_down", ""),
            "user_thumbs_up": row.get("user_thumbs_up", ""),
            "was_modified": row.get("was_modified", ""),
            "user_add": row.get("user_add", ""),
            "brewer": {
                "name": row.get("brewer", ""),
                "description": row.get("brewer_description", ""),
                "url": row.get("brewer_url", ""),
                "facebook_url": row.get("brewer_facebook", ""),
                "twitter_url": row.get("brewer_twitter", ""),
                "instagram_url": row.get("brewer_instagram", "")
            }
        }
        data.append(beer)

    with open("../../data/production_data/final_data_file.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    backup()