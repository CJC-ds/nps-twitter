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
            if (tweet.in_reply_to_status_id_str==str(tweet_id))
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
        # Save full_text
        t = [reply._json['full_text'] for reply in replies]
        t_series = pd.Series(
            t,
            name='full_text',
            dtype='string'
        )
        # Save created_at
        ca = [reply._json['created_at'] for reply in replies]
        ca_series = pd.Series(
            ca,
            name='created_at',
            dtype='string'
        )
        # Save favorite_count
        fc = [reply._json['favorite_count'] for reply in replies]
        fc_series = pd.Series(
            fc,
            name='favorite_count',
            dtype='int64'
        )
        # Save retweet_count
        rtc = [reply._json['retweet_count'] for reply in replies]
        rtc_series = pd.Series(
            rtc,
            name='retweet_count',
            dtype='int64'
        )
        # Save user.location
        ul = [reply._json['user']['location'] for reply in replies]
        ul_series = pd.Series(
            ul,
            name='user_location',
            dtype='string'
        )

        # Combine the columns
        df = pd.concat([
            t_series,
            rtc_series,
            fc_series,
            ul_series,
            ca_series],
            axis=1
        )
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
