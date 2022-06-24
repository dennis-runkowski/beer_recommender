"""Build redis index
Example Beer

    {
        "id": "3c4df9d1-84cb-485d-b510-a4a599d294a3",
        "object": "beer",
        "name": "\"18\" Imperial IPA 2",
        "style": "American-Style Imperial Stout",
        "description": null,
        "abv": 11.1,
        "ibu": null,
        "cb_verified": false,
        "brewer_verified": false,
        "last_modified": 1588448205,
        "brewer": {
            "id": "ecbd38d5-957b-4239-ab90-e6509b84ffd9",
            "object": "brewer",
            "name": "Ship Bottom Brewery",
            "description": null,
            "short_description": null,
            "url": "http://shipbottombrewery.com/",
            "cb_verified": false,
            "brewer_verified": false,
            "facebook_url": null,
            "twitter_url": null,
            "instagram_url": null,
            "last_modified": 1588448205
        }
    }
"""

from redisearch import Client, TextField, TagField, IndexDefinition, \
    NumericField, AutoCompleter, Suggestion
import json
import sys
import os

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


def create_beer_index(client):
    """Create index full of beers

    Args:
        client (obj): redis client
    """
    definition = IndexDefinition(prefix=['beer:'])
    client.create_index(
        (
            TextField("title", no_stem=True, sortable=True, weight=3),
            TextField("style", no_stem=True, weight=2),
            TextField("description", weight=2),
            TagField("user_thumbs_down", separator=","),
            TagField("user_thumbs_up", separator=","),
            NumericField("abv", sortable=True,  no_index=True),
            NumericField("ibu", sortable=True, no_index=True),
            NumericField("user_thumbs_up_cnt", sortable=True, no_index=True),
            NumericField("user_thumbs_down_cnt", sortable=True, no_index=True),
            TextField("brewer", no_stem=True, weight=1),
            TextField("brewer_description", weight=1)
        ),
        definition=definition
    )


def helper_empty_value(data, integer=False):
    """Set None to empty string
    """
    if integer:
        if not data:
            return 0.0
        return float(data)
    if not data:
        return ""
    return data


def index_data(client):
    """Index data into redis

    Args:
        client (obj): redis client
    """
    with open('../../data/production_data/final_data_file.json', 'r') as f:
        data = json.load(f)
    count = []

    # Type ahead
    auto = AutoCompleter("beer_title_ac")
    auto_style = AutoCompleter("beer_title_style")
    auto_brewer = AutoCompleter("beer_title_brewer")
    for beer in data:
        beer_id = f"beer:{beer['id']}"
        if beer_id not in count:
            count.append(beer_id)
        brewer = beer["brewer"]

        style = helper_empty_value(beer.get("style", ""))
        if style:
            auto_style.add_suggestions(Suggestion(style))

        brewer_name = helper_empty_value(brewer.get("name", ""))
        if brewer_name:
            auto_brewer.add_suggestions(Suggestion(brewer_name))

        auto.add_suggestions(Suggestion(beer["name"]))
        client.redis.hset(
            beer_id,
            mapping={
                "title": beer["name"],
                "style": style,
                "user_thumbs_down": beer.get("user_thumbs_down", ""),
                "user_thumbs_up": beer.get("user_thumbs_up", ""),
                "description": helper_empty_value(beer.get("description", "")),
                "abv": helper_empty_value(beer.get("abv", ""), integer=True),
                "ibu": helper_empty_value(beer.get("ibu", ""), integer=True),
                "brewer": brewer_name,
                "user_add": beer.get("user_add", ""),
                "brewer_description": helper_empty_value(
                    brewer.get("description", "")),
                "brewer_url": helper_empty_value(brewer.get("url", "")),
                "brewer_facebook": helper_empty_value(
                    brewer.get("facebook_url", "")),
                "brewer_instagram": helper_empty_value(
                    brewer.get("instagram_url", "")),
                "brewer_twitter": helper_empty_value(brewer.get("twitter_url"))
            }
        )
    print(len(count))


def delete_beer_index(client):
    """Delete beer index

    Args:
        client (obj): redis client
    """
    try:
        client.drop_index()
    except Exception as e:
        print(f"Could not delete {e}")


if __name__ == "__main__":
    client = redis_client(BEER_INDEX_NAME)
    delete_beer_index(client)
    create_beer_index(client)
    index_data(client)
