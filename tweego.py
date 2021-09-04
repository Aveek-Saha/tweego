from multiprocessing.pool import Pool
import os
import errno
import urllib.parse
import time
import datetime
import json

import requests
from TwitterAPI import TwitterAPI, TwitterPager
    
#     url = create_url(screen_name, cursor)
#     json_response = connect_to_endpoint(url).json()
#     next_cursor = json_response["next_cursor_str"]
#     users = json_response["users"]
#     for user in users:
#         json.dump(user, open("{}/{}.json".format(dump_dir, user["id_str"]), "w"))
    
#     while next_cursor != "0":
#         url = create_url(screen_name, next_cursor)
#         response = connect_to_endpoint(url)
#         if response.status_code == 429:
#             print("exceeded")

#         json_response = response.json()
#         next_cursor = json_response["next_cursor_str"]
#         users = json_response["users"]
#         for user in users:
#             json.dump(user, open("{}/{}.json".format(dump_dir, user["id_str"]), "w"))
#         print(json.dumps(json_response, indent=4, sort_keys=True))


# if __name__ == "__main__":
#     main()

DATA_DIR = 'dataset'

def encode_query(query):
    '''
    To preserve the original query, the query is
    url-encoded with no safe ("/") characters.
    '''
    return (urllib.parse.quote(query.strip(), safe=''))


def create_api(config):
    api = TwitterAPI(config['app_key'],
                     config['app_secret'],
                     config['oauth_token'],
                     config['oauth_token_secret']
                     )
    return api


def api_request(endpoint, params):
    '''Respects api limits and retries after waiting.'''
    r = api.request(endpoint, params)
    if r.headers['x-rate-limit-remaining'] == '0':
        waiting_time = int(
            r.headers['x-rate-limit-reset']) - int(round(time.time()))
        print(
            'Hit the API limit. Waiting for refresh at {}.'
            .format(datetime.datetime.utcfromtimestamp(int(r.headers['x-rate-limit-reset']))
                    .strftime('%Y-%m-%dT%H:%M:%SZ')))
        time.sleep(waiting_time)
        return (api_request(endpoint, params))
    return(r)


def collect_friends(account_id, cursor=-1, over5000=False):
    '''Get IDs of the accounts a given account follows
    over5000 allows to collect more than 5000 friends'''
    ids = []
    r = api_request(
        'friends/ids', {'user_id': account_id, 'cursor': cursor})

    # todo: wait if api requests are exhausted

    if 'errors' in r.json():
        if r.json()['errors'][0]['code'] == 34:
            return(ids)

    for item in r:
        if isinstance(item, int):
            ids.append(item)
        elif 'message' in item:
            print('{0} ({1})'.format(item['message'], item['code']))

    if over5000:
        if 'next_cursor' in r.json:
            if r.json['next_cursor'] != 0:
                ids = ids + collect_friends(account_id, r.json['next_cursor'])

    return(ids)


def get_friends(friend_id):
    friends = []
    try:
        with open('{0}/{1}.f'.format(DATA_DIR, friend_id)) as f:
            for line in f:
                friends.append(int(line))
    except:
        pass
    return (friends)


def save_friends(user, ids):
    with open('{0}/{1}.txt'.format(DATA_DIR, user), 'w', encoding='utf-8') as f:
        f.write(str.join('\n', (str(x) for x in ids)))


def collect_and_save_friends(user, refresh=False):
    if not refresh and os.path.exists('{0}/{1}.f'.format(DATA_DIR, user)):
        return()
    else:
        friends = collect_friends(user)
        save_friends(user, friends)
        return()


keys_file = "keys.json"
keys = json.load(open(keys_file, 'r'))

apis = []
for key in keys:
    api = create_api(key)
    apis.append(api)

api = apis[0]
screen_name = "verified"
print(api_request(
        'friends/ids', {'screen_name': screen_name, 'cursor': -1}).json())