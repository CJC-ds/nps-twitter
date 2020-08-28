# In[]
import sys
import time
import tweepy
import configparser
import logging
import pandas as pd
import urllib.parse

def setup_api_config(path_to_credentials):
    # Configure the credentials
    CONFIG = configparser.ConfigParser()
    CONFIG.read(path_to_credentials)

    # Define each key
    consumer_key = CONFIG['API']['key']
    consumer_secret = CONFIG['API']['secret']
    access_token = CONFIG['Access']['token']
    access_token_secret = CONFIG['Access']['secret']

    auth = tweepy.OAuthHandler(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret)
    auth.set_access_token(
        key=access_token,
        secret=access_token_secret)
    api = tweepy.API(auth)
    return api

def get_replies(api, twitter_user, tweet_id):
    replies = [
            tweet
            for tweet in tweepy.Cursor(
            api.search,
            q='to:'+twitter_user,
            result_type='recent',
            tweet_mode='extended',
            timeout=999999).items(1000)
            if hasattr(tweet, 'in_reply_to_status_id_str')
            if (tweet.in_reply_to_status_id_str==tweet_id)
    ]
    return replies

def main():
    path = 'credentials.ini'
    twitter_user = input('Thread owner: ')# e.g. 'eigenbom'
    tweet_id = input('Thread id: ')# e.g. '1299114959792611328'
    api = setup_api_config(path)
    try:
        replies = get_replies(
            api=api,
            twitter_user=twitter_user,
            tweet_id=tweet_id
        )
        t = [reply._json['full_text'] for reply in replies]
        t_series = pd.Series(t, name='replies', dtype='string')
        print('Saving...')
        file_name = 'replies_to_'+tweet_id+'.csv'
        t_series.to_csv(file_name, index=False)
        print('Saved successfully as %s', file_name)
        print('Done.')
    except twitter.error.TwitterError as e:
        print('Caught twitter api error: %s', e)



if __name__ == '__main__':
    main()
