from multiprocessing.pool import Pool

from tqdm import tqdm
import tweepy


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

users = []
def get_friends(screen_name):

    for page in tweepy.Cursor(api.friends_ids, screen_name=screen_name).pages():
        users.extend(page)
        print(page)

get_friends("verified")