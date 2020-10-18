import sys
import time
import tweepy
import configparser
import logging
import pandas as pd
import urllib.parse
from flatten_json import flatten

# Tweet attributes we wish to keep.
# For full list of attributes see `tweet_fields_of_interest.txt`
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

default_flags = {
    'file_format': 'csv',
    'search_depth': 1000,
    'wait_on_rate_limit': 'off',
    'big_query': 'on',
    'stop_words': []
}

def setup_api_config(path_to_credentials, flag_list):
    """
    Handles setting up credentials to access the Twitter API via tweepy wrapper.

    Args:
    path_to_credentials (String):
        Path to the credentials.ini file location.

    Returns:
    api (tweepy.api.API):
        Twitter API wrapper object.
        See http://docs.tweepy.org/en/latest/api.html
    """
    if flag_list['wait_on_rate_limit'].lower() == 'on':
        wait_on_limit=True
    else:
        wait_on_limit=False

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
    api = tweepy.API(
        auth,
        wait_on_rate_limit=wait_on_limit,
        wait_on_rate_limit_notify=wait_on_limit
    )
    return api

def get_replies(api, twitter_user, tweet_id, flag_options):
    """
    Uses the tweepy api and searches for specified twitter user and associated
    tweet_id.

    Args:
    api (tweepy.api.API):
        Twitter API wrapper object.
        See http://docs.tweepy.org/en/latest/api.html
    twitter_user (String):
        Twitter user that owns the tweet we are interested in retrieving.
    tweet_id (String):
        Tweet id of tweet we are interested in retrieving.
    flag_options (dict):
        Specifies user options for retrieving tweets.

    Returns:
    replies (list):
        A list of Tweepy.models.status, or tweet status objects that
        are in_reply_to specified tweet.
    """
    items = flag_options['search_depth']
    replies = [
            tweet
            for tweet in tweepy.Cursor(
            api.search,
            q='to:'+twitter_user,
            result_type='recent',
            tweet_mode='extended',
            timeout=999999).items(items)
            if hasattr(tweet, 'in_reply_to_status_id_str')
            if (tweet.in_reply_to_status_id_str==str(tweet_id))
    ]
    return replies

def get_field(replies, tweet_field):
    """
    Parses the raw data retrieved from the Twitter API by flattening
    and constructing a pandas.Series object specified by tweet_field.

    Args:
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

    Args:
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

def raw_input_parser(string_with_flags):
    """
    Seperate the raw input string into segments.
    These segments will be a twitter url string, and a list of tuples
    that match the key flag with the associated value.

    Args:
        string_with_flags (String):
            raw input from user

    Returns:
        url (string):
            the specified url string.
        flag_list (list):
            list of tuples with the flag (key) and associated value in each
            listed pair e.g. flag_list[0][0] (key), flag_list[0][1] (value).
    """
    try:
        url, flags = string_with_flags.split(' ', 1)
        flags = flags.split('-')
        flag_list = tuple(flag.split(' ', 1) for flag in flags if flag)
        return url, flag_list
    except ValueError as ve:
        print('No specified flags. Using default options.')
        return string_with_flags, {}

def flag_parser(flag_list):
    """
    Reads the flag_list to appropriately assign optional
    values to intended functions.

    current_flags:
        file_format `-f`:
            Specify the output file format. Default `csv`.
            Other option `pickle`.
        search_depth `-sd`:
            Specify the number of tweets to search through. Default `1000`,
            Note that not all tweets that are searched will be `in_reply_to`
            specified tweet. If `-s` is greater than 1000 please set `-w` to `on`.
            Free tier twitter API limits at 1000.
        wait_on_rate_limit `-w`:
            Wait to retrieve more tweets once API limitations are exceeded.
            Can be either `on` or `off`. Default `off`.

    Args:
        flag_list (list): a list of lists holding key, value pairs as tuples.
    Returns:
        dict: key value pairs that specify user options.

    Raises:
        ValueError: specified flags are not available options.
    """
    flag_conv = {
        'f':'file_format',
        'sd':'search_depth',
        'w':'wait_on_rate_limit',
        'bq': 'big_query',
        'sw': 'stop_words'
    }
    global default_flags
    try:
        user_flags = {flag_conv[flag[0]]:flag[1] for flag in flag_list}
        merged_flags = {**default_flags, **user_flags}
        try:
            merged_flags['search_depth'] = int(merged_flags['search_depth'])
        except TypeError as te:
            print(ke)
            print('Flag `search_depth` specified is not an integer')
            print('Set `search_depth to default...`')
            merged_flags['search_depth'] = 1000
        if not (not merged_flags['stop_words']):
            merged_flags['stop_words'] = merged_flags['stop_words'].split(',')
            merged_flags['stop_words'] = [x.strip() for x in merged_flags['stop_words']]
        return merged_flags
    except KeyError as ke:
        print(ke)
        print('Flag value input not recognised. \
        Specified flags are not available options')
        return default_flags

def save_to_disk(dataframe, tweet_id, flag_options):
    print('Saving...')
    if flag_options['file_format'] == 'pickle':
        file_name = '../data/raw/replies_to_'+tweet_id+'.pickle'
        dataframe.to_pickle(file_name)
    else:
        file_name = '../data/raw/replies_to_'+tweet_id+'.csv'
        dataframe.to_csv(file_name, index=False)
    print('Saved successfully as '+file_name)

def print_welcome():
    print('--------------')
    print('get_replies.py')
    print('--------------')
    print('Get the replies to a twitter thread.')
    print('Flags enabled: -f, -s, -w, -bq, -sw')
    print('Enter tweet url followed by flag options.')

def main(*args):
    print_welcome()
    try:
        user_input = args[0]
    except:
        print('No args passed to get_replies.py main().')
        user_input = input('Tweet url: ')
    print('Parsing link...')
    tweet_url, flag_list = raw_input_parser(user_input)
    twitter_user, tweet_id = parse_tweet_url(tweet_url)
    flag_dict = flag_parser(flag_list)
    # Specify twitter object fields to keep.
    global tweet_fields_of_interest

    # Setup path to credentials file.
    path = 'credentials.ini'
    try:
        print('Loading credentials')
        api = setup_api_config(path, flag_dict)
    except Exception as e:
        print('Invalid path to credentials.ini. credentials.ini file not found.')
        exit()
    # Retrieve replies from Twitter API
    try:
        print('Retrieving tweets from server...')
        replies = get_replies(
            api=api,
            twitter_user=twitter_user,
            tweet_id=tweet_id,
            flag_options=flag_dict
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
        save_to_disk(df, tweet_id, flag_options=flag_dict)

        # Print summary message to console.
        print(str(df.shape[0])+' rows retrieved.')
        print('Done.')
        return twitter_user, tweet_id, flag_dict
    except tweepy.error.TweepError as e:
        print('API usage rate exceeded.')
        print(str(e))
        print('Failed to collect data.')
        print('Try again in 15 mins.')

if __name__ == '__main__':
    main()
