from tqdm import tqdm
import click

import os
import errno
import time
import datetime
import json

from TwitterAPI import TwitterAPI, TwitterPager

import networkx as nx

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def is_folder_exists(folder_name):
    return os.path.exists(folder_name)


def create_api(config):
    # Create a Twitter API object
    api = TwitterAPI(config['app_key'],
                     config['app_secret'],
                     config['oauth_token'],
                     config['oauth_token_secret']
                     )
    return api


def pick_api(apis):
    # Pick an API object that hasn't timed out
    available = [api["available"] for api in apis]
    if all(v == 0 for v in available):
        return None, -1
    for index, api in enumerate(apis):
        if api["available"] == 1:
            return api, index


def api_request(apis, endpoint, params):
    # Send a request using an available API object
    api, index = pick_api(apis)
    if index != -1:
        r = api["connection"].request(endpoint, params)
        if r.headers['x-rate-limit-remaining'] == '0':
            apis[index]["available"] = 0
            return (api_request(apis, endpoint, params))
        return(r)

    else:
        apis[index]["available"] = 0
        wait_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
        print('\nHit the API limit. Waiting for refresh at {}.'
              .format(wait_time.strftime("%H:%M:%S")))
        time.sleep(15 * 60)
        for api in apis:
            api["available"] = 1
        return (api_request(apis, endpoint, params))


def collect_friends(apis, account_id, cursor=-1, limit=5000):
    ids = []
    r = api_request(apis,
                    'friends/ids', {'user_id': account_id, 'cursor': cursor})

    if 'errors' in r.json():
        if r.json()['errors'][0]['code'] == 34:
            return(ids)

    if 'ids' in r.json():
        ids = r.json()['ids']

    if limit > 5000:
        if 'next_cursor' in r.json():
            if r.json()['next_cursor'] != 0:
                ids = ids + \
                    collect_friends(apis, account_id, r.json()
                                    ['next_cursor'], limit)

    return(ids)


def get_friends(friend_id):
    friends = []
    try:
        with open('{0}/{1}.txt'.format(DATA_DIR, friend_id)) as f:
            for line in f:
                friends.append(int(line))
    except:
        pass
    return (friends)


def save_friends(user, ids):
    with open('{0}/{1}.txt'.format(DATA_DIR, user), 'w', encoding='utf-8') as f:
        f.write(str.join('\n', (str(x) for x in ids)))


def collect_and_save_friends(apis, user, refresh=False):
    if not refresh and os.path.exists('{0}/{1}.txt'.format(DATA_DIR, user)):
        return()
    else:
        friends = collect_friends(apis, user)
        save_friends(user, friends)
        return()


def init(apis, screen_name, cursor=-1):
    ids = []
    r = api_request(apis,
                    'friends/ids', {'screen_name': screen_name, 'cursor': cursor})

    # todo: wait if api requests are exhausted

    if 'errors' in r.json():
        if r.json()['errors'][0]['code'] == 34:
            return(ids)

    # for item in r:
    if 'ids' in r.json():
        ids = r.json()['ids']
        print("Collected {} ids".format(len(ids)))
        # ids.append(item)
    elif 'message' in r.json():
        print('{0} ({1})'.format(r.json()['message'], r.json()['code']))

    if 'next_cursor' in r.json():
        if r.json()['next_cursor'] != 0:
            ids = ids + init(apis, screen_name, r.json()['next_cursor'])

    return(ids)


def first_order_ego(apis, screen_name):
    ids = init(apis, screen_name)

    with open('{0}/{1}.txt'.format(DATA_DIR, screen_name), 'w', encoding='utf-8') as f:
        f.write(str.join('\n', (str(x) for x in ids)))


def get_ego_center_friends(screen_name):
    # create the users friend list
    friends = []
    try:
        with open('{}/{}.txt'.format(DATA_DIR, screen_name)) as f:
            for line in f:
                friends.append(int(line))
    except Exception as e:
        print("Error: ", e)
        pass
    return (friends)


def second_order_ego(screen_name, limit=5000):
    friends = get_ego_center_friends(screen_name)

    filtered_friends = []
    print("Filtering friends")
    for friend in tqdm(friends):
        try:
            user = json.load(open("{}/{}.json".format(user_dir, str(friend)), "r"))
            if (user["friends_count"] > limit):
                continue
            else:
                filtered_friends.append(friend)
        except Exception as e:
            print(e)

    print("Collecting friends of friends")
    for friend in tqdm(filtered_friends):
        friend_dir = "{}/{}".format(dump_dir, str(friend))
        user = json.load(open("{}/{}.json".format(user_dir, str(friend)), "r"))
        if is_folder_exists('{0}/{1}.txt'.format(friend_dir, str(friend))):
            continue
        create_dir(friend_dir)

        ids = collect_friends(apis, friend, -1, limit)

        with open('{0}/{1}.txt'.format(friend_dir, str(friend)), 'w', encoding='utf-8') as f:
            f.write(str.join('\n', (str(x) for x in ids)))


