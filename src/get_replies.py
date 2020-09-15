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
    """
    Handles setting up credentials to access the Twitter API via tweepy wrapper.

    Parameters:
    path_to_credentials (String):
        Path to the credentials.ini file location.
    Returns:
    api (tweepy.api.API):
        Twitter API wrapper object.
        See http://docs.tweepy.org/en/latest/api.html
    """
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
    """
    Uses the tweepy api and searches for specified twitter user and associated
    tweet_id.

    Parameters:
    api (tweepy.api.API):
        Twitter API wrapper object.
        See http://docs.tweepy.org/en/latest/api.html
    twitter_user (String):
        Twitter user that owns the tweet we are interested in retrieving.
    tweet_id (String):
        Tweet id of tweet we are interested in retrieving.
    Returns:
    replies (list):
        A list of Tweepy.models.status, or tweet status objects that
        are in_reply_to specified tweet.
    """
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
    """
    Parses the raw data retrieved from the Twitter API by flattening
    and constructing a pandas.Series object specified by tweet_field.

    Parameters:
    replies (list):
        Passing a list of replies of type Tweepy.models.status obtained
        through iterating on the Tweepy cursor.
    tweet_field (String):
        Specifies hte tweet attribute/field within the json file to find.
    Returns:
    field_data_series (pandas.Series):
        A pandas Series object containing the data of specified tweet_field.
    """
    field_data = [flatten(reply._json)[tweet_field] for reply in replies]
    field_data_series = pd.Series(
        field_data,
        name=tweet_field
    )
    return field_data_series

def parse_tweet_url(tweet_url):
    """
    Splits the twitter url to tweet into two components.

    Parameters:
    tweet_url (String):
        A url link to specified tweet.
    Returns:
    twitter_user (String):
        The '@user' owner of the tweet.
    tweet_id (String):
        The tweet status id of interest.
    """
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
    # Setup path to credentials file.
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
        # Retrieve replies from Twitter API
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
        df = pd.concat(s_list, axis=1)

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
