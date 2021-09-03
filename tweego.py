from multiprocessing.pool import Pool
import os
import errno
import urllib.parse
import time
import datetime
import json

import requests
from TwitterAPI import TwitterAPI, TwitterPager

keys_file = "keys.json"
keys = json.load(open(keys_file, 'r'))

key = keys[1]
bearer_token = key["bearer_token"]

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def create_url(screen_name, cursor):
    return "https://api.twitter.com/1.1/friends/list.json?cursor={}&count=5&screen_name={}&skip_status=true".format(cursor, screen_name)

def rate_limit_url():
    return "https://api.twitter.com/1.1/application/rate_limit_status.json?resources=users"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    # r.headers["User-Agent"] = "v2FollowersLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)
    return response


def main():
    screen_name = "verified"
    cursor = -1
    dump_dir = "{}/{}".format("dataset", screen_name)
    create_dir(dump_dir)

    
    url = create_url(screen_name, cursor)
    json_response = connect_to_endpoint(url).json()
    next_cursor = json_response["next_cursor_str"]
    users = json_response["users"]
    for user in users:
        json.dump(user, open("{}/{}.json".format(dump_dir, user["id_str"]), "w"))
    
    while next_cursor != "0":
        url = create_url(screen_name, next_cursor)
        response = connect_to_endpoint(url)
        if response.status_code == 429:
            print("exceeded")

        json_response = response.json()
        next_cursor = json_response["next_cursor_str"]
        users = json_response["users"]
        for user in users:
            json.dump(user, open("{}/{}.json".format(dump_dir, user["id_str"]), "w"))
        print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()