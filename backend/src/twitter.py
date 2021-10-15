import requests
from src.settings import TWITTER_BEARER_TOKEN

AUTH_HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

def get_twitter_user_id(username):
    response = requests.get(f"https://api.twitter.com/2/users/by?usernames={username}", headers=AUTH_HEADERS)
    response.raise_for_status()
    # todo better error handlings
    return response.json()['data'][0]['id']

def get_recent_tweets(twitter_id):
    response = requests.get(f"https://api.twitter.com/2/users/{twitter_id}/tweets?max_results=100&tweet.fields=created_at", headers=AUTH_HEADERS)
    response.raise_for_status()
    return response.json()

def get_tweets_by_username(username):
    twitter_id = get_twitter_user_id(username)
    return get_recent_tweets(twitter_id)