# In[]
import sys
import time
import tweepy
import configparser
import logging
import pandas as pd
import urllib.parse
from flatten_json import flatten

tweet_fields_of_interest = [
    'created_at',
    'id',
    'full_text',
    'user_id',
    'user_name',
    'user_screen_name',
    'user_location',
    'user_description',
    'user_followers_count',
    'retweet_count',
    'favorite_count',
    'lang'
]

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
            if (tweet.in_reply_to_status_id_str==str(tweet_id))
    ]
    return replies

def get_field(replies, tweet_field):
    field_data = [flatten(reply._json)[tweet_field] for reply in replies]
    field_data_series = pd.Series(
        field_data,
        name=tweet_field
    )
    return field_data_series

def parse_tweet_url(tweet_url):
    try:
        if ('twitter' not in tweet_url) & ('status' not in tweet_url):
            raise ValueError('Invalid twitter link.')
        link_header_removed = tweet_url.split('com/', 1)
        user_and_tweet_id = link_header_removed[1].split('/status/')
        twitter_user = user_and_tweet_id[0] # e.g. 'eigenbom'
        tweet_id = user_and_tweet_id[1] # e.g. '1299114959792611328'

        return twitter_user, tweet_id
    except ValueError as e:
        print(e)
        quit()

def main():
    path = 'credentials.ini'
    try:
        print('Loading credentials')
        api = setup_api_config(path)
    except Exception as e:
        print('Invalid path to credentials.ini. credentials.ini file not found.')

    tweet_url = input('Tweet url: ')
    print('Parsing link...')
    twitter_user, tweet_id = parse_tweet_url(tweet_url)

    global tweet_fields_of_interest
    try:
        print('Retrieving tweets from server...')
        replies = get_replies(
            api=api,
            twitter_user=twitter_user,
            tweet_id=tweet_id
        )
        print('Retrieving tweets completed.')
        # Create a list of tweet_field series objects
        s_list = [
            get_field(replies=replies, tweet_field=field)
            for field in tweet_fields_of_interest
        ]
        # Combine the columns
        df = pd.concat(s_list,axis=1)

        # Save file to disk.
        print('Saving...')
        file_name = '../data/raw/replies_to_'+tweet_id+'.csv'
        df.to_csv(file_name, index=False)
        print('Saved successfully as '+file_name)
        print(str(df.shape[0])+' row retrieved.')
        print('Done.')
    except tweepy.error.TweepError as e:
        print('API usage rate exceeded.')
        print(str(e))
        print('Failed to collect data.')
        print('Try again in 15 mins.')


if __name__ == '__main__':
    main()