# second_order_ego(screen_name)

def get_second_order_friends(friend_id):
    friends = []
    friend_dir = "{}/{}".format(dump_dir, str(friend_id))
    try:
        with open('{}/{}.txt'.format(friend_dir, str(friend_id))) as f:
            for line in f:
                friends.append(int(line))
    except:
        pass
    return friends


# def collect_users(screen_name):

#     friends = get_ego_center_friends(screen_name)

#     users = friends
#     print(len(users))
#     for friend in tqdm(friends[:20]):
#         user_friends = get_second_order_friends(friend)
#         users.extend(user_friends)

#     unique_users = list(set(users))

#     print(len(users))
#     print(len(unique_users))

# collect_users(screen_name)


def get_users(apis, user_id):

    r = api_request(apis,
                    'users/lookup', {'user_id': user_id, 'include_entities': "false"})

    users = r.json()

    if 'errors' in r.json():
        if r.json()['errors'][0]['code'] == 34:
            return(users)

    return(users)


def friend_details(screen_name):
    friends = get_ego_center_friends(screen_name)
    filtered_friends = []

    print("Filtering friends")
    for friend in tqdm(friends):
        if (not os.path.exists("{}/{}.json".format(user_dir, str(friend)))):
            filtered_friends.append(friend)

    n = 100
    groups = [filtered_friends[i:i+n] for i in range(0, len(filtered_friends), n)]

    for group in tqdm(groups):
        users = get_users(apis, ",".join(map(str, group)))
        for user in users:
            json.dump(user, open(
                "{}/{}.json".format(user_dir, user["id"]), "w"))


def create_gml(screen_name, limit=5000):
    # Create a directed graph to store the ego net
    G = nx.DiGraph()
    # Get first degree network
    friends = get_ego_center_friends(screen_name)

    # edges = [(screen_name, x) for x in friends]
    # G.add_edges_from(edges)

    username = {}
    filtered_friends = []

    for friend in tqdm(friends):
        user = json.load(open("{}/{}.json".format(user_dir, str(friend)), "r"))
        if (user["friends_count"] > limit):
                continue
        else:
            filtered_friends.append(friend)
            details = {
                "userid": user["id_str"],
                "followers_count": user["followers_count"],
                "friends_count": user["friends_count"],
                "listed_count": user["listed_count"],
                "verified": user["verified"],
                "statuses_count": user["statuses_count"]
            }

            username[str(friend)] = user["screen_name"]
            G.add_nodes_from([(user["screen_name"], details)])

    for friend in tqdm(filtered_friends):

        second_friends = get_second_order_friends(friend)
        second_edge = [(username[str(friend)], username[str(x)])
                       for x in second_friends if x in filtered_friends]

        # edges.extend(second_edge)

        G.add_edges_from(second_edge)
    
    screen_name_edge = [(screen_name, username[str(x)])
                    for x in filtered_friends]

    G.add_edges_from(screen_name_edge)

    nx.write_gml(G, "{}/{}.gml".format(DATA_DIR, screen_name))


# @click.group()
@click.command()
@click.option("-d", "--dir", type=click.Path(), help="Directory to store data")
@click.option("-k", "--keys-file", type=click.Path(exists=True), help="Location of the api keys JSON file")
@click.option("-n", "--screen-name", type=str, help="The screen name of the ego center user")
@click.option("-f", "--follower-limit", type=int, help="Number of followers for the second order ego")
@click.version_option()
def cli(dir, keys_file, screen_name, follower_limit):
    """Tweego.
    This is a command line program to generate second order ego networks for Twitter users.
    """

    global DATA_DIR
    global dump_dir
    global user_dir
    global apis

    DATA_DIR = dir

    # keys_file = "keys.json"
    keys = json.load(open(keys_file, 'r'))

    apis = []
    for key in keys:
        api = create_api(key)
        apis.append({"connection": api, "available": 1, "time": None})

    # screen_name = "verified"

    dump_dir = "{}/{}".format(DATA_DIR, screen_name)
    user_dir = "{}/{}".format(DATA_DIR, "users")
    create_dir(dump_dir)
    create_dir(user_dir)

    # Get the first order ego net for the given user
    print("Get first order egos")
    first_order_ego(apis, screen_name)
    
    # Get user details
    print("Get user details")
    friend_details(screen_name)

    # Collect second order ego network
    print("Get second order egos")
    second_order_ego(screen_name, follower_limit)

    # Create a GML of the ego network for the user
    print("Generate gml")
    create_gml(screen_name, follower_limit)
    

# cli.add_command(generate)
# generate("dataset", "keys.json", "verified", 10000)
