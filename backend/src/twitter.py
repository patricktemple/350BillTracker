import requests
from src.settings import TWITTER_BEARER_TOKEN
import re

AUTH_HEADERS = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}

def get_twitter_user_id(username):
    response = requests.get(f"https://api.twitter.com/2/users/by?usernames={username}", headers=AUTH_HEADERS)
    response.raise_for_status()
    # todo better error handlings
    return response.json()['data'][0]['id']

def get_recent_tweets(twitter_id):
    response = requests.get(f"https://api.twitter.com/2/users/{twitter_id}/tweets?max_results=100&tweet.fields=created_at&expansions=referenced_tweets.id", headers=AUTH_HEADERS)
    response.raise_for_status()
    return response.json()

# needs to paginate
def get_tweets_by_username(username):
    twitter_id = get_twitter_user_id(username)
    return get_recent_tweets(twitter_id)


def _get_canonical_tweet(text):
    return re.sub("\W+", " ", text)


def _tweet_matches_keywords(tweet, keywords, referenced_tweets_by_id):
    for keyword in keywords:
        canonical_keyword = _get_canonical_tweet(keyword)
        # improve this logic a lot
        if canonical_keyword.lower() in _get_canonical_tweet(tweet['text'].lower()):
            return True
        if referenced := tweet.get('referenced_tweets'):
            for referenced_tweet in referenced:
                if referenced_tweet['id'] not in referenced_tweets_by_id:
                    print(f"Did not find referenced tweet {referenced_tweet['id']}")
                    continue
                if canonical_keyword.lower() in _get_canonical_tweet(referenced_tweets_by_id[referenced_tweet['id']]['text']).lower():
                    return True
    return False


def search_tweets_by_user(username, keywords):
    response = get_tweets_by_username(username)
    print("Got results, processing", flush=True)
    tweets = response['data']
    referenced_tweets = response['includes']['tweets']

    referenced_tweets_by_id = {t['id']: t for t in referenced_tweets}

    results = []
    for tweet in tweets:
        if _tweet_matches_keywords(tweet, keywords, referenced_tweets_by_id):
            # TODO: Expand the referenced tweets in the results
            results.append(tweet)
        
    return results