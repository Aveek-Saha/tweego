from multiprocessing.pool import Pool

from tqdm import tqdm
import time
import json

import requests

keys_file = "keys.json"
keys = json.load(open(keys_file, 'r'))

key = keys[0]
bearer_token = ""

def create_url():
    # Replace with user ID below
    user_id = "verified"
    return "https://api.twitter.com/1.1/friends/list.json?count=5&screen_name={}&skip_status=true".format(user_id)


def get_params():
    return {"user.fields": "created_at"}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FollowersLookupPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main():
    url = create_url()
    params = get_params()
    json_response = connect_to_endpoint(url, params)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()